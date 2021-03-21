# Social Media Analytics

## Web Science Coursework 2021

This project is a piece of coursework for my Web Science course at university.

### Overview

The objective of this coursework is to develop a Twitter crawler for data collection in English and to conduct social media analytics.

### Installation Instructions

1. Create a new Python3 virtual environment using your preffered method. This project has only been tested with Python 3.8.1, however, any version of Python 3.5 or greater should work.

   - Instructions for setting up a virtual environment using `virtualenv` can be found [here](https://virtualenv.pypa.io/en/latest/installation.html).

2. Activate your virtual environment

3. Navigate to the `social-media-analytics` folder if you haven't already. This is the same folder as this `readme.md` file.
4. Install the required packages using `pip install –r requirements.txt`. This will install the required packages required for this project.
5. For the first time you use the program, you will be required to install NLTK Data. The easiest way to install this additional data is using the interactive installer.
   1. In your command prompt, start your python interpreter. This would be using the command python or python3 depending on how your environment is set-up.
      ```
      python
      ```
   2. Once Python is running you can run the commands to import `nltk` and download the data.
      ```
      >>> import nltk
      >>> nltk.download()
      ```
   3. This should bring up a interactive window. You can then navigate to "All Packages" and download `stopwords` and `wordnet`. You can also just choose `all` in the "Collection" menu, however, this will download a lot of uneeded data as well.
   4. Once you are done you can close the window and exit the Python interpreter with the command:
      ```
      >>> exit()
      ```
6. This project uses the Twitter API. You will be required to have a Twitter developer account to run the crawlers.
   - You can add your account API keys to a `.env` file created in the main folder. The contents should look like this:
   ```
   CONSUMER_KEY="<EXAMPLE_CONSUMER_KEY>"
   CONSUMER_SECRET="<EXAMPLE_CONSUMER_SECRET>"
   ACCESS_TOKEN="<EXAMPLE_ACCESS_TOKEN>"
   ACCESS_TOKEN_SECRET="<EXAMPLE_ACCESS_TOKEN_SECRET>"
   ```
7. You will require mongoDB to store the tweet data.
   - To set up a local database, you can install mongoDB compass [here](https://www.mongodb.com/try/download/compass).

### Pre-setup run (quick test)

The project has a 5 minute sample data which has been crawled using the streamer API. This can be used to test the clustering programs quickly.

#### To run clustering

1. Navigate to the `kmeans` folder. This can be done with if you are in the main directory:
   ```
   cd kmeans
   ```
   This is where the sample data `streamer_5min.json` is stored.
2. **(Optional)** To get the optimal number of cluster run the `kmeans_elbow_method.py`. The parameters have been preset to the input `streamer_5min.json`. This will present a graph with the optimal number of clusters.
   ```
   python streamer_elbow_method.py
   ```
   - The optimal number of clusters when ran was 14
3. To run the clustering program, set the constants to the JSON input file and optimal number of clusters. This is already preset.
   ```
   JSON_INPUT = "streamer_5min.json"
   NUMBER_OF_CLUSTERS = 14
   ```
4. After running the code, a JSON file with stats about the clusters formed called `streamer_5min groups.json` will be created in the `kmeans` folder. You can then view a overview of the kmeans clusters and the top terms in each cluster.

### How to run

There are 4 runable files which are used to run the two crawlers and the tweet clustering.

#### Crawlers

To run the crawlers, you must make sure your mongoDB database is connected. The code in both `streamer_crawler.py` and `hybrid_crawler.py` is set up for a local mongoDB database instance. The code will have to be changed if you are hosting the mongoDB database in a external server.

To download media objects from tweets while streaming, set `DOWNLOAD = True`. Tweets media objects will be downloaded into a folder called `media_tweets` which is located in the project folder.

To set the runtime of the crawler, set the constant `RUNTIME` to the number of seconds you will like the crawler to run. e.g. `60 * 60` = 1 hour.

- `streamer_crawler.py`

  - This file can be used to run the twitter streamer API. Each tweet is stored in the mongoDB database in the database `TwitterDB` and a collection called `streamer` and overall stats about the tweets will be exported to `streamer_stats.json` after crawling.
  - The current location and words which are being used in the streamer are for the UK. You can change the location by changing `Loc_UK` to your prefered location and `Words_UK` to your prefered words.

  - To run the crawler, use the command:
    ```
    python streamer_crawler.py
    ```

- `hybrid_crawler.py`

  - This file runs a streamer and rest API crawler simultaneously. Each tweet is stored in the mongoDB database in the database `TwitterDB` and a collection called `hybrid_streamer` for the streamer data; `hybrid_rest` for the hybrid data and overall stats about the tweets will be exported to `hybrid_stats.json` after crawling.

  - The syntax for the hybrid crawler if very similar to the streamer crawler.

  - The current location and words which are being used in the filter are for the UK. You can change the location by changing `Loc_UK` to your prefered location and `Words_UK` to your prefered words. For the REST API, you can set the query terms in the `query` tuple. You can uses logical operators such as `OR` and `AND` to split different terms.

  - To run the crawler, use the command:
    ```
    python hybrid_crawler.py
    ```

#### Clustering

Clustering programs are located in the `kmeans` folder.

- `kmeans_elbow_method.py`
  - This file find the optimal number of clusters to cluster the tweets. This will output a graph which can be used to find the "elbow" which is the optimal number of clusters.
  - More information about the elbow method can be found [here](<https://en.wikipedia.org/wiki/Elbow_method_(clustering)>).
  - You will be required to set the input JSON file.
    ```
    JSON_INPUT = "<INPUT_JSON_NAME>"
    ```
- `kmeans_similarity.py`
  - This file clusters tweets based on the input from `kmeans_elbow_method.py`.
  - You will be required to set the input JSON file and the number of clusters you will like to cluster the data with.
    ```
    JSON_INPUT = "<INPUT_JSON_NAME>"
    NUMBER_OF_CLUSTERS = <OPTIMAL_NUMBER_OF_CLUSTERS>
    ```

1. To navigate to the `kmeans` folder from the main director, you can run the command:

   ```
   cd kmeans
   ```

2. Download a json file from your mongoDB of the streamer API tweets. You can follow this guide [here](https://docs.mongodb.com/compass/current/import-export/#export-data-from-a-collection) to do this. Add this file to the kmeans folder.
3. Open the `kmeans_elbow_method.py` file and set the `JSON_INPUT` constant to your JSON file input.
4. To run the `kmeans_elbow_method.py`, run the command:
   ```
   python kmeans_elbow_method.py
   ```
   This will output the optimal cluster number.
5. Open the `kmeans_elbow_method.py` file and set the `JSON_INPUT` constant to your JSON file input and `NUMBER_OF_CLUSTERS` constant to the optimal number of clusters which you got from `kmeans_elbow_method.py`.
6. After running the code, a JSON file with stats about the clusters formed called `<INPUT_JSON_NAME> groups.json` will be created in the `kmeans` folder. You can then view a overview of the kmeans clusters and the top terms in each cluster.
