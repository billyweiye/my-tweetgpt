import schedule
import configparser
import datetime
import pytz
import time
from tweetgpt import generate_tweet
from tweet import post_tweet 
import logging 
from news import get_headlines
import threading

# Counter to keep track of job executions
job_execution_count_initial = 0
max_job_executions = 10
news_posted=[]
# Counter to keep track of job executions
# 创建线程本地存储对象
local_data = threading.local()

# 设置线程本地存储中的全局变量字典
def set_job_execution_count(job_execution_count=0):
    local_data.job_execution_count = job_execution_count
    

# 获取线程本地存储中的全局变量字典
def get_job_execution_count():
    if not hasattr(local_data, 'job_execution_count'):
        local_data.job_execution_count = job_execution_count_initial
    return local_data.job_execution_count

def reset_job_counter():
    set_job_execution_count(job_execution_count=job_execution_count_initial)
    logging.info("Job execution count reset at", datetime.datetime.now())

def main(country,language,timezone):
    global news_posted
    job_execution_count=get_job_execution_count()
    current_time = datetime.datetime.now()
    # 将当前时间设置为目标时区的时间
    target_time = current_time.astimezone(timezone)
    # 限制任务时间 
    if target_time.hour < 8 or target_time.hour > 23:
        return

    if job_execution_count < max_job_executions:
        logging.info(f"TASK: {job_execution_count}")

        #get news list
        # kw='China'
        # sort_type = "relevancy"
        # news=get_news(topic=kw, date=date, sort_type=sort_type, apikey=apikey)

        news=get_headlines(country=country,category='',topic='',apikey=apikey)

        cnt=0
        while True:
            news_title=news.get("articles")[job_execution_count+cnt].get("title")
            if news_title not in news_posted :
                break
            elif cnt>=max_job_executions:
                set_job_execution_count(max_job_executions)
                return
            else:
                cnt+=1
                time.sleep(0.8)

        news_posted.append(news_title)
        news_title=news.get("articles")[job_execution_count+cnt].get("title")
        new_description=news.get("articles")[job_execution_count+cnt].get("description")
        news_url=news.get("articles")[job_execution_count+cnt].get("url")

        prompts=f"title:{news_title} || description:{new_description}"

        tweets=generate_tweet(openai_api_key,prompts,language)

        tweets += f" {news_url}"

        logging.info(f"{job_execution_count}",'||',tweets)

        if tweets:
            post_tweet(auth=auth,text=tweets)

        set_job_execution_count(job_execution_count + 1)



def schedule_job():
    # 创建任务和调度器
    scheduler_cn = schedule.Scheduler()
    scheduler_us = schedule.Scheduler()

    # Schedule the job to reset the counter every day at midnight
    scheduler_cn.every().day.at("00:00").do(reset_job_counter)
    scheduler_us.every().day.at("00:00").do(reset_job_counter)

    # Schedule the job to run every 10 to 48 minutes between 8 am and 10 pm
    scheduler_cn.every(5).to(40).minutes.do(main,country='cn',timezone=cn_timezone,language="Simplified Chinese")
    scheduler_us.every(10).to(30).minutes.do(main,country='us',timezone=us_timezone,language='English')

    # 定义一个函数来运行调度器
    def run_scheduler(scheduler):
        while True:
            try:
                scheduler.run_pending()
                time.sleep(1)  # Sleep for a second to avoid high CPU usage
            except Exception as e:
                logging.error("An unexpected error occurred: %s", e)
                time.sleep(300)

    # 创建两个线程来并行执行任务
    thread_cn = threading.Thread(target=run_scheduler, args=(scheduler_cn,))
    thread_us = threading.Thread(target=run_scheduler, args=(scheduler_us,))
    
    # 启动线程
    thread_cn.start()
    thread_us.start()

    # 等待线程结束
    thread_cn.join()
    thread_us.join()



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

    apikey=config['news']['api_key']

    openai_api_key=config['openai']["openai_api_key"]

    auth={
            "consumer_key" :config['twitter']["api_key"] ,
            "consumer_secret" :config['twitter']["api_secret"],
            "access_token" :config['twitter']["access_token"] ,
            "access_token_secret" :config['twitter']["token_secret"] ,
    }

    # 指定目标时区
    us_timezone = pytz.timezone('America/New_York')

    cn_timezone = pytz.timezone('Asia/Shanghai')


    schedule_job()

    




    

