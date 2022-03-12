import os
import tweepy
import re
import markovify
import logging

logger = logging.getLogger(__name__)

user_cache = dict()
user_tweet_model_cache = dict()

client = tweepy.Client(os.environ["TWITTER_BEARER_TOKEN"])


class GenerateResponse:

    def __init__(self, tweets, model_tweet_count, user):
        self.tweets = tweets
        self.model_tweet_count = model_tweet_count
        self.user = user


def fetch_user(username):
    """
    Returns twitter user with format:
      <User id=44196397 name=Elon Musk username=elonmusk>
    Or None if not found.
    """
    # Standardise username format - tweeter is case-insensitive
    username = username.lower()
    if username in user_cache:
        logger.info(f"Fetching {username} from cache")
        return user_cache[username]

    logger.info(f"Fetching user {username} from Twitter")
    user = client.get_user(username=username).data

    # Store in cache
    user_cache[username] = user
    return user


def generate(username):
    """
    Returns generated tweets along with meta data on model run with format:
      <GenerateResponse tweets=["hi"] model_tweet_count=200 user=User>
    """
    user = fetch_user(username)

    # Only fetch from cache if existing search has enough tweets (200)
    if user.id in user_tweet_model_cache and user_tweet_model_cache[user.id][1] >= 200:
        logger.info(f"Fetching tweet model from cache")
        tweet_model = user_tweet_model_cache[user.id]
    else:
        logger.info(f"Fetching {username} user tweets from Twitter")
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
            while re.search(r"@\w+", san):
                san = re.sub(r"@\w+", "", san)

            # Strip whitespace & replace ampersand
            san = san.strip()
            san = san.replace("&amp;", "&")

            # Skip if we're not left with anything useful
            if not san or not re.search(r"\w", san):
                continue

            # Append full stop
            if not san.endswith((".", "!", "?")):
                san = san + "."

            tweets_sanitised.append(san)

        corpus = "\n".join(tweets_sanitised)

        # Train model
        try:
            logger.info(f"Generating Markov model for {username} using {len(tweets_sanitised)} tweets")
            markov_model = markovify.Text(corpus)
            tweet_model = (markov_model, len(tweets_sanitised), user)
        except Exception as e:
            logger.info(f"Failed to generate Markov model for {username} using {len(tweets_sanitised)} tweets")
            return GenerateResponse(None, len(tweets_sanitised), user)

        # Store in cache
        user_tweet_model_cache[user.id] = tweet_model

    # Generate sentences
    generated_tweets = list()
    for i in range(3):
        s = tweet_model[0].make_sentence()
        if not s or s in generated_tweets:
            continue
        generated_tweets.append(s)

    return GenerateResponse(
        generated_tweets if generated_tweets else None,
        tweet_model[1],
        tweet_model[2]
    )
