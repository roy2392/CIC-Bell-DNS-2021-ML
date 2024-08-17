# impoprt necessary libraries
import os
import boto3
import pandas as pd
import csv
from io import StringIO
from dotenv import load_dotenv
import warnings

# suppress SyntaxWarnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

# define paths
RAW_DATA_DIR = 'data/raw'
PROCESSED_DATA_DIR = 'data/processed'

# create necessary directories if they don't exist
def create_directories():
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# load environment variables
def load_env_variables():
    load_dotenv()
    return {
        'bucket_name': os.getenv('S3_BUCKET_NAME'),
        'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
        'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'aws_region': os.getenv('AWS_DEFAULT_REGION')
    }

# initialize S3 client
def initialize_s3_client(aws_access_key_id, aws_secret_access_key, aws_region):
    """Initialize and return S3 client."""
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )
# download files from S3 bucket
def download_files_from_s3(s3, bucket_name, file_keys):
    """Download files from S3 bucket."""
    for key, filename in file_keys.items():
        try:
            s3.download_file(bucket_name, filename, os.path.join(RAW_DATA_DIR, filename))
            print(f"Downloaded {filename} from S3 bucket {bucket_name}.")
        except Exception as e:
            print(f"Error downloading {filename} from S3: {e}")

# parse and load CSV file
def parse_and_load_csv(file_path):
    """Parse the CSV file and return a DataFrame."""
    # Create a StringIO object to hold the converted content
    converted = StringIO()
    
    # read and replace specific patterns in the file
    with open(file_path, encoding="utf8") as file:
        converted.write(
            file.read()
            .replace('[', ';[')
            .replace(']', '];')
            .replace('days,', 'days')
            .replace('defaultdict(<class \'int\'>,', ';')
            .replace('})', '};')
        )
    
    # move the pointer back to the start of the StringIO object
    converted.seek(0)
    
    # read the content into a CSV reader, using ';' as the quote character
    reader = csv.reader(converted, quotechar=';')
    
    # load the reader's content into a df
    df = pd.DataFrame(reader)
    
    # set the 1st row as the header
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header
    return df

# process all CSV files
def process_files(file_keys):
    """Process all CSV files."""
    for key, filename in file_keys.items():
        raw_file_path = os.path.join(RAW_DATA_DIR, filename)
        processed_file_path = os.path.join(PROCESSED_DATA_DIR, f"processed_{filename}")
        
        # Parse the CSV and save the processed DataFrame
        df = parse_and_load_csv(raw_file_path)
        df.to_csv(processed_file_path, index=False)
        print(f"{filename} has been processed and saved to {processed_file_path}")
# main function
def main():
    create_directories()
    env_vars = load_env_variables()
    s3 = initialize_s3_client(env_vars['aws_access_key_id'], env_vars['aws_secret_access_key'], env_vars['aws_region'])
    
    file_keys = {
        'malware': 'CSV_malware.csv',
        'phishing': 'CSV_phishing.csv',
        'spam': 'CSV_spam.csv',
        'benign': 'CSV_benign.csv'
    }
    
    download_files_from_s3(s3, env_vars['bucket_name'], file_keys)
    process_files(file_keys)
    print("\nScript completed. Any SyntaxWarnings about invalid decimal literals were suppressed.")

if __name__ == "__main__":
    main()