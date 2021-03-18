import os
import wget


def downloader(media_files):

    directory = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "media_tweets")

    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        for media_file in media_files:
            title = media_file.split("/")[-1]

            destination = os.path.join(directory, title)
            wget.download(media_file, out=destination)
    except:
        print("error occured while downloading")
