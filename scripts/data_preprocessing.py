import os
import boto3
import pandas as pd
import csv
from io import StringIO
from dotenv import load_dotenv
import ast
import re
import warnings

# Suppress SyntaxWarnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

# Define paths
RAW_DATA_DIR = 'data/raw'
PROCESSED_DATA_DIR = 'data/processed'

def create_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

def load_env_variables():
    """Load environment variables from .env file."""
    load_dotenv()
    return {
        'bucket_name': os.getenv('S3_BUCKET_NAME'),
        'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
        'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'aws_region': os.getenv('AWS_DEFAULT_REGION')
    }

def initialize_s3_client(aws_access_key_id, aws_secret_access_key, aws_region):
    """Initialize and return S3 client."""
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )

def download_files_from_s3(s3, bucket_name, file_keys):
    """Download files from S3 bucket."""
    for key, filename in file_keys.items():
        try:
            s3.download_file(bucket_name, filename, os.path.join(RAW_DATA_DIR, filename))
            print(f"Downloaded {filename} from S3 bucket {bucket_name}.")
        except Exception as e:
            print(f"Error downloading {filename} from S3: {e}")

def process_csv(file_path):
    """Process CSV files (except benign)."""
    converted = StringIO()
    with open(file_path, encoding="utf8") as file:
        converted.write(
            file.read()
                .replace('[', ';[')
                .replace(']', '];')
                .replace('days,', 'days')
                .replace('defaultdict(<class \'int\'>,', ';')
                .replace('})', '};')
        )
    converted.seek(0)
    reader = csv.reader(converted, quotechar=';', delimiter=',')
    df = pd.DataFrame(reader)
    df.columns = df.iloc[0]
    df = df[1:]
    df.reset_index(drop=True, inplace=True)
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            continue
    if 'Creation_Date_Time' in df.columns:
        try:
            df['Creation_Date_Time'] = pd.to_datetime(df['Creation_Date_Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        except (ValueError, TypeError):
            pass
    return df

def process_benign_csv(file_path):
    """Process benign CSV file."""
    def safe_eval(x):
        try:
            return ast.literal_eval(x)
        except (ValueError, SyntaxError):
            return x

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = re.sub(r"b'([^']*)'", r"'\1'", content)
    content = content.replace("defaultdict(<class 'int'>,", "{")
    content = content.replace("})", "}")
    content = content.replace("nan", "''")
    content = re.sub(r'(\d+) days, (\d+:\d+:\d+\.\d+)', r"'\1 days, \2'", content)
    
    reader = csv.reader(StringIO(content), quotechar="'", escapechar='\\')
    headers = next(reader)
    data = []
    for row in reader:
        padded_row = row + [''] * (len(headers) - len(row))
        padded_row = padded_row[:len(headers)]
        data.append(padded_row)
    
    df = pd.DataFrame(data, columns=headers)
    
    for col in df.columns:
        df[col] = df[col].apply(safe_eval)
    
    if 'Creation_Date_Time' in df.columns:
        df['Creation_Date_Time'] = pd.to_datetime(df['Creation_Date_Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    
    if 'Domain_Age' in df.columns:
        df['Domain_Age'] = pd.to_timedelta(df['Domain_Age'].fillna(''), errors='coerce')
    
    return df

def realign_and_clean(df):
    """Realign and clean spam dataset."""
    df['Creation_Date_Time'] = df['numeric_percentage']
    df['numeric_percentage'] = df['Emails']
    df['Emails'] = df['2gram']
    df['2gram'] = df['entropy']
    df['entropy'] = df['Domain_Age']
    df['Domain_Age'] = df['Domain_Name']
    df['Domain_Name'] = df[df.columns[-3]]
    df = df.drop(columns=df.columns[-3:])
    return df

def process_files(file_keys):
    """Process all CSV files."""
    for key, filename in file_keys.items():
        raw_file_path = os.path.join(RAW_DATA_DIR, filename)
        processed_file_path = os.path.join(PROCESSED_DATA_DIR, f"processed_{filename}")
        
        if key == 'benign':
            df = process_benign_csv(raw_file_path)
        else:
            df = process_csv(raw_file_path)
        
        if key == 'spam':
            df = realign_and_clean(df)
        
        df.to_csv(processed_file_path, index=False)
        print(f"{filename} has been processed and saved to {processed_file_path}")

def preview_benign_data():
    """Preview the processed benign data."""
    benign_file_path = os.path.join(PROCESSED_DATA_DIR, "processed_CSV_benign.csv")
    df_benign = pd.read_csv(benign_file_path)
    print("\nPreview of Benign data:")
    print(df_benign.head())
    print("\nDataFrame Info:")
    print(df_benign.info())

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
    preview_benign_data()
    
    print("\nScript completed. Any SyntaxWarnings about invalid decimal literals were suppressed.")

if __name__ == "__main__":
    main()