import re
import string

import emoji
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer


def lemmatize_tweets(array):
    wordnet_stemmer = WordNetLemmatizer()
    return [wordnet_stemmer.lemmatize(word) for word in array]


def remove_emoji(text):
    removed_emoji_text = re.sub(emoji.get_emoji_regexp(), r"", text)
    removed_emoji_text.encode("ascii", errors="ignore").decode()
    return removed_emoji_text


def tokenize_string(text):
    # Keeps converts text to lower case, keeps mentions/handles, reduces length of long words
    tokenizer = TweetTokenizer(
        preserve_case=False, strip_handles=False, reduce_len=True)
    tokens = tokenizer.tokenize(text)
    return tokens


def remove_punct_stopwords(array):
    stopwords_english = stopwords.words('english')
    punctuation = string.punctuation
    return [word for word in array if (word not in ('...', '…', '‘', '’', '“', '”') and word not in stopwords_english and word not in punctuation)]


def tweets_text_processor(text):
    text = remove_emoji(text)

    # Removes any URL's from tweets
    text = re.sub(r'https?:\/\/\S*', '', text, flags=re.MULTILINE)

    # Tokenizes tweet
    tokenized = tokenize_string(text)
    clearOfNoise = remove_punct_stopwords(tokenized)
    stemmed = lemmatize_tweets(clearOfNoise)
    try:
        if (stemmed[0] == "rt"):
            stemmed = stemmed[1:]
    except:
        pass
    return stemmed


def tweet_processor_streamer(tweet):
    """
    Gets processed data from Tweet object
    """
    place = False
    place_countrycode = None
    place_name = None
    place_country = None
    place_coordinates = None
    source = None
    exactcoord = None

    try:
        created = tweet['created_at']
        # The Tweet ID from Twitter in string format
        tweet_id = tweet['id_str']
        # The Tweet body
        text = tweet['text']
        # The username of the Tweet author
        username = tweet['user']['screen_name']

    except Exception as e:
        # Error with JSON, ignore tweet
        print(e)
        return None

    rt = False
    try:
        # Check if text is truncted and if it is get extended text
        if(tweet['truncated'] == True):
            text = tweet['extended_tweet']['full_text']

        # Check if tweet is a retweet
        elif(text.startswith('RT') == True):

            rt = True
            try:
                # Check if text is truncted and if it is get extended text
                if(tweet['retweeted_status']['truncated'] == True):
                    text = tweet['retweeted_status']['extended_tweet']['full_text']
                else:
                    text = tweet['retweeted_status']['full_text']
            except Exception:
                pass

    except Exception as e:
        print("Exception")
        print(e)

    entities = tweet['entities']

    hashtags = entities['hashtags']  # Any hashtags used in the Tweet
    hashtag_list = []
    for tag in hashtags:
        hashtag_list.append(tag['text'])

    mentions = entities['user_mentions']
    mention_list = []

    for mention in mentions:
        mention_list.append(mention['screen_name'])

    images_counter = 0
    videos_counter = 0
    media_urls = []
    try:
        for element in entities["media"]:
            if element["type"] == "photo":
                images_counter += 1
            elif element["type"] == "video":
                videos_counter += 1
            else:
                media_urls.append(element["media_url"])

    except:
        pass

    source = tweet['source']
    exactcoord = tweet['coordinates']

    coordinates = None
    if(exactcoord):
        coordinates = exactcoord['coordinates']

    #geoenabled = tweet['user']['geo_enabled']
    location = tweet['user']['location']
    # The user is verified
    verified = tweet["user"]['verified']

    # if ((geoenabled) and (text.startswith('RT') == False)):
    try:
        if(tweet['place']):
            place = True
            place_name = tweet['place']['full_name']
            place_country = tweet['place']['country']
            place_countrycode = tweet['place']['country_code']
            place_coordinates = tweet['place']['bounding_box']['coordinates']
    except Exception as e:
        print(e)
        print('error from place details')

    quote = (tweet["is_quote_status"])

    preprocessed_text = tweets_text_processor(text)

    tweet = {'_id': tweet_id, 'date': created, 'username': username,  'text': text, 'processed_text': preprocessed_text, "quote": quote, 'RT': rt, 'verified': verified,
             # 'geoenabled': geoenabled,
             'location': location,
             'coordinates': coordinates,
             'place': place,
             'place_name': place_name,
             'place_country': place_country,
             'country_code': place_countrycode,
             'place_coordinates': place_coordinates, "no_images": images_counter, "no_videos": videos_counter, "media_urls": media_urls, 'hashtags': hashtag_list, 'mentions': mention_list, 'source': source}
    return tweet


def tweet_processor_rest(tweet):
    """
    Gets processed data from Tweet object
    """
    place = False
    place_countrycode = None
    place_name = None
    place_country = None
    place_coordinates = None
    source = None
    exactcoord = None

    try:
        created = tweet.created_at
        # The Tweet ID from Twitter in string format
        tweet_id = tweet.id_str
        # The Tweet body
        text = tweet.full_text
        # The username of the Tweet author
        username = tweet.user.screen_name

    except Exception as e:
        # Error with JSON, ignore tweet
        print(e)
        return None
    rt = False
    try:
        # Check if text is truncted and if it is get extended text
        if(tweet.truncated == True):
            text = tweet.extended_tweet.full_text

        # Check if tweet is a retweet
        elif(text.startswith('RT') == True):

            rt = True
            try:
                # Check if text is truncted and if it is get extended text
                if(tweet.retweeted_status.truncated == True):
                    text = tweet.retweeted_status.extended_tweet.full_text
                else:
                    text = tweet.retweeted_status.full_text
            except Exception:
                pass

    except Exception as e:
        print("Exception")
        print(e)

    entities = tweet.entities

    hashtags = entities["hashtags"]  # Any hashtags used in the Tweet

    hashtag_list = []
    for tag in hashtags:
        hashtag_list.append(tag["text"])

    mentions = entities["user_mentions"]
    mention_list = []

    for mention in mentions:
        mention_list.append(mention["screen_name"])

    images_counter = 0
    videos_counter = 0
    media_urls = []
    try:
        for element in entities["media"]:
            if element.type == "photo":
                images_counter += 1
            elif element.type == "video":
                videos_counter += 1
            else:
                media_urls.append(element.media_url)

    except:
        pass

    source = tweet.source
    exactcoord = tweet.coordinates

    coordinates = None
    if(exactcoord):
        coordinates = exactcoord["coordinates"]

    #geoenabled = tweet.user.geo_enabled
    location = tweet.user.location
    # The user is verified
    verified = tweet.user.verified

    # if (text.startswith('RT') == False):
    try:
        if(tweet.place):
            place = True
            place_name = tweet.place.full_name
            place_country = tweet.place.country
            place_countrycode = tweet.place.country_code
            place_coordinates = tweet.place.bounding_box.coordinates
    except Exception as e:
        print(e)
        print('error from place details')

    quote = (tweet.is_quote_status)

    preprocessed_text = tweets_text_processor(text)

    tweet = {'_id': tweet_id, 'date': created, 'username': username,  'text': text, 'processed_text': preprocessed_text, "quote": quote, 'RT': rt, 'verified': verified,
             # 'geoenabled': geoenabled,
             'location': location,
             'coordinates': coordinates,
             'place': place,
             'place_name': place_name,
             'place_country': place_country,
             'country_code': place_countrycode,
             'place_coordinates': place_coordinates, "no_images": images_counter, "no_videos": videos_counter, "media_urls": media_urls, 'hashtags': hashtag_list, 'mentions': mention_list, 'source': source}
    return tweet
