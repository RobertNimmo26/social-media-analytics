import asyncio
import json
import time

import tweepy
from decouple import config
from pymongo import MongoClient, errors

from newsworthyness_tweets import newsworthiness_tweet
from process_tweets import tweet_processor_rest, tweet_processor_streamer
from downloader_tweets import downloader

# Keys of the app
CONSUMER_KEY = config("CONSUMER_KEY")
CONSUMER_SECRET = config("CONSUMER_SECRET")
ACCESS_TOKEN = config("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = config("ACCESS_TOKEN_SECRET")

# Download media objects
DOWNLOAD = False

# Runtime
RUNTIME = time.time() + 60 * 1
# 60  # 60 * 18

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
if (not api):
    print('Can\'t authenticate')
    print('failed cosumeer id ----------: ', CONSUMER_KEY)

# this is to setup local Mongodb
client = MongoClient('127.0.0.1', 27017)  # is assigned local port
dbName = "TwitterDB"  # set-up a MongoDatabase
db = client[dbName]
collName_streamer = 'hybrid_streamer'  # here we create a collection
collName_rest = 'hybrid_rest'  # here we create a collection

# This is for the Collection  put in the DB
collection_streamer = db[collName_streamer]
# This is for the Collection  put in the DB
collection_rest = db[collName_rest]


stats = {
    "total": 0,
    "streamer_total": 0,
    "rest_total": 0,
    "no_retweets": 0,
    "no_quotes": 0,
    "no_images": 0,
    "no_video": 0,
    "no_verified": 0,
    "no_geotagged": 0,
    "no_coordinates": 0,
    "no_location_place": 0
}


async def rest_process_tweets(data):

    # Checks if tweet has a newsworthiness score of > 70%
    # if newsworthiness_tweet(data, "rest"):
    tweet = tweet_processor_rest(data)
    try:
        collection_rest.insert_one(tweet)
    except errors.DuplicateKeyError:
        return

    stats["total"] += 1

    stats["rest_total"] += 1

    if tweet["RT"]:
        stats["no_retweets"] += 1
    if tweet["quote"]:
        stats["no_quotes"] += 1
    if tweet["no_images"] > 0:
        stats["no_images"] += tweet["no_images"]
    if tweet["no_videos"] > 0:
        stats["no_videos"] += tweet["no_videos"]
    if tweet["verified"]:
        stats["no_verified"] += 1
    if tweet["geoenabled"]:
        stats["no_geotagged"] += 1
    if tweet["coordinates"] is not None:
        stats["no_coordinates"] += 1
    if tweet["place"] != False:
        stats["no_location_place"] += 1

    if DOWNLOAD:
        if tweet["media_urls"]:
            downloader(tweet["media_urls"])


class StreamListener(tweepy.StreamListener):
  # This is a class provided by tweepy to access the Twitter Streaming API.

    global geoEnabled
    global geoDisabled

    def on_connect(self):
        # Called initially to connect to the Streaming API
        print("You are now connected to the streaming API.")

    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code
        print('An Error has occured: ' + repr(status_code))
        return False

    def on_data(self, data):
        t = json.loads(data)

        # Checks if tweet has a newsworthiness score of > 70%
        if newsworthiness_tweet(t, "streamer"):
            tweet = tweet_processor_streamer(t)

            collection_streamer.insert_one(tweet)

            stats["total"] += 1
            stats["streamer_total"] += 1

            if tweet["RT"]:
                stats["no_retweets"] += 1
            if tweet["quote"]:
                stats["no_quotes"] += 1
            if tweet["no_images"] > 0:
                stats["no_images"] += tweet["no_images"]
            if tweet["no_videos"] > 0:
                stats["no_videos"] += tweet["no_videos"]
            if tweet["verified"]:
                stats["no_verified"] += 1
            if tweet["geoenabled"]:
                stats["no_geotagged"] += 1
            if tweet["coordinates"] is not None:
                stats["no_coordinates"] += 1
            if tweet["place"] != False:
                stats["no_location_place"] += 1

            if DOWNLOAD:
                if tweet["media_urls"]:
                    downloader(tweet["media_urls"])


if __name__ == '__main__':

    Loc_UK = [-10.392627, 49.681847, 1.055039, 61.122019]  # UK and Ireland
    Words_UK = ["Boris", "Prime Minister", "Tories", "UK", "London", "England", "Manchester", "Sheffield", "York", "Southampton",
                "Wales", "Cardiff", "Swansea", "Banff", "Bristol", "Oxford", "Birmingham", "Scotland", "Glasgow", "Edinburgh", "Dundee", "Aberdeen", "Highlands"
                "Inverness", "Perth", "St Andrews", "Dumfries", "Ayr"
                "Ireland", "Dublin", "Cork", "Limerick", "Galway", "Belfast", " Derry", "Armagh"
                "BoJo", "Labour", "Liberal Democrats", "SNP", "Conservatives", "First Minister", "Nicola Sturgeon", "Surgeon", "Chancelor"
                "Boris Johnson", "Keir Stramer"]

    print(f"Tracking: {str(Words_UK)}")

    # Set up the listener. The 'wait_on_rate_limit=True' is needed to help with Twitter API rate limiting.
    listener = StreamListener(api=tweepy.API(wait_on_rate_limit_notify=True,
                                             wait_on_rate_limit=True))
    streamer = tweepy.Stream(auth=auth, listener=listener)
    streamer.filter(locations=Loc_UK, track=Words_UK,
                    languages=['en'], is_async=True)

    # Place = 'London'
    # Lat = '51.450798'
    # Long = '-0.137842'
    # geoTerm = Lat+','+Long+','+'10km'

    last_id = None
    counter = 0
    sinceID = None

    results = True

    query = ("edinburgh OR glasgow OR UK OR uk OR Boris OR Johnson OR EU")

    while time.time() < RUNTIME:
        # print(geoTerm)

        # if counter < RUNTIME:
        # print(counter)
        try:
            tweets = api.search(q=query, count=100, lang="en", include_entities=True,
                                tweet_mode='extended', max_id=last_id)  # , since_id = sinceID)
            for tweet in tweets:
                asyncio.run(rest_process_tweets(tweet))
        except Exception as e:
            print(e)
        #counter += 1
        # else:
        #    results = False
        #  the following let the crawler to sleep for 15 minutes; to meet the Tiwtter 15 minute restriction
        # time.sleep(15*60)

    # Disconnect from streamer
    streamer.disconnect()
    print("You have been disconnected from twitter streamer API")

    with open('hybrid_stats.json', 'w') as json_file:
        json_file.truncate(0)
        json.dump(stats, json_file)
