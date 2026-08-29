import boto3
from botocore.exceptions import ClientError

def initialize_and_list():
    # Explicit session definition is an industry best practice
    session = boto3.Session(profile_name='default')
    
    # Initialize the low-level client
    s3_client = session.client('s3')
    
    try:
        # The Client interface always returns standard Python dictionaries
        response = s3_client.list_buckets()
        print("Your Active S3 Buckets:")

        # print(response)
        
        for bucket in response.get('Buckets', []):
            print(f"- {bucket['Name']}")
            
    except ClientError as e:
        print(f"AWS API Error: {e}")

if __name__ == '__main__':
    initialize_and_list()