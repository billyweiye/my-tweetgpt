from requests_oauthlib import OAuth1Session
import json


# apikey=st.secrets["news_api_key"]
# consumer_key = st.secrets["api_key"] 
# consumer_secret = os.environ.get("api_secret")
# access_token = os.environ.get("access_token")
# access_token_secret = os.environ.get("token_secret")



def post_tweet(auth={},text=""):
    
    consumer_key =auth.get("consumer_key")
    consumer_secret =auth.get("consumer_secret")
    access_token =auth.get("access_token")
    access_token_secret = auth.get("access_token_secret")

    # Be sure to add replace the text of the with the text you wish to Tweet. You can also add parameters to post polls, quote Tweets, Tweet with reply settings, and Tweet to Super Followers in addition to other features.
    payload = {
        "text": text,
        # "direct_message_deep_link":link,
    }


    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    # Making the request
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        if response.status_code == 429: #too many requests
            return "Too many requests"
        else:
            raise Exception(
                "Request returned an error: {} {}".format(response.status_code, response.text)
            )
    else:
        return "Success"

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))






