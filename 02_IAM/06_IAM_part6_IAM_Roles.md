_Suggested Image from AWS Docs to insert here:_
\_![IAM Role Assumption](```mermaid
sequenceDiagram
participant EC2 as EC2 Instance (Python App)
participant STS as AWS STS
participant S3 as Amazon S3

    Note over EC2: App needs to read an S3 bucket
    EC2->>STS: 1. AssumeRole (via Instance Profile)
    STS-->>EC2: 2. Returns Temporary Credentials (Valid for 1-12 hrs)
    EC2->>S3: 3. boto3 uses Temporary Credentials for API call
    S3-->>EC2: 4. S3 allows request & returns data)_

## 1. What Exactly is an IAM Role?

Unlike an IAM User, a **Role** does not have long-term credentials (no password, no permanent Access Keys). Instead, an IAM Role provides **temporary security credentials** that are valid for a short duration (usually 1 to 12 hours).

An IAM Role has two distinct parts:

1.  **Trust Policy (Who):** A JSON document that defines _who or what_ is allowed to assume the role. (e.g., "Only EC2 instances can assume this role," or "Only users from Account B can assume this role.")
2.  **Permissions Policy (What):** A JSON document that defines _what_ the role is allowed to do once it is assumed. (e.g., "Allow read access to an S3 bucket.")

## 2. Why Developers Must Use Roles

If you are writing a Python web scraper that runs on an EC2 instance and saves data to DynamoDB, you _could_ create an IAM User, generate Access Keys, and put them in your Python code. **Do not do this.**

- **The Problem:** If you commit those keys to a public GitHub repo, bots will steal them in seconds and spin up thousands of dollars of Bitcoin miners in your AWS account.
- **The Solution:** Attach an **IAM Role for EC2** to the instance. The EC2 service will automatically contact the AWS Security Token Service (STS) behind the scenes, grab temporary credentials, and rotate them automatically.

## 3. Top IAM Best Practices (Straight from AWS Docs)

AWS constantly tests you on these best practices for both the Developer and Solutions Architect exams:

- **Require human users to use federation:** Instead of creating IAM Users for employees, use your company's Active Directory or Okta to federate into AWS using temporary roles.
- **Require workloads to use IAM Roles:** Applications running on EC2, Lambda, or ECS should _always_ use IAM roles. **Never embed long-term credentials in code.**
- **Grant Least Privilege:** Start with a minimum set of permissions and grant additional permissions only as necessary. Don't use `AdministratorAccess` just because it's "easier for testing."
- **Configure strong password policies and require MFA:** If you _must_ have IAM Users (like the Root user or emergency admin users), enforce complex passwords and Multi-Factor Authentication.
- **Use IAM Access Analyzer:** This AWS tool helps you identify resources in your organization and accounts that are shared with an external entity, helping you spot security leaks.

---

## 💡 Practical Developer Tip (Python / Boto3)

When you run your Python code on an AWS service like Lambda or EC2 that has an IAM Role attached, Boto3 handles the temporary credentials completely automatically.

Look at how clean and secure this code is. There are zero passwords:

```python
import boto3

# Boto3 implicitly searches for the IAM Role attached to the EC2 instance or Lambda function.
# It automatically retrieves, uses, and rotates the temporary STS credentials!
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('MyApplicationData')

# Write data securely without hardcoding any keys
response = table.put_item(
    Item={
        'UserId': '123',
        'Name': 'Stephane'
    }
)
```

_Stephane's Summary:_ Write code as if credentials don't exist. Let the environment (IAM Roles) inject them for you.

---

# Interview Preparation: Roles & Best Practices

## Summary

Interviewers want to see that you have a "security-first" mindset. The fastest way to fail an AWS developer interview is to suggest hardcoding Access Keys. Always default to IAM Roles and Least Privilege.

## Q&A Details

**Q1: We need to give a third-party auditing company access to view our AWS billing reports. Should we create an IAM User with a password and email it to them?**

- **Answer:** Absolutely not. Creating permanent IAM users for third parties is a major security risk. Instead, we should create an IAM Role in our account with a Trust Policy that specifically allows the third-party company's AWS Account ID to `sts:AssumeRole`. We should also require an `ExternalId` in the trust policy to prevent the "confused deputy" problem.

**Q2: You just took over an old Python application running on an EC2 instance. You notice the previous developer stored their personal IAM Access Keys in a `.env` file on the server to access S3. How would you fix this architecture?**

- **Answer:** I would immediately remove the `.env` file and rotate/delete those permanent Access Keys in IAM. Then, I would create an IAM Role with a policy granting the exact S3 permissions needed. I would attach this Role directly to the EC2 instance as an Instance Profile. Finally, I would ensure the `boto3` SDK in the Python code relies on the default credential provider chain, which will automatically use the Role's temporary credentials.

**Q3: What is the purpose of an IAM Policy Condition block, and how does it help enforce best practices?**

- **Answer:** The Condition block allows us to enforce highly granular security restrictions. To follow the best practice of least privilege, I can use conditions to ensure an IAM Role can only be assumed if the user has MFA enabled (`aws:MultiFactorAuthPresent`), or if the API call is originating from our corporate IP address (`aws:SourceIp`).
