import tweepy
from tweepy.streaming import StreamListener
import json
from bs4 import BeautifulSoup
import config

consumer_key, consumer_secret = config.CONSUMER_KEY, config.CONSUMER_SECRET
access_token = config.ACCESS_TOKEN
access_token_secret = config.ACCESS_TOKEN_SECRET

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# tweets = api.search(q="#CrimingWhileWhite")

class listener(StreamListener):
    """basic stream listener for now. just prints to console. will style on it
    l8r
    """

    def on_data(self, data):
        jsn = json.loads(data)
        if jsn['lang'] == 'en': # only english words for now
            if jsn['text'][:2] == "RT":
                tweet(jsn['user']['screen_name'], jsn['text'].split(": ")[1]).commit()
            else:
                tweet(jsn['user']['screen_name'], jsn['text']).commit()
        return True

    def on_error(self, status):
        print status

    def on_timeout(self):
        return True # don't kill the stream, yo

class tweet:
    """takes info from listener, formats it, commits it to csv"""

    def __init__(self, user, in_text):
        self.user = user # maybe use this later
        self.in_text = in_text
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
                elif word[:5] == "http:":
                    pass
                else: # otherwise, spit it out
                    out_txt.append(word)
            except: # something weird. maybe triggered by short tweet? discard
                pass
        out_txt = ",".join(out_txt).encode('utf-8')
        return out_txt

    def commit(self):
        print self.tweet_text
        with open("cww_tweets.csv", "a") as f:
            f.write(self.tweet_text + "\n")



auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
twitterStream = tweepy.Stream(auth, listener(api))
twitterStream.filter(track=["#CrimingWhileWhite"])
