import requests

def get_headlines(country,category,topic,apikey):
    #top headline endpoint
    url=f"https://newsapi.org/v2/top-headlines?country={country}&category={category}&q={topic}&apiKey={apikey}"

    response = requests.get(url)

    return response.json()

def get_news(topic, date, sort_type, apikey):
    #everything endpoint
    url = f"https://newsapi.org/v2/everything?q={topic}&from={date}&sortBy={sort_type}&apiKey={apikey}&language=en"

    response = requests.get(url)

    return response.json()
