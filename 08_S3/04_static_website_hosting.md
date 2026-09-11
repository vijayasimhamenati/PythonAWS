# Amazon S3: Static Website Hosting

You do not always need a fleet of EC2 instances and an Apache or Nginx web server to host a website. If your website consists solely of static files—like HTML, CSS, JavaScript, and images—you can host it directly on Amazon S3.

This is incredibly cost-effective, highly available by default, and removes the burden of managing and patching server operating systems.

---

## 1. The S3 Website Endpoint

When you enable Static Website Hosting on a bucket, AWS provisions a special website endpoint for it. This is a unique URL separate from the standard S3 Object URL.

Depending on the region, the URL format will look like one of these:

* `http://<bucket-name>.s3-website-<region>.amazonaws.com` (Dash format)
* `http://<bucket-name>.s3-website.<region>.amazonaws.com` (Dot format)

*Note: S3 Website endpoints do not support HTTPS natively. If you need HTTPS (and a custom domain name), you must place Amazon CloudFront in front of the S3 bucket.*

## 2. The "403 Forbidden" Trap

Enabling the Static Website Hosting feature does **not** automatically make your files public.

If you configure the bucket for website hosting but forget to update the security settings, navigating to your website endpoint will result in a **403 Forbidden** XML error.

To host a website, you *must* perform the steps from the previous lecture:

1. Turn off **Block Public Access**.
2. Attach a **Bucket Policy** that explicitly allows `s3:GetObject` for `Principal: "*"`.

---

## 3. Practical Guide: Enabling Static Website Hosting

Let's transform a standard bucket into a functional web server.

### A. Prepare the Files

1. Ensure you have an `index.html` file ready on your local machine (e.g., a simple file containing `<h1>Hello World! I love coffee.</h1>`).
2. Navigate to your S3 bucket in the AWS Console.
3. Upload the `index.html` file (and any related image files, like the `beach.jpg` mentioned in the lecture) to the root of your bucket.

### B. Configure Website Hosting

1. Click on the **Properties** tab of your bucket.
2. Scroll all the way down to the bottom to the **Static website hosting** section.
3. Click **Edit**.
4. **Static website hosting:** Select **Enable**.
5. **Hosting type:** Select **Host a static website**.
6. **Index document:** Type exactly `index.html`. (This tells S3 which file to serve by default when a user hits the root URL, similar to how Apache handles index files).
7. Click **Save changes**.

### C. Test the Website

1. Scroll back down to the **Static website hosting** section.
2. You will now see a **Bucket website endpoint** link.
3. Click this URL.

**Success!** Your browser will render the HTML file perfectly. Because the bucket policy allows public reads, any images referenced in your HTML file will also load correctly.

---

## 4. Boto3 Implementation

If you want to automate this process, here is a concise, simplified `boto3` script that isolates the exact API calls needed to enable static website hosting on an existing bucket.

```python
import boto3
import json

# Define variables
region = 'eu-west-1'
bucket_name = 'stephane-demo-s3-v12-random123'
index_file = 'index.html'

s3_client = boto3.client('s3', region_name=region)

print(f"Configuring {bucket_name} for Static Website Hosting...")

# 1. Enable Static Website Hosting
s3_client.put_bucket_website(
    Bucket=bucket_name,
    WebsiteConfiguration={
        'IndexDocument': {
            'Suffix': index_file
        }
    }
)
print("✅ Website endpoint enabled!")

# 2. Lower the "Block Public Access" Shield
s3_client.put_public_access_block(
    Bucket=bucket_name,
    PublicAccessBlockConfiguration={
        'BlockPublicAcls': False,
        'IgnorePublicAcls': False,
        'BlockPublicPolicy': False,
        'RestrictPublicBuckets': False
    }
)
print("🔓 Block Public Access disabled.")

# 3. Apply the Public Read Bucket Policy
bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }
    ]
}

s3_client.put_bucket_policy(
    Bucket=bucket_name,
    Policy=json.dumps(bucket_policy)
)
print("🌐 Public read Bucket Policy applied.")

# Output the final Website URL (Dash format)
website_url = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
print(f"\n🚀 Your website is live at:\n{website_url}")

```
