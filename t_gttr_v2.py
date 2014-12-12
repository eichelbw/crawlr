import tweepy
from tweepy.streaming import StreamListener
from datetime import datetime
import os
import json
import config

consumer_key, consumer_secret = config.CONSUMER_KEY, config.CONSUMER_SECRET
access_token = config.ACCESS_TOKEN
access_token_secret = config.ACCESS_TOKEN_SECRET

# much of this structure is heavily inspire by 
# https://github.com/computermacgyver/twitter-python/blob/master/streaming.py
# that version saves json objects, and this one grabs text and coerces
# it into a roughly csv format.

class scraper:

    def __init__(self, track, target):
        self.track = track
        self.target = target

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        twitterStream = tweepy.Stream(auth, listener(self.target))
        twitterStream.filter(track=[self.track])

class listener(StreamListener):
    """pretty basic streaming api listener."""

    def __init__(self, target):
        super(StreamListener, self).__init__(self)
        self.base_path = target
        os.system("touch %s" % target)

    d = datetime.today()
    self.filename = "%i-%02d-%02d.csv" % (d.year, d.month, d.day)
    self.fh = open(self.base_path + "/" + self.filename, "a")

    self.tweet_count = 0
    self.error_count = 0
    self.limit_count = 0
    self.last = datetime.now()

    def on_data(self, data): # called when the listener receivs a new tweet
        tweet(json.loads(data), self.base_path).commit()
        return True

    def on_error(self, status):
        print status

    def on_timeout(self):
        return True # don't kill the stream, yo

class tweet:
    """takes info from listener, formats it, commits it to csv"""

    def __init__(self, jsn, target):
        self.jsn = jsn
        self.target = target
        self.tweet_text = self.csv_format(self.jsn)

    def csv_format(self, in_jsn):
        if in_jsn['lang'] == 'en': # only english words for now
            if in_jsn['text'][:2] == 'RT': # don't care who's being retweeted
                in_jsn = in_jsn['text'].split(": ")[1].split()
            else:
                in_jsn = in_jsn['text'].split()

        in_jsn = [word.lower().strip('\'\"-,.:;!?') for word in in_jsn]
        out_txt = []

        for word in in_jsn:
            try:
                if word == "&amp": # discard a bunch of nonsense
                    pass
                elif word[0] == "@":
                    pass
                elif word[:4] == "http":
                    pass
                else: # otherwise, spit it out
                    out_txt.append(word)
            except: # something weird. maybe triggered by short tweet? discard
                pass
        out_txt = ",".join(out_txt).encode('utf-8')
        return out_txt

    def commit(self):
        """writes the current tweet to the destination csv"""
        print self.tweet_text # print to the console just to have something to look at
        with open(self.target, "a") as f:
            f.write(self.tweet_text + "\n")


if __name__ == '__main__':
    while True:
        try:
            # create the listener
            listener = listener()
        except TimeoutException:
            print "%s - Timeout exception caught. Closing stream." % datetime.now()

