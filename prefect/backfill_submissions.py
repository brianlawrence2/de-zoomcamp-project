import json
import datetime

import pandas as pd

from prefect import task, flow

from google.cloud import storage
from google.cloud import bigquery

from utils import create_submission_dict

GCS_BUCKET = "reddit-data-lake-de-zoomcamp-project-384603"
SUBMISSIONS_FOLDER = f"submissions"

@task(log_prints=True)
def get_blobs(bucket):
    print("Getting bucket list.")
    blobs = list(bucket.list_blobs(prefix=SUBMISSIONS_FOLDER))
    return blobs

@task(log_prints=True)
def extract_from_gcs(bucket, blob):
    print(f"Extracting {blob.name} from GCS.")
    blob = bucket.blob(blob.name)
    submission = create_submission_dict(json.loads(blob.download_as_string()))
    return pd.DataFrame.from_dict(submission, orient='index').T

@task(log_prints=True)
def write_to_bq(df):
    print(f"Writing {df.id} to subreddit_posts.submissions.")
    
    df = df.convert_dtypes()

    df.to_gbq(
        destination_table="subreddit_posts.submissions",
        project_id="de-zoomcamp-project-384603",
        if_exists='append'
    )
    return df

@task(log_prints=True)
def log_progress_to_bq(bucket, blob, df):
    print(f"Logging {blob.name} to subreddit_posts.processed_submissions.")
    df = pd.DataFrame({
        'bucket': bucket.name,
        'file_name': blob.name,
        'submission_id': df.id,
        'processed_on': datetime.datetime.now()
    })
    
    df.to_gbq(
        destination_table="subreddit_posts.processed_submissions",
        project_id="de-zoomcamp-project-384603",
        if_exists='append'
    )

@flow(log_prints=True)
def backfill_submissions():
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET)
    
    blobs = get_blobs(bucket)
    for blob in blobs:
        print(f"Processing: {blob.name}")
        df = extract_from_gcs(bucket, blob)
        df = write_to_bq(df)
        log_progress_to_bq(bucket, blob, df)
        

if __name__ == '__main__':
    backfill_submissions()