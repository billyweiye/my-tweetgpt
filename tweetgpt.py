import openai



def generate_tweet(api_key,prompt):
    openai.api_key =api_key
    system_text="I want you to act as a commentariat. I will provide you with the latest news title and a brief description and you will write a very short opinion piece that provides insightful commentary on the topic at hand. Your comment on this news should be funny and sarcastic and sharp. Make sure your comment is less than 140 characters and the only thing you reply is your comments."

    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    max_tokens=250,
    messages=[
        {"role": "system", "content": system_text},
        {"role": "user", "content": prompt}
    ]
    )

    return completion.choices[0].message.content
