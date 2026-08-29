# Amazon S3: Core Concepts & Practical Guide

Amazon Simple Storage Service (S3) is one of the oldest, most foundational, and most widely used services in AWS. It provides infinitely scalable, highly durable object storage.

Unlike block storage (EBS) which functions like a hard drive attached to a server, or file storage (EFS) which functions like a shared network drive, S3 is **Object Storage**. You store files (objects) inside containers (buckets), and access them over the network via HTTP APIs.

---

## 1. Buckets & The Global Namespace Rule

To store files in S3, you must first create a **Bucket**.

- A bucket is a logical container for your objects.
- Buckets must be created in a specific AWS Region (e.g., `us-east-1` or `eu-west-1`), but the S3 service console provides a global view of all buckets across all regions.

### The Naming Challenge

Historically, the most famous rule in S3 is that **Bucket names must be globally unique across all AWS accounts.**

If someone, anywhere in the world, has created an S3 bucket named `test` or `my-demo-bucket`, you cannot use that name.

### Global vs. Account Regional Namespace

To solve the friction of finding a globally unique name, AWS recently introduced a dual-namespace model:

1. **Global Namespace (Legacy/Standard):** You must provide a highly specific, globally unique name (e.g., `stephane-demo-s3-v12`).
2. **Account Regional Namespace (Modern):** You can use simple, generic names (like `test` or `images`). AWS automatically appends a unique suffix containing your AWS Account ID and Region code to ensure global uniqueness (e.g., `test--usw2-az1--x-s3`). This is the recommended approach for modern architectures to avoid naming collisions.

---

## 2. Security Defaults: Block Public Access

When you create a bucket, AWS now heavily prioritizes security by default.

- **Block Public Access:** This setting is enabled by default on all new buckets. It ensures that no objects within the bucket can be accessed anonymously via the public internet, regardless of individual file permissions.
- **Default Encryption:** AWS now automatically encrypts all new objects uploaded to an S3 bucket using Server-Side Encryption with Amazon S3 Managed Keys (SSE-S3). You do not have to configure this manually; data is secure at rest by default.

---

## 3. Objects, Folders, and Keys

Once a bucket is created, you upload **Objects** (files) into it.

- **Keys (The "Path"):** An object's Key is its full path within the bucket. For example, if you upload `beach.jpg` into a folder named `images`, the Object Key is literally `images/beach.jpg`.
- **The Folder Illusion:** S3 has a flat architectural structure. It does not actually have directories or folders. When you create a "folder" named `images/` in the UI, S3 is simply creating a zero-byte object with the key `images/`. The console UI interprets the forward slashes (`/`) to visually render a folder structure for your convenience.

---

## 4. Accessing Objects: Public URLs vs Pre-Signed URLs

Every object in S3 is assigned a standard HTTP URL (e.g., `[https://stephane-demo-s3-v12.s3.eu-west-1.amazonaws.com/coffee.jpg](https://stephane-demo-s3-v12.s3.eu-west-1.amazonaws.com/coffee.jpg)`).

However, if you attempt to copy that URL and paste it into a new browser tab, you will likely receive an `AccessDenied` XML error. Why? Because the bucket has **Block Public Access** enabled. Anonymous internet users cannot view your files.

**How do you view your own files securely?**
When you click the "Open" button inside the AWS Console, AWS does not use the standard public URL. Instead, it generates a **Pre-Signed URL**.

- **Pre-Signed URLs:** This is a temporary URL that contains a cryptographic signature embedding your specific IAM credentials.
- It temporarily grants whoever holds the URL the exact same permissions that _you_ have, but only for a limited timeframe (e.g., 5 minutes).
- This allows you to securely view the image in your browser without making the bucket public to the world.

---

## Interview Preparation: S3 Basics

### Summary

Understand the global nature of bucket naming, the fact that S3 is a flat object store (no real folders), and the critical difference between a static public URL and a Pre-Signed URL.

### Q&A Details

**Q1: A junior developer attempts to create an S3 bucket named `website-assets` in the `us-east-1` region but receives an error stating the bucket name already exists. The developer checks the company's AWS account and confirms no such bucket exists. What is the problem?**
**Answer:** The standard S3 Global Namespace requires bucket names to be unique across _all_ AWS accounts globally, not just within the user's specific account. Someone else in the world has already claimed the name `website-assets`. The developer should either append a unique identifier (like a company name) or utilize the new Account Regional Namespace to bypass global naming collisions.

**Q2: We have an S3 bucket configured with 'Block Public Access' enabled to protect sensitive reports. We need to temporarily allow an external auditor to download a specific PDF report from the bucket for the next 24 hours without creating an IAM user for them. How can we achieve this securely?**
**Answer:** You should generate a **Pre-Signed URL** for the specific PDF object and set the expiration time to 24 hours. The auditor can use this temporary URL to download the file directly from S3 using their web browser. Once the 24 hours pass, the signature expires and the link becomes invalid, maintaining the strict security posture of the bucket.

**Q3: A developer asks you to write a script to recursively delete all the nested subdirectories inside an S3 bucket. How does S3 handle directories and subdirectories internally?**
**Answer:** Internally, S3 does not have directories or subdirectories; it uses a flat namespace. What appears as a folder structure in the AWS Console is simply a visual abstraction based on the forward slash (`/`) characters in the object's Key (its full name/path). To "delete a directory," the script must actually find and delete all objects whose keys share that specific prefix.

---

### Prerequisites for Hands-on

Make sure you have `boto3` installed (`pip install boto3`) and your AWS credentials configured (via `aws configure`), and create a dummy file named `coffee.jpg` in the same directory as this script.

### The Boto3 Script

```python
import boto3

# Define your variables
region = 'eu-west-1'
# Remember: This must be globally unique! Change 'v12' to something random.
bucket_name = 'stephane-demo-s3-v12-random123'
local_file = 'coffee.jpg'
s3_key = 'images/coffee.jpg' # The '/' creates the illusion of a folder

# 1. Initialize the S3 Client
s3_client = boto3.client('s3', region_name=region)

# 2. Create the Bucket
print(f"Creating bucket: {bucket_name}...")
# Note: AWS requires a LocationConstraint for all regions except us-east-1
s3_client.create_bucket(
    Bucket=bucket_name,
    CreateBucketConfiguration={
        'LocationConstraint': region
    }
)
print("✅ Bucket created!")

# 3. Upload the Object
print(f"Uploading {local_file} to {s3_key}...")
s3_client.upload_file(local_file, bucket_name, s3_key)
print("✅ Upload complete!")

# 4. Generate a Pre-Signed URL
print("Generating pre-signed URL...")
presigned_url = s3_client.generate_presigned_url(
    ClientMethod='get_object',
    Params={
        'Bucket': bucket_name,
        'Key': s3_key
    },
    ExpiresIn=300  # Link expires in 5 minutes (300 seconds)
)

print("\n🔒 Here is your secure, temporary access link:")
print(presigned_url)

```

### What this script does:

1. **Client Initialization:** Connects to AWS using your local credentials and targets the `eu-west-1` region.
2. **Bucket Creation:** Notice the `LocationConstraint` block. S3 has a quirk where creating a bucket in `us-east-1` requires a different API call than the rest of the world. The configuration block is required for `eu-west-1`.
3. **Upload & Folders:** The `upload_file` method handles the transfer. By setting the key to `images/coffee.jpg`, S3 will automatically render an `images` folder in the AWS Console.
4. **Pre-Signed URL:** Generates a temporary URL embedding your IAM credentials, allowing you to view the private file in your browser without changing the bucket's public access settings.
