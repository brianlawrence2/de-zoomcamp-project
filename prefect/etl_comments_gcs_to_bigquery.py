import json
import datetime
import pandas as pd

from io import BytesIO

from prefect import task, flow
from prefect_gcp import GcpCredentials, GcsBucket, BigQueryWarehouse

from google.cloud import storage

from utils import create_comment_dict

GCS_BUCKET_NAME = "reddit-data-lake-de-zoomcamp-project-384603"

@task(log_prints=True)
def extract_from_gcs() -> pd.DataFrame:
    gcp_credentials_block = GcpCredentials.load("de-zoomcamp-project-creds")
    gcs_bucket = GcsBucket(
        bucket=GCS_BUCKET_NAME,
        gcp_credentials=gcp_credentials_block,
    )
    for blob in gcs_bucket.list_blobs("comments"):
        print(blob.name)
        
@task(log_prints=True)
def get_processed_comments():
    with BigQueryWarehouse.load("de-zoomcamp-project-bq") as dw:
        operation = '''
            SELECT file_name
            FROM subreddit_posts.processed_comments
        '''
        results = dw.fetch_all(operation)
        
    return {result.file_name for result in results}
    
@task(log_prints=True)
def get_gcs_file_names():
    gcp_credentials_block = GcpCredentials.load("de-zoomcamp-project-creds")
    gcs_bucket = GcsBucket(
        bucket=GCS_BUCKET_NAME,
        gcp_credentials=gcp_credentials_block,
    )
        
    return {blob.name for blob in gcs_bucket.list_blobs("comments")}

@task(log_prints=True)
def extract_from_gcs(file_name):
    gcp_credentials_block = GcpCredentials.load("de-zoomcamp-project-creds")
    gcs_bucket = GcsBucket(
        bucket=GCS_BUCKET_NAME,
        gcp_credentials=gcp_credentials_block,
    )
    with BytesIO() as buf:
        gcs_bucket.download_object_to_file_object(file_name, buf)
        file = buf.getvalue().decode('UTF-8')
        print(file)
    comment = create_comment_dict(json.loads(file))
    return pd.DataFrame.from_dict(comment, orient='index').T
    
        
@task(log_prints=True)
def write_to_bq(df):
    print(f"Writing {df.id} to subreddit_posts.comments.")
    gcp_credentials_block = GcpCredentials.load("de-zoomcamp-project-creds")
    
    df = df.convert_dtypes()

    df.to_gbq(
        destination_table="subreddit_posts.comments",
        project_id="de-zoomcamp-project-384603",
        if_exists='append',
        credentials=gcp_credentials_block.get_credentials_from_service_account()
    )
    return df

@task(log_prints=True)
def log_progress_to_bq(bucket, file_name, df):
    print(f"Logging {file_name} to subreddit_posts.processed_comments.")
    gcp_credentials_block = GcpCredentials.load("de-zoomcamp-project-creds")
    df = pd.DataFrame({
        'bucket': bucket.name,
        'file_name': file_name,
        'comment_id': df.id,
        'processed_on': datetime.datetime.now()
    })
    
    df.to_gbq(
        destination_table="subreddit_posts.processed_comments",
        project_id="de-zoomcamp-project-384603",
        if_exists='append',
        credentials=gcp_credentials_block.get_credentials_from_service_account()
    )

@flow(log_prints=True)
def etl_gcs_to_bigquery():
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    
    processed = get_processed_comments()
    file_names = get_gcs_file_names()
    files_to_process = file_names - processed
    
    for file_name in files_to_process:
        df = extract_from_gcs(file_name)
        df = write_to_bq(df)
        log_progress_to_bq(bucket, file_name, df)
        print(df)
    #df = extract_from_gcs()
    
if __name__ == '__main__':
    etl_gcs_to_bigquery()