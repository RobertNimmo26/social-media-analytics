import datetime

from process_tweets import tweets_text_processor


def newsworthiness_tweet(tweet, type):
    """Calculates  the newsworthiness of each tweet"""

    quality_score = 0
    list_terms = ['news', 'report', 'journal', 'write', 'editor', 'analyst', 'analysis', 'media', 'updates', 'stories', 'trader',
                  'investor', 'forex', 'stock', 'finance', 'market', "journalist", "reporter", "bbc", "expert", "column", "alumni", "proffessor"]
    list_spam = ['ebay', 'review', 'shopping', 'deal', 'sale', 'sales', 'link', 'click', 'marketing', 'promote', 'discount',
                 'products', 'store', 'diet', 'weight', 'porn', 'followback', 'follow back', 'lucky', 'winners', 'prize', 'hiring']

    # Description weight
    try:
        if type == "rest":
            description = tweet.user.description
        else:
            description = tweet["user"]["description"]

        description_processed = tweets_text_processor(description)
        description_weight = 0
        for word in description_processed:
            if word in list_terms:
                description_weight += 2
            elif word in list_spam:
                description_weight += 0.01
            else:
                description_weight += 1
        if(description_weight > 0):
            normalised_weight = description_weight / \
                (len(description_processed)*2)
            quality_score += (normalised_weight)
        else:
            normalised_weight = 0
            quality_score += 0
    except Exception:
        # Error with JSON, ignore tweet
        normalised_weight = 0
        quality_score += 0

    # Account age weight
    age_weight = 0
    try:
        if type == "rest":
            account_creation_date_string = tweet.user.created_at
        else:
            account_creation_date_string = tweet["user"]["created_at"]
        months = {"Jan": 1,
                  "Feb": 2,
                  "Mar": 3,
                  "Apr": 4,
                  "May": 5,
                  "Jun": 6,
                  "Jul": 7,
                  "Aug": 8,
                  "Sep": 9,
                  "Oct": 10,
                  "Nov": 11,
                  "Dec": 12}
        date_split = account_creation_date_string.split()
        month = date_split[1]
        day = date_split[2]
        year = date_split[5]
        date_time_obj = datetime.datetime(int(year), months[month], int(day))
        date_now_obj = datetime.datetime.now()
        day_diff = (date_now_obj-date_time_obj).days
        if day_diff > 60:
            age_weight = 1.0
        else:
            age_weight = 0.1
        quality_score += age_weight
    except Exception:
        # Error with JSON, ignore tweet
        quality_score += 0

    # No. of Followers
    try:
        if type == "rest":
            follower_count = int(tweet.user.followers_count)
        else:
            follower_count = int(tweet["user"]["followers_count"])

        follower_weight = 0
        if follower_count < 50:
            follower_weight = 0.5
        elif follower_count < 5000:
            follower_weight = 1.0
        elif follower_count < 10000:
            follower_weight = 1.5
        elif follower_count < 100000:
            follower_weight = 2.0
        elif follower_count < 200000:
            follower_weight = 2.5
        else:
            follower_weight = 3.0
        normalized_follower_weight = follower_weight/3
        quality_score += normalized_follower_weight
    except Exception:
        # Error with JSON, ignore tweet
        quality_score += 0

    try:
        # Verified
        if type == "rest":
            is_verified = tweet.user.verified
        else:
            is_verified = tweet["user"]["verified"]

        if (is_verified):
            verified_weight = 1.5
        else:
            verified_weight = 1.0
        normalized_verified = verified_weight/1.5
        quality_score += normalized_verified
    except Exception:
        # Error with JSON, ignore tweet
        quality_score += 0

    try:
        # Profile pic
        profile_weight = 1

        if type == "rest":
            dp = tweet.user.default_profile
        else:
            dp = tweet["user"]["default_profile"]

        if(dp):
            profile_weight = 0.5

        quality_score += profile_weight
    except Exception:
        # Error with JSON, ignore tweet
        quality_score += 0

    # Calculating overall score
    quality_score_overall = quality_score/5

    if quality_score_overall >= 0.7:
        return True
    else:
        return False
