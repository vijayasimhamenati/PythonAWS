import boto3

# Define your variables
region = 'ap-south-2'
# Remember: This must be globally unique! Change 'v12' to something random.
bucket_name = 'demo-mybucket-vijayasimhamenati03' 
local_file = './assets/coffee.jpg'
s3_key = 'images/coffee.jpg' # The '/' creates the illusion of a folder

s3_client = boto3.client('s3') # 1. Initialize the S3 Client

# 2. Create the Bucket
print(f"Creating bucket: {bucket_name}...")
# Note: AWS requires a LocationConstraint for all regions except us-east-1
response = s3_client.create_bucket(
    Bucket=bucket_name,
    CreateBucketConfiguration={
        'LocationConstraint': region
    }
)
print("✅ Bucket created!")
print(response)

print("Uploading a object to the bucket")

response = s3_client.upload_file(local_file,bucket_name,s3_key)

print(response)

print("Generating pre-signed URL...")

presigned_url = s3_client.generate_presigned_url(
    ClientMethod='get_object',
    Params={
        'Bucket': bucket_name,
        'Key': s3_key
    },
    ExpiresIn=300  # Link expires in 5 minutes (300 seconds)
)
print(presigned_url)