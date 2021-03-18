import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from yellowbrick.cluster import KElbowVisualizer, SilhouetteVisualizer


JSON_INPUT = "StreamedTweets.json"


def tokenised_data(doc):
    return doc


if __name__ == '__main__':
    # importing the data
    tweets_df = pd.read_json(JSON_INPUT)

    # Vectorialising the strings, bag of words
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

    tf_idfVectors = vectorizer.transform(tweets_df["processed_text"]).toarray()

    # Elbow method to find the best cluster
    km_model = KMeans(init="k-means++", verbose=10, max_iter=5)

    k_range = range(2, 50, 2)
    visualizer = KElbowVisualizer(km_model, metric='silhouette', k=k_range)
    # visualizer = SilhouetteVisualizer(model, colors='yellowbrick')
    visualizer.fit(tf_idfVectors)        # Fit the data to the visualizer
    visualizer.show()        # Finalize and render the figure
