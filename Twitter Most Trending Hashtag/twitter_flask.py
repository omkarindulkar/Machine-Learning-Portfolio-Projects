# To get Consumer Key and Access Tokens
# go to https://developer.twitter.com/en/apps
# Create App and generate Consumer API keys and Access token & access token secret

import tweepy, json
import tweepy as tw
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, request, render_template, session, redirect
import numpy as np
import io
from io import StringIO, BytesIO
import base64

app = Flask(__name__)

CONSUMER_KEY = '(API key)'
CONSUMER_SECRET = '(API secret key)'
ACCESS_KEY = '(Access token)'
ACCESS_SECRET = '(Access token secret)'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
trends1 = api.trends_place(1)
@app.route('/', methods=("POST", "GET"))
def html_table():
    hashtag=[x['name'] for x in trends1[0]['trends'] if x['name'].find('#') ==0][0]
    search_words = hashtag
    date_since = "2020-09-16"

    new_search = search_words + " -filter:retweets"

    tweets = tw.Cursor(api.search, 
                            q=new_search,
                            lang="en",
                            since=date_since).items(100)
    users_locs = [[tweet.user.screen_name, tweet.user.location, tweet.text] for tweet in tweets]

    df = pd.DataFrame(data=users_locs, 
                        columns=['user', "location",'text'])

                
    df['text_plain'] = df[['text']].astype(str)
    df['text_plain'] = df['text'].str.replace('\d+', '')
    df['text_plain'] = df['text'].str.replace(r'[^\w\s]+', '')
    df['text_plain'] = df['text'].str.replace(r'\^[a-zA-Z]\s+', '')
    df['text_plain'] = df['text'].str.lower()

    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    df['sentiment'] = df['text_plain'].apply(lambda x: sid.polarity_scores(x))
    def convert(x):
        if x < 0:
            return "negative"
        elif x > .2:
            return "positive"
        else:
            return "neutral"
    df['result'] = df['sentiment'].apply(lambda x:convert(x['compound']))
    df3 = df.sort_values('result', ascending=False)
    sns.set_style('darkgrid')
    fig = plt.figure(figsize=(10,6))
    df['result'].value_counts().plot(kind='bar')
    io = BytesIO()
    fig.savefig(io, format='png')
    data = base64.encodebytes(io.getvalue()).decode('utf-8')

    return render_template('index.html', data=data, hashtag=hashtag, tables=[df3.to_html(classes='data')], titles=df3.columns.values)



if __name__ == '__main__':
    app.run(debug=True)