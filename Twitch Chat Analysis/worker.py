# Goto https://dev.twitch.tv
# Create New Twitch Account
# in Console Create New Application
# Generate Client ID and Client Secret Key

import requests
import json
import traceback
# nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

headers = {
    "Accept": "(Your twitch Client Secret Key)",
    "Client-ID": "(Your Twitch client ID)",
}

params = (("login", "omkar_indulkar"),)
session = requests.Session()


def json_upload(data_list):
    with open("record.json", "a") as fp:
        json.dump(data_list, fp)


def score_check(sentiment_op):
    if sentiment_op["neg"] < 0:
        return "negative"
    elif sentiment_op["pos"] > 0.2:
        return "positive"
    else:
        return "neutral"


def sentiment_check(data):

    sid = SentimentIntensityAnalyzer()

    sentiment_op = score_check(sid.polarity_scores(data["comment"]))

    return sentiment_op


def get_data_dict(resp):
    try:
        count = 0
        for data in resp["comments"]:
            # print("------------------------------------------------------------")
            count += 1
            print(count)
            data_dict = dict()
            data_dict["commenter_name"] = data["commenter"]["name"]
            data_dict["comment"] = data["message"]["body"]
            data_dict["sentiment_result"] = sentiment_check(data_dict)
            yield data_dict
    except Exception as e:
        print("Exception while get data dict", e)
        traceback.print_exc


def get_next_token(resp):
    try:
        next_page = False
        if len(resp.get("_next", "")) > 0:
            next_page = resp["_next"]

        return next_page
    except Exception as e:
        print("Exception while get next token", e)
        traceback.print_exc()
        return False


def start_scraper(video_id):
    response = session.get(
        "https://api.twitch.tv/v5/videos/{}/comments?cursor=".format(video_id),
        headers=headers,
        params=params,
    )
    print(response)
    resp = json.loads(response.content.decode("utf-8-sig"))

    data_dict = get_data_dict(resp)
    for d in data_dict:
        yield d
    next_page = get_next_token(resp)
    count = 1
    while next_page:
        print(
            "------------------------------ Next Page ------------------------------------"
        )
        count += 1
        print(count)
        print(next_page)
        response = session.get(
            "https://api.twitch.tv/v5/videos/{}/comments?cursor=".format(video_id)
            + str(next_page),
            headers=headers,
            params=params,
        )
        print(response)
        resp = json.loads(response.content.decode("utf-8-sig"))
        data_dict = get_data_dict(resp)
        for d in data_dict:
            yield d
        next_page = get_next_token(resp)


