# importing the module 
import tweepy 
from tweepy import Stream 
from tweepy.streaming import StreamListener
import json 

from decodeTweet import decodeTweet
from getCovidInfo import getCovidInfo
from logger import *

from utils import nameToCountryCode, countryCodeToName
from globals import api_key, api_secret, access_token, access_token_secret, account_id, account_name


def dailyUpdates(countries): 

    for country in countries: 
        #Step 1: Call trackcorona.live api to get information and put it in tweet form 
        response = getCovidInfo(country, "", False)
        #Step 2: Tweet Back Information 
        publishTweet("Daily Update --" + response)



def respondToTweet(tweet_text, tweeted_by, tweeted_at, tweet_id): 

    #Step 1: Decode the Tweet to find the Critical Words
    country, city, travel = decodeTweet(tweet_text)

    if len(country) > 2: 
        country = country if not nameToCountryCode(country) else nameToCountryCode(country) 


    #Step 2: Call trackcorona.live api to get information and put it in tweet form 
    tweet = getCovidInfo(country, city, travel)

    #Step 3: Tweet Back Information 
    if not country and not city and not travel:
        if "symptom" in tweet_text.lower(): 
            tweet = "The symptoms of Coronavirus include fever, cough, and shortness of breath. If you think you have #COVID19 or begin to develop symptoms get tested and go to cdc.gov/COVID-19."
        elif "test" in tweet_text.lower(): 
            tweet = "Learn more about getting tested for #COVID19 at https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/testing.html."
        elif "safe" in tweet_text.lower() or "protect" in tweet_text.lower(): 
            tweet = "Protect yourself by following #CDC #socialdistancing guidelines and oblige with stay at home orders."
    
    postResponse(tweet, tweet_id)





class StdOutListener(StreamListener): 
    def on_data(self, data): 
        # print(data)
        clean_data = json.loads(data)

        user_mentions = clean_data["entities"]["user_mentions"]
        tweeter_id_str = clean_data["id_str"]
        tweeted_by, tweeted_at = clean_data["user"]["screen_name"], clean_data["in_reply_to_screen_name"]
        tweet, tweet_id = clean_data["text"], clean_data["id"]

        logging.info("====================================================")
        logging.info("Tweet by= " + str(tweeted_by))
        logging.info("Tweet at= " + str(tweeted_at))
        logging.info("Tweet= " + str(tweet))
        logging.info(clean_data)
        logging.info("====================================================")

        tweet_url = "https://twitter.com/{0}/status/{1}".format(str(tweeted_by), str(tweet_id))

        if user_mentions[0]["screen_name"] == account_name or user_mentions[0]["screen_name"] == account_name.lower():
            print("Responding to tweet..." + tweet_url)
            respondToTweet(tweet, tweeted_by, tweeted_at, tweet_id)
        elif tweeted_by != account_name and account_name in tweet: 
            print("Responding to tweet..." + tweet_url)
            respondToTweet(tweet, tweeted_by, tweeted_at, tweet_id)

        return True 
    def on_error(self, status): 
        print("IN ERROR")
        print(status)


def setUpAuth():
    # authentication of consumer key and secret 
    auth = tweepy.OAuthHandler(api_key, api_secret) 
    # authentication of access token and secret 
    auth.set_access_token(access_token, access_token_secret) 
    api = tweepy.API(auth) 
    return api, auth


def publishTweet(tweet):
    api, auth = setUpAuth()
    # update the status 
    api.update_status(status = tweet) 


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
    stream.filter(track=["CovidAsk"]) #filter=[account_id]
    # publishTweet(tweet)

if __name__ == "__main__":
    tweet = "Hello world..!"
    followStream()
