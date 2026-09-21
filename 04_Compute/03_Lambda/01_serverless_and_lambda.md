The shift to Serverless architecture is a major paradigm change. You no longer manage operating systems, patching, or scaling EC2 instances. Instead, you focus purely on your code and business logic.

**AWS Lambda** is the cornerstone of serverless compute on AWS. It allows you to run code without provisioning or managing servers. You pay only for the compute time you consume—there is no charge when your code is not running.

---

## 1. The Core Benefits of AWS Lambda

* **No Servers to Manage:** AWS handles all the infrastructure, operating system maintenance, and capacity provisioning.
* **Continuous Scaling:** Lambda automatically scales your application by running code in response to each trigger. If you have 100 requests, Lambda spins up 100 concurrent executions. If you have zero requests, it scales to zero.
* **Pay for Value:** You are charged based on the number of requests and the execution duration (measured in milliseconds). The generous free tier includes 1 million free requests per month.
* **Event-Driven:** Lambda is designed to be triggered by events from other AWS services.

---

## 2. Key Limitations and Constraints (Exam Focus)

While Lambda is powerful, it is not suitable for every workload. You must memorize these constraints:

* **Execution Timeout:** A Lambda function can run for a maximum of **15 minutes**. If your code takes longer (e.g., processing a massive video file or running a heavy machine learning model), Lambda will forcibly terminate it. You must use a different service like ECS/Fargate or EC2 for long-running tasks.
* **Resource Limits:** You can allocate up to 10 GB of RAM per function. *Note: CPU and network performance scale linearly with the amount of RAM you allocate.*
* **Deployment Package Size:** Your unzipped code and dependencies cannot exceed 250 MB.

---

## 3. Serverless CRON Jobs (A Classic Use Case)

In traditional architectures, if you need a script to run every Monday at 10:00 AM (a CRON job), you have to leave an EC2 instance running 24/7 just to execute that script once a week. This is a massive waste of money.

**The Serverless Solution:**

1. You write your script as an AWS Lambda function.
2. You use **Amazon EventBridge** (formerly CloudWatch Events) to create a scheduled rule using a standard CRON expression.
3. EventBridge triggers the Lambda function at the exact scheduled time.
4. The function executes, finishes in a few seconds, and shuts down. You only pay for those few seconds of compute time.

---

## 4. Lambda with Boto3 (Python)

When working with Lambda, you will frequently write your function logic in Python using the `boto3` library to interact with other AWS services.

### The Lambda Handler

Every Lambda function in Python requires a specific entry point called the **Handler function**. AWS passes two arguments to this function:

1. `event`: A dictionary containing all the data about the trigger (e.g., the S3 bucket name and file name, or the HTTP payload from API Gateway).
2. `context`: An object containing runtime information about the Lambda execution environment.

Here is a template of a simple Lambda function that could act as our CRON job:

```python
import boto3
import logging
from datetime import datetime

# Initialize clients outside the handler for connection reuse (best practice)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    This is the main entry point for the Lambda function.
    """
    logger.info(f"Received event: {event}")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Simulated CRON Job Logic
    try:
        logger.info(f"Executing scheduled cleanup task at {current_time}...")
        # For example, you might query a database here to delete expired records
        # or use s3_client to archive old logs.
        
        return {
            'statusCode': 200,
            'body': f'Scheduled task completed successfully at {current_time}'
        }
        
    except Exception as e:
        logger.error(f"Error executing scheduled task: {str(e)}")
        return {
            'statusCode': 500,
            'body': 'Internal Server Error'
        }

```

---

## Interview Preparation: AWS Lambda

### Summary

Focus on the 15-minute execution limit, the pay-per-use billing model, and common event-driven integration patterns (like S3 uploads triggering a Lambda function).

### Q&A Details

**Q1: A development team has an existing Python script that performs a complex machine learning data transformation. The script requires 8 GB of RAM and consistently takes 45 minutes to execute. Can this script be migrated to AWS Lambda to reduce costs?**
**Answer:** No. While AWS Lambda supports up to 10 GB of RAM, it has a strict maximum execution timeout of **15 minutes**. Because the script takes 45 minutes to run, Lambda will forcibly terminate it before it finishes. The team should look into using AWS Fargate (serverless containers) or AWS Batch for this long-running task.

**Q2: We need to build a system that automatically generates a thumbnail image every time a user uploads a high-resolution photo to an S3 bucket. How should we architect this using serverless technologies?**
**Answer:** You should configure an **Amazon S3 Event Notification** to trigger an **AWS Lambda** function upon the `s3:ObjectCreated` event. The Lambda function will receive the event payload containing the bucket name and the object key. The function can then use an image processing library to fetch the high-resolution photo, generate the thumbnail, and upload the thumbnail back to S3.

**Q3: Our company currently runs an EC2 instance 24/7. The only purpose of this instance is to execute a daily bash script at midnight that backs up our database. How can we optimize this architecture to save money?**
**Answer:** This is a perfect use case for a **Serverless CRON Job**. You should rewrite the backup script (e.g., in Python or Node.js) and deploy it as an **AWS Lambda function**. Then, use **Amazon EventBridge** to create a scheduled rule that triggers the Lambda function every night at midnight. You will eliminate the continuous EC2 hourly charges and only pay for the few seconds the Lambda function runs each day.