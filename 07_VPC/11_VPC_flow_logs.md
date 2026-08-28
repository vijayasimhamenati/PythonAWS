# VPC Flow Logs: Network Monitoring and Troubleshooting

In AWS, it is entirely possible to create a perfectly architected network where traffic is inexplicably failing. When Security Groups, NACLs, or Route Tables are misconfigured, packets are simply dropped silently.

To diagnose these issues, or to monitor for malicious activity like port scanning, you must use **VPC Flow Logs**.

## 1. What are VPC Flow Logs?

VPC Flow Logs capture metadata about the IP traffic going to and from network interfaces within your VPC.

- **Levels of Capture:** You can enable flow logs at the VPC level (captures all traffic in the VPC), the Subnet level, or on a specific Elastic Network Interface (ENI).
- **What is Captured?** They do _not_ capture the actual payload (the data) of the packet. They capture the metadata (Source IP, Destination IP, Ports, Protocol, and whether the packet was Accepted or Rejected).
- **Supported Interfaces:** They capture traffic for EC2 instances, but also for managed services deployed in your VPC like ELBs, RDS databases, NAT Gateways, and Transit Gateways.

### Where do the logs go?

You can configure VPC Flow Logs to publish to three primary destinations:

1. **Amazon CloudWatch Logs:** Best for real-time alerting and streaming analysis using CloudWatch Logs Insights.
2. **Amazon S3:** Best for long-term, cheap storage and querying massive datasets using Amazon Athena (SQL).
3. **Amazon Kinesis Data Firehose:** Best for streaming the logs to third-party SIEMs (like Splunk or Datadog) or custom analytics pipelines.

---

## 2. Using Flow Logs for Troubleshooting (Exam Focus)

The most important field in a VPC Flow Log is the `action` field, which will be logged as either `ACCEPT` or `REJECT`.

By analyzing the `action` field alongside the direction of traffic (Inbound vs. Outbound), you can instantly determine if a connectivity issue is caused by a stateless NACL or a stateful Security Group.

### The Troubleshooting Matrix

**Scenario A: Inbound Request from the Internet**

- **Log shows:** `Inbound REJECT`
- **Diagnosis:** The request was blocked. Because the packet just arrived, it could have been blocked by the Subnet's **NACL** _or_ the instance's **Security Group**.
- **Log shows:** `Inbound ACCEPT` followed by `Outbound REJECT`
- **Diagnosis:** This is **100% a NACL issue**. Why? Because Security Groups are stateful. If the Security Group allowed the traffic _in_, it automatically allows the response _out_. The only firewall that would block the outbound response is the stateless NACL (likely missing an Ephemeral Port rule).

**Scenario B: Outbound Request to the Internet (e.g., `yum update`)**

- **Log shows:** `Outbound REJECT`
- **Diagnosis:** Could be the **NACL** or the **Security Group** outbound rules.
- **Log shows:** `Outbound ACCEPT` followed by `Inbound REJECT`
- **Diagnosis:** This is **100% a NACL issue**. The Security Group allowed the request out, and its statefulness would automatically allow the response back in. The stateless NACL blocked the returning packet.

---

## 3. Security and Automation Architectures

VPC Flow Logs are a foundational element of DevSecOps in AWS.

- **Intrusion Detection:** You can stream flow logs to CloudWatch and configure a Metric Filter looking for specific patterns (e.g., `REJECT` actions on Port 22). If a hacker runs a port scanner against your infrastructure, CloudWatch will detect the spike in rejected SSH connections, trigger a CloudWatch Alarm, and send an SNS alert to the security team.
- **Traffic Analytics:** By streaming to S3 and querying with Amazon Athena, you can identify the "Top 10" IP addresses consuming the most bandwidth, helping to optimize costs or identify data exfiltration attempts.
- **Permissions:** VPC Flow Logs run as a background AWS service. To publish logs to CloudWatch, you must provide the service with an **IAM Role** containing permissions like `logs:CreateLogStream` and `logs:PutLogEvents`.

---

## Interview Preparation: VPC Flow Logs

### Summary

If a scenario involves diagnosing silent network failures, auditing IP traffic, or detecting port scans, the answer is always **VPC Flow Logs**.

### Q&A Details

**Q1: A developer reports that their EC2 instance in a private subnet can successfully reach out to a third-party API, but the incoming responses are failing. You check the VPC Flow Logs for that ENI and see an `Outbound ACCEPT` log followed immediately by an `Inbound REJECT` log. What is the exact architectural issue?**
**Answer:** The issue resides in the **Network ACL (NACL)** associated with the private subnet. Security Groups are stateful; because the `Outbound ACCEPT` occurred, the Security Group would automatically allow the response. The `Inbound REJECT` proves that the returning packet hit the stateless NACL and was dropped, likely because the NACL is missing an inbound allow rule for the required Ephemeral Port range.

**Q2: We need to monitor our VPC for malicious activity. Specifically, if a single external IP address attempts to connect to our database instances on Port 3306 and is rejected more than 50 times in a 5-minute period, our security team needs an immediate Slack notification. How do we build this using native AWS services?**
**Answer:** First, enable **VPC Flow Logs** on the database subnets and configure them to publish to **CloudWatch Logs**. Second, create a **CloudWatch Metric Filter** that parses the logs for the specific pattern (Destination Port `3306` with Action `REJECT`). Third, create a **CloudWatch Alarm** based on that metric filter that triggers if the threshold exceeds 50 within 5 minutes. Finally, configure the alarm's action to publish to an **SNS Topic**, which can trigger an AWS Lambda function to format and send the alert to Slack.

**Q3: We enabled VPC Flow Logs on our primary production VPC and set the destination to an S3 bucket. We want to query these logs to find the total amount of bytes transferred between our web servers and our NAT Gateway over the last 30 days. What is the most efficient way to query this raw data in S3?**
**Answer:** The most efficient way is to use **Amazon Athena**. Athena allows you to run standard SQL queries directly against the raw VPC Flow Log files stored in the S3 bucket without needing to load the data into a traditional database or data warehouse.

---

# Practical Guide: Configuring and Querying VPC Flow Logs

In this hands-on guide, we will configure VPC Flow Logs to capture network traffic metadata. We will send this data to two destinations simultaneously: Amazon CloudWatch Logs (for real-time streaming) and Amazon S3 (for batch analysis using Amazon Athena).

---

## 1. Creating the Flow Log Destinations

Before we can capture network traffic, we need places to store it.

### Destination A: Amazon S3

1. Navigate to the **S3 Console**.
2. Click **Create bucket**.
3. **Name:** Give it a globally unique name (e.g., `demo-vpc-flow-logs-[your-initials]`).
4. Ensure it is in the same Region as your VPC.
5. Click **Create bucket**. Keep this tab open; you will need the Bucket ARN shortly.

### Destination B: CloudWatch Logs

1. Navigate to the **CloudWatch Console**.
2. On the left menu, select **Log groups**.
3. Click **Create log group**.
4. **Name:** `VPCFlowLogs`.
5. **Retention:** Set to **1 day** (to save costs for this demo).
6. Click **Create**.

To allow the VPC service to publish logs to CloudWatch, you need an IAM Role.

1. Navigate to the **IAM Console** > **Roles** > **Create role**.
2. Select **Custom trust policy** and enter the following JSON to allow the VPC service to assume the role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "vpc-flow-logs.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

3. Click Next. Search for and attach the `CloudWatchLogsFullAccess` policy.
4. Click Next. Name the role `FlowLogsRole` and click **Create role**.

---

## 2. Enabling VPC Flow Logs

Now we will attach the monitors to our custom VPC.

1. Navigate to the **VPC Console** > **Your VPCs**.
2. Select your `DemoVPC`.
3. Click the **Flow logs** tab at the bottom, then click **Create flow log**.

### Creating the S3 Flow Log

1. **Name:** `DemoS3FlowLog`.
2. **Filter:** Select **All** (to capture both Accept and Reject actions).
3. **Maximum aggregation interval:** Select **1 minute** (Default is 10. We use 1 minute for this demo so data appears faster, but in production, 10 minutes is significantly cheaper).
4. **Destination:** Select **Send to an Amazon S3 bucket**.
5. **S3 bucket ARN:** Paste the ARN of the S3 bucket you created earlier.
   _(Note: AWS will automatically generate the required S3 Bucket Policy to allow the write permissions)._
6. Click **Create flow log**.

### Creating the CloudWatch Flow Log

1. Click **Create flow log** again.
2. **Name:** `DemoCWFlowLog`.
3. **Filter:** Select **All**.
4. **Maximum aggregation interval:** Select **1 minute**.
5. **Destination:** Select **Send to CloudWatch Logs**.
6. **Destination log group:** Select `VPCFlowLogs`.
7. **IAM role:** Select `FlowLogsRole`.
8. Click **Create flow log**.

---

## 3. Viewing Logs in CloudWatch

Within a few minutes, data will begin populating.

1. Navigate to the **CloudWatch Console** > **Log groups**.
2. Click on `VPCFlowLogs`.
3. You will see several **Log streams**. Each stream corresponds to a specific Elastic Network Interface (ENI) in your VPC.
4. To find your Bastion Host's logs, go to the EC2 console, select your Bastion instance, look at the Networking tab, and find the **Network interface ID** (e.g., `eni-01234abcd`).
5. Click the Log stream matching that ENI.
6. You will see lines of raw data. Look specifically for external public IPs attempting to connect and resulting in a `REJECT` status—this is typical background internet noise (automated bots scanning for open ports).

---

## 4. Querying Flow Logs with Amazon Athena

CloudWatch is great for real-time streaming, but for querying thousands of records using SQL, we use Amazon Athena to query the logs stored in S3.

### Preparing Athena

Athena needs its own S3 bucket to temporarily store the results of the queries you run.

1. Create a quick S3 bucket (e.g., `demo-athena-results-[your-initials]`).
2. Navigate to the **Athena Console**.
3. Click **Settings** > **Manage**.
4. Under **Query result location**, browse S3 and select your new Athena results bucket. Add a trailing slash (e.g., `s3://demo-athena-results/`). Click Save.

### Creating the Athena Table

We must define the schema so Athena knows how to read the raw text logs in S3.

1. In the Athena Query Editor, run the standard AWS-provided DDL query to create the table structure. _(You can find this query in the AWS Documentation by searching "Querying VPC Flow Logs with Athena")_.
2. **Crucial Step:** At the very bottom of the SQL statement, you must replace the `LOCATION` string with the specific S3 URI of your flow logs.

- Navigate to your S3 Flow Logs bucket. Dig down through the folders (`AWSLogs` -> `[AccountID]` -> `vpcflowlogs` -> `[Region]`) and copy the S3 URI.
- Example: `LOCATION 's3://demo-vpc-flow-logs/AWSLogs/123456789012/vpcflowlogs/eu-central-1/'`

3. Click **Run**.

### Loading the Partitions

Because VPC Flow Logs are partitioned by date, you must explicitly load the partition for today's date so Athena can find the files.

1. Run the `ALTER TABLE` statement (also found in the AWS docs) and supply the specific date folder you want to query.

```sql
ALTER TABLE vpc_flow_logs ADD PARTITION (`date`='2026-08-28')
LOCATION 's3://demo-vpc-flow-logs/AWSLogs/123456789012/vpcflowlogs/eu-central-1/2026/08/28/';

```

2. Click **Run**.

### Running the Analytics Query

Now you can use standard SQL to analyze your network traffic!

To find all malicious/rejected traffic:

```sql
SELECT *
FROM vpc_flow_logs
WHERE action = 'REJECT'
LIMIT 100;

```

**Success!** You have successfully implemented a full DevSecOps network monitoring pipeline.

_Remember to delete your Flow Logs and empty your S3 buckets to prevent ongoing charges after completing this exercise._
