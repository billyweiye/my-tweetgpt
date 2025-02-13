import schedule
import configparser
import datetime
import pytz
import time
from tweetgpt import generate_tweet
from tweet import post_tweet 
import logging 
from logging.handlers import TimedRotatingFileHandler
import threading
import queue
from feeds import get_rss_urls,get_feeds
import random

# 创建线程本地存储对象
local_data = threading.local()

lock = threading.Lock()
job_execution_count_global=0
# 设置线程本地存储中的全局变量字典
def set_job_execution_count(count=0):
    global job_execution_count_global
    with lock:  # 使用线程锁确保线程安全
        job_execution_count_global =count

    

# 获取线程本地存储中的全局变量字典
def get_job_execution_count():
    global job_execution_count_global
    return job_execution_count_global

def reset_job_counter(timezone='America/New_York'):
    try:
        time_zone=pytz.timezone(timezone)
        def reset_job():
            set_job_execution_count(0)
            logger.info(f"Job execution count reset at {datetime.datetime.now()} || Current Job Count is {get_job_execution_count()}")

        #创建定时任务来重置发推次数上限
        scheduler = schedule.Scheduler()
        scheduler.every().day.at("00:00",time_zone).do(reset_job)
        logger.info(f"{threading.current_thread()}: started reset job count schedule")
        while True:
            # next_zero_time = datetime.datetime.now().astimezone(time_zone).replace(hour=0, minute=0, second=0, microsecond=0)
            # next_zero_time = next_zero_time + datetime.timedelta(days=1)
            # current_time = datetime.datetime.now(time_zone)
            # wait_time=(next_zero_time-current_time).seconds
            scheduler.run_pending()
            time.sleep(0.5)
    except Exception as e:
        logger.error(f"Error occured in {threading.current_thread()}: {e}")


    

# 获取及储存线程本地存储中的已发布的feeds
def get_posted_news():
    if not hasattr(local_data, 'posted_news'):
        local_data.posted_news = []
    return local_data.posted_news

def save_posted_news(news_id):
    local_data.posted_news.append(news_id) 


news_list=[]
my_queue = queue.LifoQueue()  # 使用LIFO队列 
def put_unique_message(queue_obj, message):
    # 检查队列中是否已经存在相同的消息
    if message not in news_list:
        news_list.append(message)
        queue_obj.put(message)
        logger.info(f"Inserted unique message: {message}")
    #else:
     #   logger.info(f"Message already exists in the queue: {message}")

def news_queue(mins_interval:int =1,catogery:list = [],publish_time:int=60):
    while True:
        try:
            urls=get_rss_urls("Feeds.opml",catogery)
            news=get_feeds(urls,publish_time)
            for feed in news:
                put_unique_message(my_queue,feed)
            logger.info(f"The Current Queue Size: {len(my_queue.queue)}")
            time.sleep(mins_interval*60)
        except Exception as e:
            logger.error(f"Error occured in {threading.current_thread()}: {e}")


def get_feed_queue():
    return my_queue.get()


def post_interval(current_time):
    if current_time.hour >= 9 and current_time.hour < 14:
        min_tweet_interval=16
        max_tweet_interval=20
    elif current_time.hour >= 19 and current_time.hour < 22:
        min_tweet_interval=30
        max_tweet_interval=40
    elif (current_time-datetime.datetime(current_time.year,current_time.month,current_time.day,9,0,0,tzinfo=current_time.tzinfo)).seconds<=190*60 or (current_time-datetime.datetime(current_time.year,current_time.month,current_time.day,19,0,0,tzinfo=current_time.tzinfo)).seconds<=190*60:
        min_tweet_interval=min([(current_time-datetime.datetime(current_time.year,current_time.month,current_time.day,9,0,0,tzinfo=current_time.tzinfo)).seconds/60,(current_time-datetime.datetime(current_time.year,current_time.month,current_time.day,19,0,0,tzinfo=current_time.tzinfo)).seconds/60])
        max_tweet_interval=min([(current_time-datetime.datetime(current_time.year,current_time.month,current_time.day,9,0,0,tzinfo=current_time.tzinfo)).seconds/60,(current_time-datetime.datetime(current_time.year,current_time.month,current_time.day,19,0,0,tzinfo=current_time.tzinfo)).seconds/60])
    else:
        min_tweet_interval=190*2
        max_tweet_interval=200*2
    return (min_tweet_interval,max_tweet_interval)


def tweet_job(sys_prompt,timezone):
    time_zone=pytz.timezone(timezone)
    while True:
        try:
            job_execution_count=get_job_execution_count()

            current_time = datetime.datetime.now()
            # 将当前时间设置为目标时区的时间
            target_time = current_time.astimezone(time_zone)
            # 限制任务时间 
         #   if target_time.hour < 7 and target_time.hour > 2:
         #       logger.warning("Not Scheduled time. Wait another 10 mins.")
         #       time.sleep(10*60)   #等待10分钟
         #       continue

            if job_execution_count < max_job_executions:
                logger.info(f"TASK: {job_execution_count}")

                news=get_feed_queue()
                news_id=news.get("id")
                if news_id in get_posted_news() :
                    logger.info("No New Source Found")
                    time.sleep(1) 
                    continue

                save_posted_news(news_id)
                news_title=news.get("title")
                new_description=news.get("description")
                news_url=news.get("link")
                news_content=news.get("content")
                logger.info(f"New Source Found: {news_id}")

                #调用GPT 生成content
                if 'youtube' not in news_url:
                    prompts=f"""title:{news_title} \
                          description:{new_description} \ 
                          content: {news_content} \ 
                          """
                    logger.info(f"Prompts:{prompts}")
                    tweets=generate_tweet(openai_api_key,prompts,sys_prompt)
                    
                    #加上news link
                    tweets = f"{news_url} " + tweets
                else:  #youtube content  post directly
                    tweets = f"{new_description} {news_url}"

                logger.info(f"TASK: {job_execution_count} || {tweets}")

                if tweets:
                    post_result=post_tweet(auth=auth,text=tweets)
                    logger.info("Response mesg: {} {}".format(post_result.status_code,post_result.text))
                    if post_result.status_code == 429: #too many requests
                        logger.warning("TOO MANY REQUESTS. WAIT!!")
                        time.sleep(3*60*60) #wait for 3 hours to continue if the api has reached the limit
                        continue
                    elif post_result.status_code != 201:
                        raise Exception(
                            "Request returned an error: {} {}".format(post_result.status_code, post_result.text)
                        )

                set_job_execution_count(job_execution_count + 1)

                min_interval=post_interval(target_time)[0]
                max_interval=post_interval(target_time)[1]
                sleep_seconds=random.randint(min_interval*60,max_interval*60)
                next_post_time=datetime.datetime.now()+datetime.timedelta(seconds=sleep_seconds)
                logger.info(f"Next Post Time: {next_post_time.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(sleep_seconds)
            else:
                logger.warning(f"JOB COUNTS: {job_execution_count} EXCEEDED THE MAX JOB COUNT!!")
                time.sleep(30*60)
        except Exception as e:
            logger.error(f"Error occured in {threading.current_thread()}: {e}")
            time.sleep(30*60)



def schedule_job(news_req_interval:int=1,category:list=[],publish_time:int=60,sys_prompt:str="",timezone='America/New_York'):
    #创建获取feeds线程
    thread_rss=threading.Thread(target=news_queue,args=(news_req_interval,category,publish_time,),name="RSS")

    # 创建线程来并行执行任务
    thread_tweet = threading.Thread(target=tweet_job,args=(sys_prompt,timezone,), name="TWEET")
    
    #创建重置任务计数线程
    thread_counter = threading.Thread(target=reset_job_counter,args=(timezone,), name="JOB_COUNTER")
    
    # 启动线程
    thread_rss.start()
    thread_tweet.start()
    thread_counter.start()
    

    # 等待线程结束
    thread_rss.join()
    thread_tweet.join()
    thread_counter.join()





if __name__ == "__main__":
    # 配置日志记录器
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # 创建 TimedRotatingFileHandler，每 6 小时滚动一次日志文件
    log_handler = TimedRotatingFileHandler('app.log', when='H', interval=6, backupCount=4)
    log_handler.setLevel(logging.DEBUG)


    # 配置日志格式
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(log_formatter)

    # 添加处理器到记录器
    logger.addHandler(log_handler)


    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')

    openai_api_key=config['openai']["openai_api_key"]

    auth={
            "consumer_key" :config['twitter']["api_key"] ,
            "consumer_secret" :config['twitter']["api_secret"],
            "access_token" :config['twitter']["access_token"] ,
            "access_token_secret" :config['twitter']["token_secret"] ,
    }

    # Counter to keep track of job executions
    max_job_executions = 17

    news_req_interval=1  #每1分钟检查一次rss
    publish_time_limt=60

    # 指定目标时区\语言\主题
    us_timezone = config['general']["TIMEZONE"]
    sys_prompt=config['system prompt']["PROMPT"]
    rss_category= config['general']["TOPICS"].replace(' ','').split(',') 
    

    schedule_job(news_req_interval,rss_category,publish_time_limt,sys_prompt,us_timezone)

    




    

