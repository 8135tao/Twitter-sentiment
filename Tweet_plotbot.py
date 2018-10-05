import tweepy
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer() 
import matplotlib.pyplot as plt
#from matplotlib import style
#style.use('ggplot')
plt.use('Agg')

import time
#import json
import requests as req
from datetime import datetime

# Twitter API Keys
# import consumer_key, consumer_secret, access_token, access_token_secret

consumer_key = os.environ.get("consumer_key")
consumer_secret = os.environ.get("consumer_secret")
access_token = os.environ.get("access_token")
access_token_secret = os.environ.get("access_token_secret")
# print(consumer_key)
# print(consumer_secret)
# print(access_token)
# print(access_token_secret)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

# create function that does the sentiment analysis
target_account_set = set([])


def TweetBot():
   
    #last_status = 0
    
    mentions = api.search(q="@tao6178 Analyze:")
    #, since_id = 1047324147112656896)
    words = []
    oldest_tweet = None
    #print(mentions)
    #print(json.dumps(mentions,sort_keys=True,indent=4))
    #print(mentions["statuses"][0]["user"]["name"])
    try:
        command = mentions["statuses"][0]["text"]
        words = command.split("Analyze:")
        target_account = words[1].strip()
        #target_account = "@WSJ"
        helper = mentions["statuses"][0]["user"]["name"]
        print(f"analysis for target_account: {target_account} at the request of @{helper}")
        
        if target_account not in target_account_set:
            target_account_set.add(target_account)
            counter = 0
            sentiments =[]
            results =[]
            for x in range(25):

                
                user_tweets = api.user_timeline(target_account, max_id = oldest_tweet)

                # Loop through tweets
                for tweet in user_tweets:
                    results = analyzer.polarity_scores(tweet["text"])
                    cpd = results["compound"]
                    pos = results["pos"]
                    neu = results["neu"]
                    neg = results["neg"]
                    counter += 1
                    oldest_tweet = tweet['id'] - 1
                    
                    sentiments.append({"Date": tweet["created_at"], 
                               "Compound": cpd,
                               "Positive": pos,
                               "Negative": neg,
                               "Neutral": neu,
                               "Tweets Ago": counter})
            
            sentiments_pd = pd.DataFrame(sentiments)
            
            legend_list =[]

            fig, ax = plt.subplots(1,1,figsize=(10,6))
            
            x_vals = sentiments_pd["Tweets Ago"]
            y_vals = sentiments_pd["Compound"]
            #plt.plot(x_vals, y_vals, linewidth=1, marker='o', color='r')
            leg, = plt.plot(x_vals, y_vals, linewidth=1, marker='o', color='r')
            legend_list.append(leg)
    
            
            
            # # Incorporate the other graph properties
            now = datetime.now()
            now = now.strftime("%Y-%m-%d %H:%M")
            plt.title(f"Sentiment Analysis of Tweets ({now}) for {target_account}")
            plt.xlim([x_vals.max(),x_vals.min()]) 
            plt.ylabel("Tweet Polarity")
            plt.xlabel("Tweets Ago")
            
            legen = plt.legend(handles = legend_list)
            legen.get_texts()[0].set_text('sentiment of tweets for '+target_account)

            plt.show()
            
            
            fig.savefig(f"sentiment_analysis.png")
            
            api.update_with_media("sentiment_analysis.png", f"Sentiment analysis for {target_account} (thx @{helper}!)" )
            #api.update_status(f"Thank you! @{helper}")
            

        else:
            print("already analyzed "+target_account)
    
    except (IndexError,tweepy.TweepError):
        print("nothing found")

        
# let the bot run 100 times, waiting 5 min between each time
counter = 0
while(counter < 100):
    TweetBot()
    print("\n")
    time.sleep(300)
    counter += 1

