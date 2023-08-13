import streamlit as st
import requests
import os
import datetime
import time
import pandas as pd


def get_news(topic, date, sort_type, apikey):
    url = f"https://newsapi.org/v2/everything?q={topic}&from={date}&sortBy={sort_type}&apiKey={apikey}"

    response = requests.get(url)

    return response.json()


if __name__ == "__main__":
   # apikey=os.environ.get("news_api_key")
    apikey='d4bb6970165d44f8b5d52c52b9ca4c2a'
    topic = ["Tesla","Microsoft"]
    sort_type = "popularity"
    date=(datetime.date.today()-datetime.timedelta(1)).strftime("%Y-%m-%d") 



   # df.to_csv("test.csv",index=False)


    initial_time=datetime.datetime.now()
    count=0
    tp=0

    if "news" not in st.session_state:
        st.session_state.news = "wait for loading"


    while True:
        if count<10:
            news=get_news(topic=topic[tp], date=date, sort_type=sort_type, apikey=apikey)
            df=pd.DataFrame(data=news.get("articles"))
            st.session_state['news'] = df

            st.write(st.session_state.news)

            tp=0 if tp!=0 else 1 
            count += 1 
            time.sleep(30)
        else :
            break

    

