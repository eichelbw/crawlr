import tweepy
from tweepy.streaming import StreamListener
from datetime import datetime
import json
import config

consumer_key, consumer_secret = config.CONSUMER_KEY, config.CONSUMER_SECRET
access_token = config.ACCESS_TOKEN
access_token_secret = config.ACCESS_TOKEN_SECRET

# much of this structure is heavily inspire by 
# https://github.com/computermacgyver/twitter-python/blob/master/streaming.py
# that version saves json objects, and this one grabs text and coerces
# it into a roughly csv format.

### USAGE ###
# define filter in ./FILTER.txt (one term/line)
#


class listener(StreamListener):
    """pretty basic streaming api listener."""

    def __init__(self, target):
        super(listener, self).__init__(self)
        self.target = target # where 2 save the tweets

    def on_data(self, data): # called when the listener receives a new tweet
        print "got a tweet"
        tweet(json.loads(data), self.target).commit()
        return True

    def on_error(self, status):
        print status

    def on_timeout(self):
        print "timeout"
        return True # don't kill the stream, yo

class tweet:
    """takes info from listener, formats it, commits it to csv"""

    def __init__(self, jsn, target):
        self.tweet_text = self.csv_format(self.jsn)
        self.target = target

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
        print "%s - %s" % (datetime.now(), self.tweet_text) # print to the console just to have something to look at
        with open(self.target, "a") as f:
            f.write(self.tweet_text + "\n") # append tweet to target


if __name__ == '__main__':
    while True:
        try:
            # create the listener
            stream_listener = listener("test.csv")
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)

            # get the filter terms
            filter_terms = []
            with open("FILTER.txt", "r") as f:
                for line in f:
                    filter_terms.append(line.strip())
            print "%s - starting stream to track %s" % (datetime.now(), ",".join(filter_terms))

            twitterStream = tweepy.Stream(auth, stream_listener)
            twitterStream.filter(track=filter_terms)
        except KeyboardInterrupt:
            print "%s - caught keyboardinterrupt, killing stream" % datetime.now()
            twitterStream.disconnect()
            break
        except:
            print "something real strange is up, yo"
            break
