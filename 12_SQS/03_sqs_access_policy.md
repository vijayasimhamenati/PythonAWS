# AWS SQS Access Policies: Resource-Based Security

In AWS, security is typically handled by assigning IAM Policies to identities (users, groups, or roles). However, certain services—like S3 and SQS—also support **Resource-Based Policies**.

An SQS Access Policy is a JSON document attached directly to the queue itself. It defines who (or what) is allowed to send or receive messages, regardless of what the sender's personal IAM policy says.

---

## 1. Primary Use Cases for SQS Access Policies

There are two major scenarios where an SQS Access Policy is absolutely required. These are heavily tested on AWS certification exams.

### A. Cross-Account Access

If an EC2 instance running in AWS Account A needs to pull messages from an SQS queue located in AWS Account B, IAM policies alone are not enough.

Because IAM policies cannot cross account boundaries by default, the administrator of Account B must attach a Resource-Based Policy to the SQS queue explicitly granting the `sqs:ReceiveMessage` action to the Principal (Account ID) of Account A.

### B. AWS Service Integration (e.g., S3 Event Notifications)

When a user uploads a video file to an Amazon S3 bucket, S3 can automatically send a notification message to an SQS queue, triggering a backend worker to process the video.

However, the S3 service does not have IAM user credentials. It operates as an AWS service principal. Therefore, the SQS queue **must** have an Access Policy attached that explicitly grants the `s3.amazonaws.com` service the `sqs:SendMessage` permission, but only if the message originates from your specific bucket ARN.

---

## 2. Practical Guide: S3 to SQS Integration

In this hands-on lab, we will configure an S3 bucket to automatically send a message to an SQS queue every time a new file is uploaded.

### Step 1: Create the Queue & S3 Bucket

1. **Create Queue:** In the SQS console, create a standard queue named `EventFromS3`. Leave all settings as default and copy its ARN to your clipboard.
2. **Create Bucket:** In the S3 console, create a new bucket (e.g., `s3-sqs-event-demo-12345`).

### Step 2: Update the SQS Access Policy

We must tell the queue to accept messages from the S3 bucket.

1. Navigate to your `EventFromS3` queue in the SQS console.
2. Go to the **Access policy** tab and click **Edit**.
3. Replace the default JSON with the following policy (ensure you replace the placeholders with your actual Queue ARN, Bucket Name, and Account ID):

```json
{
  "Version": "2012-10-17",
  "Id": "S3-to-SQS-Policy",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "sqs:SendMessage",
      "Resource": "arn:aws:sqs:us-east-1:123456789012:EventFromS3",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "123456789012"
        },
        "ArnLike": {
          "aws:SourceArn": "arn:aws:s3:::s3-sqs-event-demo-12345"
        }
      }
    }
  ]
}
```

_Security Note:_ The `Condition` block is critical. Without it, _any_ S3 bucket in the world could spam your queue with messages. The condition ensures the queue only accepts messages triggered by _your_ specific bucket in _your_ account.

### Step 3: Configure the S3 Event Notification

Now we tell S3 to send the message.

1. Navigate to your S3 bucket in the console.
2. Click the **Properties** tab.
3. Scroll down to **Event notifications** and click **Create event notification**.
4. **Name:** `NewObjectUploads`
5. **Event types:** Check the box for **All object create events**.
6. **Destination:** Select **SQS queue**.
7. Choose your `EventFromS3` queue from the dropdown.
8. Click **Save changes**.

- _(Note: If you get a validation error here, it means your SQS Access Policy from Step 2 was configured incorrectly, and S3 was denied permission to test the connection)._

### Step 4: Test the Integration

1. Upload any file (e.g., a `.txt` or `.jpg` file) into your S3 bucket.
2. Navigate to your `EventFromS3` queue in the SQS console.
3. Click **Send and receive messages** and then **Poll for messages**.
4. You will see a new message in the queue! If you open its details, the JSON body will contain all the metadata about the file you just uploaded to S3.

---

## Interview Preparation: SQS Security & Integration

### Summary

Expect questions on how to architect cross-account messaging and how to troubleshoot failed S3 event notifications by diagnosing Resource-Based Policy errors.

### Q&A Details

**Q1: We have an EC2 Auto Scaling Group in our primary AWS Account (`Account A`) that needs to pull messages from an SQS queue located in our vendor's AWS Account (`Account B`). We attached an IAM Policy to the EC2 instances granting full `sqs:*` access, but the instances are receiving an `AccessDenied` error. What is missing?**
**Answer:** In cross-account scenarios, an IAM Policy in the requesting account is not enough. The vendor's administrator in `Account B` must attach a **Resource-Based Access Policy** to the SQS queue itself, explicitly granting `sqs:ReceiveMessage` permissions to the Principal (Account ID) of `Account A`.

**Q2: You configure an S3 bucket to trigger an Event Notification to an SQS queue whenever a new `.mp4` video is uploaded. However, when you click 'Save changes' on the Event Notification configuration in the S3 console, AWS throws an error stating it cannot validate the destination configuration. What is the root cause?**
**Answer:** The SQS queue does not have the correct **Access Policy** attached. S3 operates as an AWS service principal and requires explicit permission to write to your queue. You must update the SQS Access Policy to allow `sqs:SendMessage` from the `s3.amazonaws.com` service principal, ensuring the `aws:SourceArn` matches your S3 bucket.

**Q3: A developer asks you to review a proposed SQS Access Policy that grants `s3.amazonaws.com` permission to perform `sqs:SendMessage` to a queue. The policy does not include a `Condition` block restricting the `aws:SourceArn` or `aws:SourceAccount`. What security risk does this pose?**
**Answer:** This policy suffers from the **Confused Deputy Problem**. Without a `Condition` block explicitly limiting access to _your_ S3 bucket or _your_ AWS account, any AWS user in the world could configure their own S3 bucket to send event notifications into your SQS queue, potentially flooding your backend workers with malicious or garbage data.
