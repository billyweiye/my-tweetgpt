import openai



def generate_tweet(api_key,prompt,language):
    openai.api_key =api_key
    system_text=f"""Imagine you are a sarcastic commentator!. \
        I will provide you with the latest news title and a brief description \
        and you will write a short opinion piece that provides insightful commentary on the topic at hand.\
        Your comment on this news should be sarcastic and humorous. \
        Perform the following tasks:
        1 - make the comment on the news i sent to you. 
        2 - generate 5 hashtags that could attract more views on twitter, each hashtag should be short but common.
        Remember, keep the total comment under 140 characters. \
        Your reply should start with comment content directly and end with hashtags.
        The language you use to reply is {language}."""
        
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    temperature=1.1,
    max_tokens=250,
    messages=[
        {"role": "system", "content": system_text},
        {"role": "user", "content": prompt}
    ]
    )

    return completion.choices[0].message.content
