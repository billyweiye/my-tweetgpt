import schedule
import requests
import configparser
import datetime
import time
from tweetgpt import generate_tweet
from tweet import post_tweet 
import logging 

def get_news(topic, date, sort_type, apikey):
    url = f"https://newsapi.org/v2/everything?q={topic}&from={date}&sortBy={sort_type}&apiKey={apikey}&language=en"

    response = requests.get(url)

    return response.json()

# Counter to keep track of job executions
job_execution_count = 0
max_job_executions = 20

def reset_job_counter():
    global job_execution_count
    job_execution_count = 0
    logging.info("Job execution count reset at", datetime.datetime.now())

def main():
    global job_execution_count
    if job_execution_count < max_job_executions:
        #get news list
        kw='Elon Musk'
        sort_type = "relevancy"
        news=get_news(topic=kw, date=date, sort_type=sort_type, apikey=apikey)


        news_title=news.get("articles")[job_execution_count].get("title")
        new_description=news.get("articles")[job_execution_count].get("description")
        news_url=news.get("articles")[job_execution_count].get("url")

        prompts=f"title:{news_title} || description:{new_description}"

        tweets=generate_tweet(openai_api_key,prompts)

        tweets += f" {news_url}"

        logging.info(job_execution_count,'||',tweets)

        post_tweet(auth=auth,text=tweets)

        job_execution_count += 1



def schedule_job():
    # Schedule the job to reset the counter every day at midnight
    schedule.every().day.at("00:00").do(reset_job_counter)

    # Schedule the job to run every 10 to 48 minutes between 8 am and 10 pm
    schedule.every(10).to(25).minutes.do(main)

    while True:
        try:
            now = datetime.datetime.now()
            if now.hour >= 8 and now.hour <= 23:
                logging.info(schedule.idle_seconds())
                schedule.run_pending()
            time.sleep(1)  # Sleep for a second to avoid high CPU usage
        except Exception as e:
            logging.error("An unexpected error occurred: %s", e)
            time.sleep(30)

if __name__ == "__main__":
    # 配置日志输出的格式
    logging.basicConfig(
        filename='app.log', level=logging.INFO,  # 设置日志级别，可选的级别有 DEBUG, INFO, WARNING, ERROR, CRITICAL
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


    config = configparser.ConfigParser()
    # 读取配置文件
    config.read('config.ini')

    apikey=config['news']['api_key']

    openai_api_key=config['openai']["openai_api_key"]

    auth={
            "consumer_key" :config['twitter']["api_key"] ,
            "consumer_secret" :config['twitter']["api_secret"],
            "access_token" :config['twitter']["access_token"] ,
            "access_token_secret" :config['twitter']["token_secret"] ,
    }

    # # 指定目标时区
    # target_timezone = pytz.timezone('America/New_York')

    # # 获取当前时间（无时区信息）
    # current_time = datetime.datetime.now()

    # # 将当前时间设置为目标时区的时间
    # target_time = current_time.astimezone(target_timezone)

    date=(datetime.datetime.now()-datetime.timedelta(1)).strftime("%Y-%m-%d") 


    # if "news" not in st.session_state:
    #     st.session_state.news = "wait for loading"
    
    schedule_job()
    



    

