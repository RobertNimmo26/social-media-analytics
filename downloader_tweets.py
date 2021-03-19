import os

import wget


def downloader(media_files):
    """Downloads the tweet media objects into the media_tweets folder"""

    # gets directory
    directory = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "media_tweets")

    # creates directory if directory doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        # for each media object
        for media_file in media_files:
            title = media_file.split("/")[-1]

            destination = os.path.join(directory, title)

            # download the media object using wget
            wget.download(media_file, out=destination)
    except:
        print("error occured while downloading")
