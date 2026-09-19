**Issue:** ENG-402
**Title:** Implement Serverless Threshold Alerter Pipeline with Streamlit Ingestion
**Assignee:** Developer
**Reporter:** Solution Architect
**Epic:** Real-Time Data Processing & Alerting
**Estimate:** 1 Story Point (1-Day Task)

---

### **Description**

**Background:**
We need an automated pipeline to ingest and validate batch data files. The user will upload a CSV containing sensor metrics (e.g., water quality telemetry) via a web frontend. If any metrics in the CSV breach predefined safety thresholds, the system must immediately notify the on-call engineer via email.

**Architecture Flow:**

![Architecture Diagram](./assets/threshold_alerter_architecture.png)

1. **Frontend:** Streamlit app accepts the CSV upload.
2. **Ingestion:** Streamlit uses `boto3` to push the file to an S3 bucket.
3. **Event Trigger:** The S3 `ObjectCreated` event triggers a Lambda function.
4. **Processing:** Lambda reads the file into memory, parses the rows, and evaluates the metrics.
5. **Notification:** If an anomaly is found, Lambda publishes a payload to an SNS topic.
6. **Delivery:** SNS pushes an email alert to subscribed users.

### **Acceptance Criteria (DoD)**

- [ ] Streamlit UI successfully authenticates with AWS and uploads a CSV to the designated S3 bucket.
- [ ] Uploading a file to the bucket automatically invokes the Lambda function.
- [ ] Lambda successfully reads the object from S3 without permission errors.
- [ ] If thresholds are exceeded (e.g., `turbidity > 5.0` or `pH > 8.5`), an email is successfully delivered containing the specific row data.
- [ ] Infrastructure follows least-privilege IAM permissions.

---

### **Implementation Guide & Technical Notes**

Please follow these steps to execute the architecture.

#### **Step 1: Foundational Infrastructure (AWS Console)**

1. **Create the SNS Topic:** Navigate to SNS, create a Standard topic named `MetricAlerts`. Create a subscription for your email address. _Note: You must click the confirmation link in your email before it will work._
2. **Create the S3 Bucket:** Create a bucket (e.g., `telemetry-ingestion-bucket-dev`). Keep it private.

#### **Step 2: IAM & Security**

You will need two separate IAM roles:

1. **Frontend User/IAM Key:** Create an IAM user for the Streamlit app. Generate Access Keys. Attach an inline policy that only allows `s3:PutObject` on the specific bucket ARN.
2. **Lambda Execution Role:** Create a role for Lambda. It requires:

- `AWSLambdaBasicExecutionRole` (for CloudWatch logging).
- An inline policy for `s3:GetObject` on the bucket.
- An inline policy for `sns:Publish` on the SNS topic ARN.

#### **Step 3: The Lambda Processor (Python)**

Create a Python 3.x Lambda function. Attach the execution role created above.

- **Logic Requirements:**
- Use the `event` payload to dynamically get the `bucket_name` and `object_key`.
- Use `boto3.client('s3').get_object()` to stream the file.
- Parse the CSV using the built-in `csv` module (no need to package `pandas` for a simple file, which keeps the Lambda lightweight).
- If a threshold is breached, use `boto3.client('sns').publish()` to send a formatted alert string.

- **Trigger:** Add a trigger to the Lambda function. Select S3, choose your bucket, and set the event type to `All object create events`.

#### **Step 4: The Streamlit Frontend**

Initialize a standard Streamlit file structure.

- Use `st.file_uploader(type=['csv'])` to capture the file.
- Configure `boto3` using environment variables or a `.env` file (do not hardcode your IAM access keys in the script).
- When the user clicks the "Upload" button, use `boto3.client('s3').upload_fileobj()` to push the Streamlit file buffer directly to the S3 bucket.

---

**SA Note:** Start with the AWS backend first. Hardcode a test event in Lambda to ensure it can parse S3 and trigger SNS. Once the serverless backend is green, move to Streamlit to wire up the frontend ingestion.
