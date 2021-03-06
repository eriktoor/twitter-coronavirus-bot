from credentials import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, ACCOUNT_ID, ACCOUNT_NAME
import tweepy 
from tweepy import Stream 
from tweepy.streaming import StreamListener
import json 

import time
from decodeTweet import decodeTweet
from getCovidInfo import getCovidInfo
from logger import *

from utils import nameToCountryCode, countryCodeToName


def respondToTweet(tweet_text, tweeted_by, tweeted_at, tweet_id): 

    #Step 1: Decode the Tweet to find the Critical Words
    decode_info = decodeTweet(tweet_text)

    country, city, state, travel = decode_info

    if len(country) > 2: 
        country = country if not nameToCountryCode(country) else nameToCountryCode(country) 

    #Step 2: Call trackcorona.live api to get information and put it in tweet form 
    tweet = getCovidInfo(decode_info)

    #Step 3: Tweet Back Information 
    if not country and not city and not travel:
        if "symptom" in tweet_text.lower(): 
            tweet = "The symptoms of Coronavirus include fever, cough, and shortness of breath. If you think you have #COVID19 or begin to develop symptoms get tested and go to cdc.gov/COVID-19."
        elif "test" in tweet_text.lower() or "tested" in tweet_text.lower(): 
            tweet = "Learn more about getting tested for #COVID19 at https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/testing.html."
        elif "safe" in tweet_text.lower() or "protect" in tweet_text.lower(): 
            tweet = "Protect yourself by following #CDC #socialdistancing guidelines and oblige with stay at home orders."
        if "what is covid" in tweet_text.lower() or "what is coronavirus" in tweet_text.lower():
            tweet = 'COVID is a large family of viruses transmitting between animals and people that cause illness ranging from the common cold to severe acute respiratory syndrome (SARS). Learn more @CDCgov #COVID #CDC'

    #Step 4: Post the Response 
    postResponse(tweet, tweet_id)





class StdOutListener(StreamListener): 
    def on_data(self, data): 
        # print(data)
        clean_data = json.loads(data)

        user_mentions, tweeter_id_str = clean_data["entities"]["user_mentions"], clean_data["id_str"]
        tweeted_by, tweeted_at = clean_data["user"]["screen_name"], clean_data["in_reply_to_screen_name"]
        tweet, tweet_id = clean_data["text"], clean_data["id"]

        tweet_url = "https://twitter.com/{0}/status/{1}".format(str(tweeted_by), str(tweet_id))

        logging.info("====================================================")
        logging.info("Tweet by= " + str(tweeted_by))
        logging.info("Tweet at= " + str(tweeted_at))
        logging.info("Tweet= " + str(tweet))
        logging.info("Tweet URL= " + str(tweet_url))
        logging.info(clean_data)
        logging.info("====================================================")


        if user_mentions[0]["screen_name"] == ACCOUNT_NAME or user_mentions[0]["screen_name"] == ACCOUNT_NAME.lower():
            print("Responding to tweet..." + tweet_url)
            respondToTweet(tweet, tweeted_by, tweeted_at, tweet_id)
        elif tweeted_by != ACCOUNT_NAME and ACCOUNT_NAME in tweet: 
            print("Responding to tweet..." + tweet_url)
            respondToTweet(tweet, tweeted_by, tweeted_at, tweet_id)

        return True 

    def on_error(self, status): 
        print("IN ERROR")
        print(status)


def setUpAuth():
    # authentication of consumer key and secret 
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET) 
    # authentication of access token and secret 
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET) 
    api = tweepy.API(auth) 
    return api, auth


def postResponse(tweet, tweetId): 
    logging.info("Tweeting tweet=" + str(tweet) + " TweetNo=" + str(tweetId))

    api, auth = setUpAuth()
    api.update_status(tweet, in_reply_to_status_id = tweetId, auto_populate_reply_metadata=True)
    #tweetId = tweet['results'][0]['id']
    # api.update_status('@<username> My status update', tweetId)


def followStream():
    api, auth = setUpAuth()
    listener = StdOutListener()

    stream = Stream(auth, listener)
    stream.filter(track=["CovidAsk"]) #filter=[ACCOUNT_ID]
    # publishTweet(tweet)


def dailyUpdates(countries): 
    """
    Currently not using, could be used to send out daily updates on a schedule. 
    If interested in this consider multithreading this as a second thread. 
    """
    for country in countries: 
        #Step 1: Call trackcorona.live api to get information and put it in tweet form 
        response = getCovidInfo((country, "", "", False))
        #Step 2: Tweet Back Information 
        publishTweet("Daily Update --" + response)


def publishTweet(tweet):
    api, auth = setUpAuth()
    # update the status 
    api.update_status(status = tweet) 


if __name__ == "__main__":

    try: 
        followStream()
    except Exception:
        time.sleep(10)
        logging.exception("Fatal exception. Consult logs.")
        followStream()
    finally: 
        time.sleep(10)
        logging.exception("IN FINALLY")
        print("IN FINALLY")
        followStream()

