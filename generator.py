import os
import tweepy
import re
import markovify

user_cache = dict()
user_tweet_model_cache = dict()

client = tweepy.Client(os.environ["TWITTER_BEARER_TOKEN"])


class GenerateResponse:

    def __init__(self, tweets, model_tweet_count):
        self.tweets = tweets
        self.model_tweet_count = model_tweet_count


def fetch_user(username):
    """
    Returns twitter user with format:
      <User id=44196397 name=Elon Musk username=elonmusk>
    Or None if not found.
    """
    # Standardise username format - tweeter is case-insensitive
    username = username.lower()
    if username in user_cache:
        print(f"Fetching {username} from cache!")
        return user_cache[username]

    user = client.get_user(username=username).data
    print(client.get_user(username=username))

    # Store in cache
    user_cache[username] = user
    return user


def generate(username):
    """
    Returns generated tweets along with meta data on model run with format:
      <GenerateResponse tweets=["hi"] tweet_count=200>
    """
    user = fetch_user(username)

    # Only fetch from cache if existing search has enough tweets (200)
    if user.id in user_tweet_model_cache and user_tweet_model_cache[user.id][1] >= 200:
        print(f"Fetching tweet model from cache!")
        tweet_model = user_tweet_model_cache[user.id]
    else:
        tweets = tweepy.Paginator(
            client.get_users_tweets,
            id=user.id,
            exclude="retweets",
            max_results=100
        ).flatten()

        # Parse & build corpus
        tweets_sanitised = list()
        for i, tweet in enumerate(tweets):
            # Strip ending links
            san = re.sub(r"https.*", "", tweet.text)

            # Remove user tags
            while re.search(r"^@\w* ", san):
                san = re.sub(r"^@\w* ", "", san)

            # Append full stop
            if not san.endswith("."):
                san = san + "."

            tweets_sanitised.append(san)

        corpus = "\n".join(tweets_sanitised)

        # Train model
        tweet_model = (markovify.Text(corpus), len(tweets_sanitised))

        # Store in cache
        user_tweet_model_cache[user.id] = tweet_model

    # Generate sentences
    generated_tweets = list()
    for i in range(5):
        s = tweet_model[0].make_sentence()
        if any(t['text'] == s for t in generated_tweets):
            continue
        if not s or s in generated_tweets:
            continue
        generated_tweet = dict()
        generated_tweet["text"] = s
        generated_tweets.append(generated_tweet)

    return GenerateResponse(
        generated_tweets if generated_tweets else None,
        tweet_model[1]
    )
