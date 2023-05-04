import praw
import json
from datetime import datetime

from praw.models.reddit.comment import Comment
from praw.models.reddit.submission import Submission

from google.cloud import storage, secretmanager_v1

from encoders import RedditEncoder

COMMENT_TOPIC = 'comment-topic'
SUBMISSOIN_TOPIC = 'submission-topic'
PROJECT = 'de-zoomcamp-project-384603'
REDDIT_USER_AGENT = 'cfb_bot by u/importantbrian'
DATA_LAKE_BUCKET = 'reddit-data-lake-de-zoomcamp-project-384603'

client = secretmanager_v1.SecretManagerServiceClient()

secret_names = [
    'projects/1015405245642/secrets/REDDIT_CLIENT_ID/versions/latest',
    'projects/1015405245642/secrets/REDDIT_CLIENT_SECRET/versions/latest'
]

secrets = {}
for name in secret_names:
    response = client.access_secret_version(request={'name': name})
    secret_string = response.payload.data.decode('UTF-8')
    secrets[name] = secret_string

reddit = praw.Reddit(
    client_id=secrets['projects/1015405245642/secrets/REDDIT_CLIENT_ID/versions/latest'],
    client_secret=secrets['projects/1015405245642/secrets/REDDIT_CLIENT_SECRET/versions/latest'],
    user_agent=REDDIT_USER_AGENT
)

def submissions_and_comments(subreddit, **kwargs):
    results=[]
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results

def write_to_gcs(data, bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(DATA_LAKE_BUCKET)
    file_name = f'{bucket_name}/{bucket_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    blob = bucket.blob(file_name)
    blob.upload_from_string(data)  

def push_post(post, bucket_name):
    data = json.dumps(post, cls=RedditEncoder).encode('utf-8')
    write_to_gcs(data, bucket_name)

subreddit = reddit.subreddit("CFB")
stream = praw.models.util.stream_generator(lambda **kwargs: submissions_and_comments(subreddit, **kwargs))

comment_buffer = []
submission_buffer = []

for post in stream:
    if post is None and comment_buffer:
        push_post(comment_buffer, 'comments')
        comment_buffer = []
    
    if post is None and submission_buffer:
        push_post(submission_buffer, 'submissions')
        submission_buffer = []
        
    if isinstance(post, Comment):
        comment_buffer.append()
    if isinstance(post, Submission):
        submission_buffer.append()