import schedule
import configparser
import datetime
import pytz
import time
from tweetgpt import generate_tweet
from tweet import post_tweet 
import logging 
from news import newsdata
import threading
import queue
from feeds import get_rss_urls,get_feeds
import random

# 创建线程本地存储对象
local_data = threading.local()
# 设置线程本地存储中的全局变量字典
def set_job_execution_count(job_execution_count=0):
    local_data.job_execution_count = job_execution_count
    

# 获取线程本地存储中的全局变量字典
def get_job_execution_count():
    if not hasattr(local_data, 'job_execution_count'):
        local_data.job_execution_count = 0
    return local_data.job_execution_count

def reset_job_counter():
    set_job_execution_count(job_execution_count=0)
    logging.info(f"Job execution count reset at {datetime.datetime.now()}")


    

# 获取及储存线程本地存储中的已发布的feeds
def get_posted_news():
    if not hasattr(local_data, 'posted_news'):
        local_data.posted_news = []
    return local_data.posted_news

def save_posted_news(news_id):
    local_data.posted_news.append(news_id) 



my_queue = queue.Queue()  # 使用优先级队列
def put_unique_message(queue_obj, message):
    # 检查队列中是否已经存在相同的消息
    if message not in queue_obj.queue:
        queue_obj.put(message)
        logging.info(f"Inserted unique message: {message}")
    else:
        logging.info(f"Message already exists in the queue: {message}")

def news_queue(mins_interval:int =1,catogery:list = [],publish_time:int=60):
    while True:
        try:
            urls=get_rss_urls("Feeds.opml",catogery)
            news=get_feeds(urls,publish_time)
            for feed in news:
                put_unique_message(my_queue,feed)
            logging.info(f"The Current Queue Size: {len(my_queue.queue)}")
            time.sleep(mins_interval*60)
        except Exception as e:
            logging.error(f"Error occured in {threading.current_thread()}: {e}")


def get_feed_queue():
    return my_queue.get()



def tweet_job(min_tweet_interval,max_tweet_interval,language,timezone):
    while True:
        try:
            job_execution_count=get_job_execution_count()

            current_time = datetime.datetime.now()
            # 将当前时间设置为目标时区的时间
            target_time = current_time.astimezone(timezone)
            # 限制任务时间 
            if target_time.hour < 7 or target_time.hour > 23:
                logging.info("Not Scheduled time. Wait another 10 mins.")
                time.wait(10*60)   #等待10分钟
                continue

            if job_execution_count < max_job_executions:
                logging.info(f"TASK: {job_execution_count}")

                news=get_feed_queue()
                news_id=news.get("id")
                if news_id in get_posted_news() :
                    time.sleep(1) 
                    continue

                save_posted_news(news_id)
                news_title=news.get("title")
                new_description=news.get("description")
                news_url=news.get("link")

                #调用GPT 生成content
                if 'youtube' not in news_url:
                    prompts=f"title:{news_title} || description:{new_description}"
                    logging.info(f"Prompts:{prompts}")
                    tweets=generate_tweet(openai_api_key,prompts,language)
                    
                    #加上news link
                    tweets += f" {news_url}"
                else:  #youtube content  post directly
                    tweets = f"{new_description} {news_url}"

                logging.info(f"TASK: {job_execution_count} || {tweets}")

                if tweets:
                    post_tweet(auth=auth,text=tweets)

                set_job_execution_count(job_execution_count + 1)

                
                time.sleep(random.randint(min_tweet_interval*60,max_tweet_interval*60))
            else:
                time.sleep(30*60)
        except Exception as e:
            logging.error(f"Error occured in {threading.current_thread()}: {e}")



def schedule_job(news_req_interval:int=1,category:list=[],publish_time:int=60,min_tweet_interval:int=1,max_tweet_interval:int=10,language_to_tweet:str="English",timezone=pytz.timezone('America/New_York')):
    #创建获取feeds线程
    thread_rss=threading.Thread(target=news_queue,args=(news_req_interval,category,publish_time),name="RSS")

    # 创建两个线程来并行执行任务
    thread_tweet = threading.Thread(target=tweet_job,args=(min_tweet_interval,max_tweet_interval,language_to_tweet,us_timezone), name="TWEET")
    
    # 启动线程
    thread_rss.start()
    thread_tweet.start()
    

    # 等待线程结束
    thread_rss.join()
    thread_tweet.join()

    #创建定时任务来重置发推次数上限
    scheduler = schedule.Scheduler()
    scheduler.every().day.at("00:00",us_timezone).do(reset_job_counter)



if __name__ == "__main__":
    # 配置日志输出的格式
    logging.basicConfig(
        filename='app.log', level=logging.INFO,  # 设置日志级别，可选的级别有 DEBUG, INFO, WARNING, ERROR, CRITICAL
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

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
    max_job_executions = 45

    # 指定目标时区
    us_timezone = pytz.timezone('America/New_York')

    cn_timezone = pytz.timezone('Asia/Shanghai')

    new_category=["Tech"]
    news_req_interval=1  #每1分钟检查一次rss
    publish_time_limt=60
    min_tweet_interval=1.5 
    max_tweet_interval=5
    language_to_tweet="English"
    rss_category=["Tech","News"]


    schedule_job(news_req_interval,rss_category,publish_time_limt,min_tweet_interval,max_tweet_interval,language_to_tweet,us_timezone)

    




    

