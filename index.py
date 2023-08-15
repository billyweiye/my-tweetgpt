import streamlit as st
import requests
# import os
import datetime
import pytz
import time
import pandas as pd
import random
from keywords import keywords
from tweetgpt import generate_tweet
from tweet import post_tweet 

def get_news(topic, date, sort_type, apikey):
    url = f"https://newsapi.org/v2/everything?q={topic}&from={date}&sortBy={sort_type}&apiKey={apikey}&language=en"

    response = requests.get(url)

    return response.json()


if __name__ == "__main__":
   # apikey=os.environ.get("news_api_key")
    apikey=st.secrets["news_api_key"]

    openai_api_key=st.secrets["openai_api_key"]

    auth={
            "consumer_key" : st.secrets["api_key"] ,
            "consumer_secret" :st.secrets["api_secret"],
            "access_token" :st.secrets["access_token"] ,
            "access_token_secret" :st.secrets["token_secret"] ,
    }


    sort_type = "relevancy"

    # 指定目标时区
    target_timezone = pytz.timezone('America/New_York')

    # 获取当前时间（无时区信息）
    current_time = datetime.datetime.now()

    # 将当前时间设置为目标时区的时间
    target_time = current_time.astimezone(target_timezone)

    date=(target_time-datetime.timedelta(1)).strftime("%Y-%m-%d") 
    



   # df.to_csv("test.csv",index=False)


    initial_time=datetime.datetime.now()
    count=0

    if "news" not in st.session_state:
        st.session_state.news = "wait for loading"
    
    kw='Elon Musk'
    news=get_news(topic=kw, date=date, sort_type=sort_type, apikey=apikey)

    news_cnt=len(news.get("articles"))

    count=0

    while True:
        if count<10 and count<news_cnt:
           # kw=random.choice(keywords)
           # df=pd.DataFrame(data=news.get("articles"))
           # st.session_state['news'] = df
            news_title=news.get("articles")[count].get("title")
            new_description=news.get("articles")[count].get("description")
            news_url=news.get("articles")[count].get("url")

            prompts=f"title:{news_title} || description:{new_description}"

            tweets=generate_tweet(openai_api_key,prompts)

            tweets += f" {news_url}"

            post_tweet(auth=auth,text=tweets)

            st.session_state['news'] =f"{count}=> {prompts}"


            st.write(st.session_state.news)
            
            count += 1 
            time.sleep(30)
        else :
            break

    

