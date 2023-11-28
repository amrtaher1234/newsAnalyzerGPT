import requests
from apscheduler.schedulers.blocking import BlockingScheduler
import json
import os
import openai
from mailjet_rest import Client


# Your API and OpenAI keys
API_KEY = 'API KEY for news api'
openai.api_key = 'opennai-api-key'


def fetch_news():
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': 'openai',
        'apiKey': API_KEY,
        'pageSize': 10,
        'sortBy': 'popularity',
        'language': 'en'
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        news_data = response.json()
        titles = [article['title']+" Description: " +article['description'] for article in news_data['articles']]
        # descriptions = [article['description'] for article in news_data['articles']]
        impact_scores = evaluate_impact(titles)
        # Persisting data to a file
        persist_data(news_data, impact_scores)
    else:
        print(f'Failed to retrieve news: {response.status_code}')

def evaluate_impact(titles):
    impact_scores = []
    for title in titles:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"""You are a stock market expert. You are reading the news and evaluating the impact of the news on the stock market.
                you should produce a score from 0 to 10 that represents how critical this news could be on stock market.
                you will be provided with a title followed by a description of the news.
                - please make sure the output is always number between 0 and 10.
                - please make sure the output is only the number.


                News: {title}
                """
            }]
        )
        print("Title: ", title)
        score = float(response.choices[0].message.content.strip())
        impact_scores.append(score)
    return impact_scores


def send_email(subject, body):
    mailjet = Client(auth=('email auth', 'email auth), version='v3.1')
    email_data = {
        'Messages': [
            {
                "From": {
                    "Email": "algorhym3@gmail.com",
                    "Name": "Mohamed"
                },
                "To": [
                    {
                        "Email": "algorhym3@gmail.com",
                        "Name": "Recipient Name"
                    },
                    {
                        "Email": "amrtaher1995@gmail.com",
                        "Name": "amr"
                    },
                       {
                        "Email": "yar2nman@gmail.com",
                        "Name": "Ahmed"
                    }
                ],
                "Subject": subject,
                "TextPart": body,
            }
        ]
    }
    
    result = mailjet.send.create(data=email_data)
    if result.status_code == 200:
        print(f"Email sent successfully: {result.json()}")
    else:
        print(f"Failed to send email: {result.json()}")


def persist_data(news_data, impact_scores):
    if not os.path.exists('data'):
        os.makedirs('data')
    
    high_impact_news = []
    for article, score in zip(news_data['articles'], impact_scores):
        article['impact_score'] = score
        if score >= 7:
            high_impact_news.append(article)
    
    if high_impact_news:
        subject = "High Impact Tech News Alert"
        body = "\n\n".join(
            f"Title: {article['title']}\n"
            f"Author: {article['author']}\n"
            f"Published At: {article['publishedAt']}\n"
            f"Impact Score: {article['impact_score']}\n"
            f"URL: {article['url']}\n"
            f"Description: {article['description']}"
            for article in high_impact_news
        )
        send_email(subject, body)

    with open(f'data/news_data_{news_data["articles"][0]["publishedAt"]}.json', 'w') as f:
        json.dump(news_data, f)
fetch_news()
scheduler = BlockingScheduler()
scheduler.add_job(fetch_news, 'interval', hours=1)
scheduler.start()
