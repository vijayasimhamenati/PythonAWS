# Automated S3 Static Website Deployment

## 1. Project Introduction

This project automates the provisioning and deployment of a static website on Amazon S3 using Python and the `boto3` SDK. Instead of relying on manual configurations within the AWS Management Console, this script handles infrastructure creation, security policy application, static hosting configuration, and automated file uploads. It is designed to be idempotent and production-ready, featuring dynamic MIME-type resolution and robust error handling.

---

## 2. Core Concepts Used

- **Infrastructure as Code (IaC):** The practice of provisioning and managing cloud resources through code or scripts rather than manual interactive tools.
- **AWS Boto3 SDK:** The official Amazon Web Services SDK for Python, allowing developers to write software that interacts with AWS services.
- **Static Website Hosting:** An S3 feature that allows a bucket to serve static web content (HTML, CSS, JS, images) natively over HTTP, bypassing the need for a backend web server.
- **Bucket Policies & Public Access:** JSON-based permission rules attached to an S3 bucket. To serve a public website, AWS's default "Block Public Access" guardrails must be explicitly disabled, and a policy granting `s3:GetObject` to `*` (everyone) must be applied.
- **MIME Types (Content-Type):** Standardized file identifiers. When uploading files programmatically to S3, setting the correct `Content-Type` metadata (e.g., `text/html` or `text/css`) is critical; otherwise, web browsers will force users to download the files rather than displaying them.

---

## 3. Instructions to Perform

### Prerequisites

1.  **Python 3.x:** Ensure Python is installed on your local machine.
2.  **Boto3 Installation:** Run `pip install boto3` in your terminal.
3.  **AWS CLI Configured:** You must have the AWS CLI installed and configured with your IAM credentials. Run `aws configure` and input your Access Key, Secret Key, and default region. Ensure this IAM user has `AmazonS3FullAccess`.

### Execution Steps

1.  Clone this repository or place the `deploy_portfolio.py` script in your project root.
2.  Ensure your website files (`index.html`, `style.css`, etc.) are located in a folder named `src/` in the same directory as the script.
3.  Open `deploy_portfolio.py` and modify the `TARGET_BUCKET_NAME` variable to a globally unique name.
4.  Run the script via your terminal: `python deploy_portfolio.py`.
5.  Check the terminal output for success logs and click the provided endpoint URL to view your live website.

---

## 4. Interview Questions & Study Guide

**Q: How do you use Boto3 to interact with AWS S3, and how are credentials managed?**

- **Answer:** You install Boto3 via pip and create a client or resource object in your Python script. Credentials should never be hardcoded; instead, Boto3 automatically looks for them in the `~/.aws/credentials` file configured by the AWS CLI, or through environment variables like `AWS_ACCESS_KEY_ID`.

**Q: What are the exact requirements to make an S3 bucket serve a public website?**

- **Answer:** You must enable the "Static Website Hosting" property on the bucket. Additionally, you must turn off the "Block Public Access" settings and attach a bucket policy that grants `s3:GetObject` permissions to a wildcard principal (`*`).

**Q: When uploading a static website to S3 via Boto3, why might HTML files trigger a download prompt instead of opening in the browser?**

- **Answer:** By default, if a `Content-Type` is not specified during a programmatic upload, S3 assigns it a default binary type (`binary/octet-stream`). You must programmatically detect and inject the correct MIME type (e.g., `text/html`) into the `ExtraArgs` parameter during the upload.

**Q: What is the maximum size of an object you can store in an S3 bucket?**

- **Answer:** The maximum size for a single S3 object is 5 TB. However, any single file larger than 5 GB requires the use of the S3 Multipart Upload API.

**Q: How do you handle exceptions in Boto3, for instance, if you try to create a bucket name that someone else is already using?**

- **Answer:** Boto3 utilizes built-in Python exception handling methods. You wrap your API call in a `try/except` block, catch the `ClientError` from `botocore.exceptions`, and extract the error code (such as `BucketAlreadyExists`) to print a graceful warning rather than crashing the script.
