import tweepy
from tweepy.streaming import StreamListener
import json
from bs4 import BeautifulSoup
import config

consumer_key, consumer_secret = config.CONSUMER_KEY, config.CONSUMER_SECRET
access_token = config.ACCESS_TOKEN
access_token_secret = config.ACCESS_TOKEN_SECRET

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
        StreamListener.__init__(self)
        self.target = target

    def on_data(self, data):
        jsn = json.loads(data)
        if jsn['lang'] == 'en': # only english words for now
            if jsn['text'][:2] == "RT": # don't care who's being retweeted
                tweet(jsn['text'].split(": ")[1], self.target).commit()
            else:
                tweet(jsn['text'], self.target).commit()
        return True

    def on_error(self, status):
        print status

    def on_timeout(self):
        return True # don't kill the stream, yo

class tweet:
    """takes info from listener, formats it, commits it to csv"""

    def __init__(self, in_text, target):
        print "tweet init"
        self.in_text = in_text
        self.target = target
        self.tweet_text = self.csv_format(self.in_text)

    def csv_format(self, in_txt):
        in_txt = in_txt.split()
        in_txt = [word.lower().strip('\'\"-,.:;!?') for word in in_txt]
        out_txt = []
        for word in in_txt:
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



