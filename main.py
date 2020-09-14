from flask import Flask, render_template, abort, request
import sys
from twython import Twython
import nltk
from dictionary import Dictionary
import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 

APP_KEY = "Zm3yk6NO21n6bSqLk9cRz5VHM"
APP_SECRET = "0k5kfFqNGgmhuAXgqYDhFSW6czoASfQchIzassTisgD0Ixx0py"

twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()

twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)

app = Flask(__name__)

class SentimentScore:
    def __init__(self, positive_tweets, negative_tweets, neutral_tweets):

        self.positive_tweets = positive_tweets
        self.negative_tweets = negative_tweets
        self.neutral_tweets = neutral_tweets

        self.neg = len(negative_tweets)
        self.pos = len(positive_tweets)
        self.neut = len(neutral_tweets)


dictionaryN = Dictionary('negative-words.txt')

dictionaryP = Dictionary('positive-words.txt')

def sentiment(tweet):

    negative_score = 0
    positive_score = 0

    tokenizer = nltk.tokenize.TweetTokenizer()
    tweet_words = tokenizer.tokenize(tweet)

    for word in tweet_words:
        negative_score += dictionaryN.check(word)

    for word in tweet_words:
        positive_score += dictionaryP.check(word)

    if negative_score > positive_score:
        return 'negative'
    elif negative_score == positive_score:
        return 'neutral'
    else:
        return 'positive'

    # use dictionary to count negative frequent

def sentiment_analysis(tweets):

    negative_tweets = []
    positive_tweets = []
    neutral_tweets = []

    for tweet in tweets:

        res = sentiment(tweet['text'])

        if res == 'negative':
            negative_tweets.append(tweet['text'])
        elif res == 'positive':
            positive_tweets.append(tweet['text'])
        else:
            neutral_tweets.append(tweet['text'])

    return SentimentScore(positive_tweets, negative_tweets, neutral_tweets)

class TwitterClient(object): 
    ''' 
    Generic Twitter Class for sentiment analysis. 
    '''
    def __init__(self): 
        ''' 
        Class constructor or initialization method. 
        '''
        
        consumer_key = "Zm3yk6NO21n6bSqLk9cRz5VHM"
        consumer_secret = "0k5kfFqNGgmhuAXgqYDhFSW6czoASfQchIzassTisgD0Ixx0py"
        access_token = "1235855507325239297-0qrIDAvSWJApyCIhtlUfA3AUOq1xQR"
        access_token_secret = "qxyoQnxyVoxkZPFQpxKteT3UW6XzhyxlCyXUKL1jrzryb"

     
        try: 
        
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            
            self.auth.set_access_token(access_token, access_token_secret) 
        
            self.api = tweepy.API(self.auth) 
        except: 
            print("Error: Authentication Failed") 

    def clean_tweet(self, tweet): 
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())  

    def get_tweet_sentiment(self, tweet): 
        # create TextBlob object of passed tweet text 
        analysis = TextBlob(self.clean_tweet(tweet)) 
        # set sentiment 
        if analysis.sentiment.polarity > 0: 
            return 'positive'
        elif analysis.sentiment.polarity == 0: 
            return 'neutral'
        else: 
            return 'negative'

    def get_tweets(self, query, count=10): 
        ''' 
        Main function to fetch tweets and parse them. 
        '''
       
        tweets = [] 

        try: 
            
            fetched_tweets = self.api.search(q = query, count = count) 

         
            for tweet in fetched_tweets: 
                parsed_tweet = {} 

                parsed_tweet['text'] = tweet.text 
                 
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text) 

               
                if tweet.retweet_count > 0 and tweet.lang=="en": 
                    if parsed_tweet not in tweets: 
                        tweets.append(parsed_tweet) 
                elif tweet.lang=="en": 
                    tweets.append(parsed_tweet) 

            return tweets 

        except tweepy.TweepError as e: 
    
            print("Error : " + str(e)) 

def analysis(q): 
    
    api = TwitterClient() 
    
    tweets = api.get_tweets(query = q, count = 500) 

    # picking positive tweets from tweets 
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
    # percentage of positive tweets 
    #print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets))) 
    # picking negative tweets from tweets 
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 
    # percentage of negative tweets 
    
    #print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))) 
    # percentage of neutral tweets 
    #print("Neutral tweets percentage: {} %".format(100*len(tweets - ntweets - ptweets)/len(tweets))) 

    # printing first 5 positive tweets 

    #print("\n\nPositive tweets:") 
   # for tweet in ptweets[:30]: 
       # print(tweet['text']) 
  
    negative=0
    positive=0
    if len(ptweets)>0 and len(tweets)>0:
        positive=(100*len(ptweets)/len(tweets))
    if len(ntweets)>0 and len(tweets)>0:
        negative=(100*len(ntweets)/len(tweets))
    
    if negative==0:
        ratingbase=positive+20
    else:
        ratingbase=positive-negative
    
    
    if ratingbase<0:
        ratingbase=(-1)*ratingbase
    elif ratingbase==0:
        ratingbase=12.5
    else:
        ratingbase=ratingbase
    rating=(ratingbase/50)*100
    
    if len(tweets)==0:
        return 0
    elif positive==0 and negative>0:
        return 1
    elif rating>0 and rating<=20:
        return 2
    elif rating>20 and rating<=40:
        return 3
    elif rating>40 and rating<=60:
        return 3.5
    elif rating>60 and rating<=70:
        return 4
    elif rating>70 and rating<=80:
        return 4.5
    else:
        return 5
    
     
    # printing first 5 negative tweets 
    #print("\n\nNegative tweets:") 
    #for tweet in ntweets[:10]: 
        #print(tweet['text'])

@app.route("/", methods=["POST","GET"])
def root():

    if request.method == "POST":
        stars=analysis(request.form['twitter_username'])
        print(stars)
        return render_template("result.html", username=request.form['twitter_username'],stars=stars)
    else:
        return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


app.run(debug=True)
