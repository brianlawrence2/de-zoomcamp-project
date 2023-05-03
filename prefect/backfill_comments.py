import json
import datetime

import pandas as pd

from prefect import task, flow

from google.cloud import storage
from google.cloud import bigquery

from utils import create_comment_dict

GCS_BUCKET = "reddit-data-lake-de-zoomcamp-project-384603"
COMMENTS_FOLDER = f"comments"

@task(log_prints=True)
def get_blobs(bucket):
    print("Getting bucket list.")
    blobs = list(bucket.list_blobs(prefix=COMMENTS_FOLDER))
    return blobs

@task(log_prints=True)
def extract_from_gcs(bucket, blob):
    print(f"Extracting {blob.name} from GCS.")
    blob = bucket.blob(blob.name)
    comment = create_comment_dict(json.loads(blob.download_as_string()))
    return pd.DataFrame.from_dict(comment, orient='index').T

@task(log_prints=True)
def write_to_bq(df):
    print(f"Writing {df.id} to subreddit_posts.comments.")
    
    df = df.convert_dtypes()

    df.to_gbq(
        destination_table="subreddit_posts.comments",
        project_id="de-zoomcamp-project-384603",
        if_exists='append'
    )
    return df

@task(log_prints=True)
def log_progress_to_bq(bucket, blob, df):
    print(f"Logging {blob.name} to subreddit_posts.processed_comments.")
    df = pd.DataFrame({
        'bucket': bucket.name,
        'file_name': blob.name,
        'comment_id': df.id,
        'processed_on': datetime.datetime.now()
    })
    
    df.to_gbq(
        destination_table="subreddit_posts.processed_comments",
        project_id="de-zoomcamp-project-384603",
        if_exists='append'
    )

@flow(log_prints=True)
def backfill_comments():
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET)
    
    blobs = get_blobs(bucket)
    for blob in blobs:
        print(f"Processing: {blob.name}")
        df = extract_from_gcs(bucket, blob)
        df = write_to_bq(df)
        log_progress_to_bq(bucket, blob, df)
        

if __name__ == '__main__':
    backfill_comments()