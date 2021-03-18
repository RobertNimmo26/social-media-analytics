# importing the data
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer, _preprocess
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
import numpy as np
import json
from collections import Counter

SIMILARITY = 0.5
PROMINENT_CLUSTER_SIZE = 5


class Cluster():
    """
    Hold informations on the cluster
    """
    # Individual Cluster Class

    def __init__(self, cluster_id, vectorizer):
        self.cluster_id = cluster_id
        self.tweets_df = []
        self.tweets_text = []
        self.number_tweets = 0

        # computes inital cluster vector and vectorizer
        self.cluster_vector = None
        self.cluster_vectorizer = vectorizer

    def get_tweets_df(self):
        return self.tweets_df

    def get_number_tweets(self):
        return self.number_tweets

    def get_cluster_vector(self):
        return self.cluster_vector

    def top_features(self):
        # feature_array = self.cluster_vectorizer.get_feature_names()
        # top_n = 5
        # indices = np.argsort(self.cluster_vector.toarray())[::-1]

        # top_features = [feature_array[i] for i in indices[:top_n]]
        # print(top_features)
        # return top_features

        top_features = Counter(self.tweets_text)
        return top_features

    def compute_similarity(self, tweet):
        tweet_vector = self.cluster_vectorizer.transform([tweet])

        # Computes the cosine similarity between tweets
        cosine_similarities = cosine_similarity(
            tweet_vector, self.cluster_vector).flatten()
        return (cosine_similarities[0], self.cluster_id)

    def compute_cluster_vector(self):
        # Might need to add back
        # self.cluster_vectorizer = TfidfVectorizer()
        # self.cluster_vectorizer.fit(self.tweets_text)
        self.cluster_vector = self.cluster_vectorizer.transform(
            [self.tweets_text])

    def add_new_tweet(self, tweet_df):
        self.tweets_text.extend(tweet_df["processed_text"])
        self.tweets_df.append(tweet_df)
        self.number_tweets += 1
        self.compute_cluster_vector()


class ClusterContainer():
    """
    Contains each cluster and hold extra information to do with the clusters
    """
    # Container class for Cluster Object

    def __init__(self, vectorizer):
        self.clusters = []
        self.cluster_counter = 0
        self.vectorizer = vectorizer

    def create_cluster(self, tweet_df):
        cluster = Cluster(self.cluster_counter, self.vectorizer)
        cluster.add_new_tweet(tweet_df)
        self.clusters.append(cluster)
        self.cluster_counter += 1

    def get_clusters(self):
        """gets all the clusters"""
        return self.clusters

    def get_cluster(self, index):
        """gets a specific cluster"""
        return self.clusters[index]


def tokenised_data(doc):
    return doc


if __name__ == '__main__':

    tweets_df = pd.read_json("Collection 10mins.json")

    # Vectorialising the all the tweets, bag of words
    vectorizer = TfidfVectorizer(
        max_features=2500,  # Only use the int(max_features) most popular words
        min_df=7,  # Words must occur in int(min_df) documents
        # Words that occur in at most int(max_df)*100 % of documents
        max_df=0.8,
        tokenizer=tokenised_data,
        preprocessor=tokenised_data,
        token_pattern=None
    )

    vectorizer.fit(tweets_df["processed_text"])

    # Creates new cluster array
    cluster_container = ClusterContainer(vectorizer)

    cluster_container.create_cluster(tweets_df.iloc[0])

    for i in tweets_df.index[1:]:
        tweet = tweets_df.iloc[i]
        cosine_sim = [0, None]
        for i in cluster_container.get_clusters():
            temp = i.compute_similarity(tweet["processed_text"])
            #print(cosine_sim, temp)
            if cosine_sim[0] < temp[0]:
                cosine_sim = temp

        if cosine_sim[0] >= SIMILARITY:
            cluster = cluster_container.get_cluster(cosine_sim[1])
            cluster.add_new_tweet(tweet)
            # print("added " + tweet["text"] + " to " +
            #       str(cosine_sim[1]) + "\n\n")

        else:
            cluster_container.create_cluster(tweet)
            #print("new cluster for tweet created " + tweet["text"]+"\n\n")

    cluster_output = {}
    cluster_output["clusters"] = []

    clusters = cluster_container.get_clusters()

    for cluster in clusters:
        cluster_json = {}
        num_tweets = cluster.get_number_tweets()
        cluster_json["number of tweets"] = num_tweets

        if num_tweets >= PROMINENT_CLUSTER_SIZE:
            cluster_json["prioritised"] = True
            cluster_json["prominent terms"] = cluster.top_features()

        cluster_output["clusters"].append(cluster_json)

    print(f"There are {len(cluster_container.get_clusters())} clusters")

    cluster_output["number of clusters"] = len(clusters)

    with open('streamer_groups.json', 'w') as json_file:
        json_file.truncate(0)
        json.dump(cluster_output, json_file)
