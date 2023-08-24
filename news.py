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





def nyt_newswire(apikey,source='all',sector='all',limit=20):
  requestUrl = f"https://api.nytimes.com/svc/news/v3/content/{source}/{sector}.json?limit={limit}&api-key={apikey}"
  requestHeaders = {
    "Accept": "application/json"
  }

  response = requests.get(requestUrl, headers=requestHeaders)

  keys_to_get=['abstract','title','url']
  result=[] 
  for i in response.json().get('results'):
    result.append({key: i[key] for key in keys_to_get if key in i})

  return result

def newsdata(apikey,timeframe,language,q="Politics OR Finance OR Stock Market"):
  url = f"https://newsdata.io/api/1/news?apikey={apikey}&timeframe={timeframe}&language={language}&q={q}"
  def get_next_page(url,page):
    url+=f"&page={page}"
    res = requests.get(url, headers=headers, data=payload)
    return res

  payload = {}
  headers =  {
    "Accept": "application/json"
  }

  response = requests.get(url, headers=headers, data=payload)

  cnt_result=response.json().get("totalResults")//10 +1 if response.json().get("totalResults")%10 !=0 else response.json().get("totalResults")//10
  next_page=response.json().get("nextPage")
  all_pages=[]
  all_pages.append(response.json().get('results'))
  for page in range(cnt_result): 
     next_page_result=get_next_page(url,next_page).json()
     all_pages.append(next_page_result.get('results'))
     next_page=next_page_result.get('nextPage')

  keys_to_get=['description','title','link']
  result=[] 
  for page in all_pages:
    for i in page:
      result.append({key: i[key] for key in keys_to_get if key in i})

  return result




sector={
  "status": "OK",
  "copyright": "Copyright (c) 2023 The New York Times Company.  All Rights Reserved.",
  "num_results": 50,
  "results": [
    {
      "section": "admin",
      "display_name": "Admin"
    },
    {
      "section": "arts",
      "display_name": "Arts"
    },
    {
      "section": "automobiles",
      "display_name": "Automobiles"
    },
    {
      "section": "books",
      "display_name": "Books"
    },
    {
      "section": "briefing",
      "display_name": "Briefing"
    },
    {
      "section": "business",
      "display_name": "Business"
    },
    {
      "section": "climate",
      "display_name": "Climate"
    },
    {
      "section": "corrections",
      "display_name": "Corrections"
    },
    {
      "section": "education",
      "display_name": "Education"
    },
    {
      "section": "en español",
      "display_name": "En español"
    },
    {
      "section": "fashion",
      "display_name": "Fashion"
    },
    {
      "section": "food",
      "display_name": "Food"
    },
    {
      "section": "gameplay",
      "display_name": "Gameplay"
    },
    {
      "section": "guide",
      "display_name": "Guide"
    },
    {
      "section": "health",
      "display_name": "Health"
    },
    {
      "section": "home & garden",
      "display_name": "Home & Garden"
    },
    {
      "section": "home page",
      "display_name": "Home Page"
    },
    {
      "section": "job market",
      "display_name": "Job Market"
    },
    {
      "section": "the learning network",
      "display_name": "The Learning Network"
    },
    {
      "section": "lens",
      "display_name": "Lens"
    },
    {
      "section": "magazine",
      "display_name": "Magazine"
    },
    {
      "section": "movies",
      "display_name": "Movies"
    },
    {
      "section": "multimedia/photos",
      "display_name": "Multimedia/Photos"
    },
    {
      "section": "new york",
      "display_name": "New York"
    },
    {
      "section": "obituaries",
      "display_name": "Obituaries"
    },
    {
      "section": "opinion",
      "display_name": "Opinion"
    },
    {
      "section": "parenting",
      "display_name": "Parenting"
    },
    {
      "section": "podcasts",
      "display_name": "Podcasts"
    },
    {
      "section": "reader center",
      "display_name": "Reader Center"
    },
    {
      "section": "real estate",
      "display_name": "Real Estate"
    },
    {
      "section": "smarter living",
      "display_name": "Smarter Living"
    },
    {
      "section": "science",
      "display_name": "Science"
    },
    {
      "section": "sports",
      "display_name": "Sports"
    },
    {
      "section": "style",
      "display_name": "Style"
    },
    {
      "section": "sunday review",
      "display_name": "Sunday Review"
    },
    {
      "section": "t brand",
      "display_name": "T Brand"
    },
    {
      "section": "t magazine",
      "display_name": "T Magazine"
    },
    {
      "section": "technology",
      "display_name": "Technology"
    },
    {
      "section": "theater",
      "display_name": "Theater"
    },
    {
      "section": "times insider",
      "display_name": "Times Insider"
    },
    {
      "section": "today’s paper",
      "display_name": "Today’s Paper"
    },
    {
      "section": "travel",
      "display_name": "Travel"
    },
    {
      "section": "u.s.",
      "display_name": "U.S."
    },
    {
      "section": "universal",
      "display_name": "Universal"
    },
    {
      "section": "the upshot",
      "display_name": "The Upshot"
    },
    {
      "section": "video",
      "display_name": "Video"
    },
    {
      "section": "the weekly",
      "display_name": "The Weekly"
    },
    {
      "section": "well",
      "display_name": "Well"
    },
    {
      "section": "world",
      "display_name": "World"
    },
    {
      "section": "your money",
      "display_name": "Your Money"
    }
  ]
}