import os
import praw

from praw.models.reddit.comment import Comment
from praw.models.reddit.submission import Submission

from dotenv import load_dotenv

load_dotenv(".env")

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

def submissions_and_comments(subreddit, **kwargs):
    results=[]
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results

subreddit = reddit.subreddit("CFB")
stream = praw.models.util.stream_generator(lambda **kwargs: submissions_and_comments(subreddit, **kwargs))

for post in stream:
    if isinstance(post, Comment):
        print(post.author)
    if isinstance(post, Submission):
        print(post.title)