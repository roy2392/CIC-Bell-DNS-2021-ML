import os
import boto3
import pandas as pd
import csv
from io import StringIO
from dotenv import load_dotenv

# Define paths
RAW_DATA_DIR = 'data/raw'
PROCESSED_DATA_DIR = 'data/processed'

# Create directories if they don't exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Load environment variables from .env file
load_dotenv()

# Access the variables
bucket_name = os.getenv('S3_BUCKET_NAME')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_DEFAULT_REGION')

# Initialize S3 client with credentials
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

file_keys = {
    'malware': 'CSV_malware.csv',
    'phishing': 'CSV_phishing.csv',
    'spam': 'CSV_spam.csv',
    'benign': 'CSV_benign.csv'
}

# Download files from S3 and save them in data/raw directory
for key, filename in file_keys.items():
    try:
        s3.download_file(bucket_name, filename, os.path.join(RAW_DATA_DIR, filename))
        print(f"Downloaded {filename} from S3 bucket {bucket_name}.")
    except Exception as e:
        print(f"Error downloading {filename} from S3: {e}")

# Define the process_csv function
def process_csv(file_path):
    # Initialize StringIO to hold the processed content
    converted = StringIO()

    # Read the file and replace characters
    with open(file_path, encoding="utf8") as file:
        converted.write(
            file.read()
                .replace('[', ';[')  # Handling lists in the data
                .replace(']', '];')
                .replace('days,', 'days')  # Fixing date formats
                .replace('defaultdict(<class \'int\'>,', ';')  # Handling defaultdict structures
                .replace('})', '};')
        )

    # Reset the cursor of the StringIO object
    converted.seek(0)

    # Read the processed content into a DataFrame
    reader = csv.reader(converted, quotechar=';', delimiter=',')
    df = pd.DataFrame(reader)

    # Set the first row as the header
    df.columns = df.iloc[0]  # Set the first row as column names
    df = df[1:]  # Take the data less the header row

    # Reset index and ensure column types are handled correctly
    df.reset_index(drop=True, inplace=True)

    # Convert columns to appropriate data types if necessary
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])  # Convert numeric columns where possible
        except (ValueError, TypeError):
            continue  # Skip columns that cannot be converted

    # Handle date-time conversion with specified format
    if 'Creation_Date_Time' in df.columns:
        try:
            df['Creation_Date_Time'] = pd.to_datetime(df['Creation_Date_Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        except (ValueError, TypeError):
            pass

    return df

# Define the realign_and_clean function
def realign_and_clean(df):
    # Manually realign the columns based on the observation
    df['Creation_Date_Time'] = df['numeric_percentage']
    df['numeric_percentage'] = df['Emails']
    df['Emails'] = df['2gram']
    df['2gram'] = df['entropy']
    df['entropy'] = df['Domain_Age']
    df['Domain_Age'] = df['Domain_Name']
    df['Domain_Name'] = df[df.columns[-3]]  # Take the second last 'None' column

    # Drop the extra columns (those labeled as None)
    df = df.drop(columns=df.columns[-3:])

    return df

# Process each CSV file and save the processed files
for key, filename in file_keys.items():
    raw_file_path = os.path.join(RAW_DATA_DIR, filename)
    processed_file_path = os.path.join(PROCESSED_DATA_DIR, f"processed_{filename}")
    
    # Process the CSV file
    df = process_csv(raw_file_path)
    
    # If the file is the spam dataset, realign and clean it
    if key == 'spam':
        df = realign_and_clean(df)
    
    # Save the processed DataFrame to the processed directory
    df.to_csv(processed_file_path, index=False)

    print(f"{filename} has been processed and saved to {processed_file_path}")