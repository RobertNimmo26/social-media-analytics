import json
import statistics
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

JSON_INPUT = "streamer.json"
NUMBER_OF_CLUSTERS = 6


def tokenised_data(doc):
    """Returns tokenised data"""
    return doc


def record_stats(km_model):
    """Records cluster stats and writes them into a JSON file"""
    stats = {}
    km_model_labels = km_model.labels_.tolist()
    cluster_size = Counter(km_model_labels)
    cluster_size_values = list(cluster_size.values())
    max_size = max(cluster_size_values)
    min_size = min(cluster_size_values)
    mean_avg_size = statistics.mean(cluster_size_values)
    median_avg_size = statistics.median(cluster_size_values)

    stats['cluster_size'] = cluster_size
    stats['groups_formed'] = NUMBER_OF_CLUSTERS
    stats['max_size'] = max_size
    stats['min_size'] = min_size
    stats['mean_avg_size'] = mean_avg_size
    stats['median_avg_size'] = median_avg_size

    stats['cluster'] = {}
    clustering = defaultdict(list)
    for idx, label in enumerate(km_model.labels_):
        clustering[label].append(idx)

    # Printing representative terms
    clusterCenters = km_model.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()
    for i in range(NUMBER_OF_CLUSTERS):
        cluster_stats = {}
        cluster_stats['top_30_terms'] = [terms[index]
                                         for index in clusterCenters[i, :30]]

        stats['cluster'][f'cluster_{i}'] = cluster_stats

    json_output = JSON_INPUT.split(".")[0]

    with open(f'{json_output} groups.json', 'w') as json_file:
        json_file.truncate(0)
        json.dump(stats, json_file)


if __name__ == '__main__':
    # importing the data
    tweets_df = pd.read_json(JSON_INPUT)

    print(len(tweets_df))

    # Vectorialising the strings
    vectorizer = TfidfVectorizer(
        max_features=2500,  # Only use the int(max_features) most popular words
        min_df=7,  # Words must occur in int(min_df) documents
        # Words that occur in at most int(max_df)*100 % of documents
        max_df=0.8,
        tokenizer=tokenised_data,  # Tokenizer for tweets
        preprocessor=tokenised_data,
        token_pattern=None
    )

    # Fit the vectorizer to the tweets "processed_text"
    vectorizer.fit(tweets_df["processed_text"])

    # Transform the vectorizer to the tweets "processed_text"
    tf_idfVectors = vectorizer.transform(tweets_df["processed_text"]).toarray()

    # Fit KMeans to the vectorizer
    km_model = KMeans(n_clusters=NUMBER_OF_CLUSTERS, init="k-means++",
                      verbose=10, max_iter=5).fit(tf_idfVectors)

    # Record the stats
    record_stats(km_model)
