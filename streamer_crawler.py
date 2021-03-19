import json
import time

import tweepy
from decouple import config
from pymongo import MongoClient

from newsworthyness_tweets import newsworthiness_tweet
from process_tweets import tweet_processor_streamer
from downloader_tweets import downloader

# Keys of the app
CONSUMER_KEY = config("CONSUMER_KEY")
CONSUMER_SECRET = config("CONSUMER_SECRET")
ACCESS_TOKEN = config("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = config("ACCESS_TOKEN_SECRET")

# Download media objects
DOWNLOAD = False

# Runtime in seconds
RUNTIME = 60 * 1

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
if (not api):
    print('Can\'t authenticate')
    print('failed cosumeer id ----------: ', CONSUMER_KEY)

# this is to setup local Mongodb
client = MongoClient('127.0.0.1', 27017)  # is assigned local port
dbName = "TwitterDB"  # set-up a MongoDatabase
db = client[dbName]
collName = 'streamer'  # here we create a collection
collection = db[collName]  # This is for the Collection  put in the DB

stats = {
    "total": 0,
    "streamer_total": 0,
    "no_retweets": 0,
    "no_quotes": 0,
    "no_images": 0,
    "no_video": 0,
    "no_verified": 0,
    "no_geotagged": 0,
    "no_coordinates": 0,
    "no_location_place": 0
}


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
            # if tweet["geoenabled"]:

            if tweet["coordinates"] is not None:
                stats["no_coordinates"] += 1
            if tweet["place"] != False:
                stats["no_geotagged"] += 1
                stats["no_location_place"] += 1

            collection.insert_one(tweet)

            if DOWNLOAD:
                if tweet["media_urls"]:
                    downloader(tweet["media_urls"])


if __name__ == '__main__':

    Loc_UK = [-10.392627, 49.681847, 1.055039, 61.122019]  # UK and Ireland
    Words_UK = ["Boris", "Prime Minister", "Tories", "UK", "London", "England", "Manchester", "Sheffield", "York", "Southampton",
                "Wales", "Cardiff", "Swansea", "Banff", "Bristol", "Oxford", "Birmingham", "Scotland", "Glasgow", "Edinburgh", "Dundee", "Aberdeen", "Highlands",
                "Inverness", "Perth", "St Andrews", "Dumfries", "Ayr",
                "Ireland", "Dublin", "Cork", "Limerick", "Galway", "Belfast", " Derry", "Armagh",
                "BoJo", "Labour", "Liberal Democrats", "SNP", "Conservatives", "First Minister", "Nicola Sturgeon", "Surgeon", "Chancelor",
                "Boris Johnson", "Keir Stramer"]

    print(f"Tracking: {str(Words_UK)}")

    # Set up the listener. The 'wait_on_rate_limit=True' is needed to help with Twitter API rate limiting.
    listener = StreamListener(api=tweepy.API(wait_on_rate_limit_notify=True,
                                             wait_on_rate_limit=True))
    streamer = tweepy.Stream(auth=auth, listener=listener)
    streamer.filter(locations=Loc_UK, track=Words_UK,
                    languages=['en'], is_async=True)

    # Wait RUNTIME seconds before disconnecting from streamer
    time.sleep(RUNTIME)
    streamer.disconnect()
    print("You have been disconnected from twitter streamer API")

    with open('streamer_stats.json', 'w') as json_file:
        json_file.truncate(0)
        json.dump(stats, json_file)
