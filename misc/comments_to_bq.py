from google.cloud import storage

# Authenticate and connect to the Google Cloud Storage client
client = storage.Client()

# Specify the source bucket and prefix
bucket_name = 'reddit-data-lake-de-zoomcamp-project-384603'
prefix = 'comments/'

# Define the maximum number of files per subfolder
max_files_per_subfolder = 10000

# List all objects within the bucket
bucket = client.get_bucket(bucket_name)
blobs = bucket.list_blobs(prefix=prefix)

# Create subfolders and move files
current_subfolder = 1
file_counter = 0

for blob in blobs:
    file_counter += 1
    
    # Extract the file name and creation date
    file_name = blob.name
    creation_date = blob.time_created.strftime('%Y-%m-%d')
    
    # Create the subfolder if necessary
    subfolder_name = f'subfolder_{current_subfolder}'
    subfolder_path = f'{prefix}{creation_date}/{subfolder_name}/'
    subfolder = bucket.blob(subfolder_path)
    
    if file_counter == 1 or (file_counter - 1) % max_files_per_subfolder == 0:
        subfolder.upload_from_string('')
        print(f'Created subfolder: {subfolder_path}')
    
    # Move the file to the appropriate subfolder
    destination_blob = bucket.rename_blob(blob, f'{subfolder_path}{file_name}')
    print(f'Moved file: {blob.name} -> {destination_blob.name}')
    
    # Move to the next subfolder if the maximum number of files is reached
    if file_counter % max_files_per_subfolder == 0:
        current_subfolder += 1

print('Organizing files into subfolders completed.')
