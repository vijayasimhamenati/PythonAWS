## Identity and Access Management (IAM) - The Basics

IAM is how you manage access to AWS services and resources securely.

- **Important:** IAM is a **global** service. You do not select a Region for IAM.
- **Root Account:** Created by default. **Never use it for daily work or coding!** Lock it away with MFA (Multi-Factor Authentication).

### The 4 Pillars of IAM

1. **Users:** Represent individual people or applications.
2. **Groups:** Collections of users. (e.g., "Developers", "DataScientists"). You assign permissions to the group, and all users inside inherit them.
3. **Policies:** JSON documents that explicitly list what you are allowed (or denied) to do. _AWS follows the "Principle of Least Privilege"_—you start with zero permissions and must be explicitly allowed to do anything.
4. **Roles:** This is the most important concept for you as an AWS Developer! Roles are **temporary** identities. Instead of giving a user a permanent password, you allow a service (like an EC2 server running your Python app) to "assume" a Role to securely talk to other services (like an S3 bucket).

### Practical Developer Tip (Python / Boto3)

When you write Python code locally, you use `aws configure` in your terminal to set your permanent IAM User Access Keys.

But when you deploy that Python code to AWS (like onto an EC2 instance or a Lambda function), **NEVER hardcode your access keys in your Python script**. Instead, you assign an **IAM Role** to the EC2 instance. Your `boto3` library is smart enough to automatically find those temporary credentials in the background!

```python
import boto3

# Boto3 automatically looks for the IAM Role attached to the environment.
# No hardcoded keys needed! This is best practice.
s3_client = boto3.client('s3')
response = s3_client.list_buckets()

```

---

Here is your interview prep for IAM Fundamentals:

# Interview Preparation: IAM Fundamentals

## Summary

In AWS Developer interviews, security is paramount. Interviewers want to ensure you never hardcode credentials and that you deeply understand the difference between IAM Users (long-term credentials for humans/external apps) and IAM Roles (short-term credentials for AWS services).

## Q&A Details

**Q1: How would you grant an EC2 instance running a Python web scraper permission to upload files to an Amazon S3 bucket?**

- **Answer:** I would create an IAM Policy that allows `s3:PutObject` on that specific bucket. Then, I would create an IAM Role for EC2 and attach that policy to the role. Finally, I would attach the IAM Role to the EC2 instance. My Python code using `boto3` will automatically inherit the temporary credentials from the instance metadata. I would _never_ put IAM access keys in my code.

**Q2: What is the "Principle of Least Privilege"?**

- **Answer:** It is the security practice of giving a user, role, or system only the exact permissions they need to perform their specific job, and nothing more. For example, if my Python script only needs to read from a database, I will grant it `ReadOnlyAccess`, not full `AdministratorAccess`.

**Q3: Explain the difference between an IAM Role and an IAM Group.**

- **Answer:** An IAM Group is a collection of IAM Users. It is used to easily manage permissions for multiple humans at once (like giving all developers access to a development environment). An IAM Role, on the other hand, is an identity with temporary credentials that can be assumed by anyone who needs it—most commonly used by AWS services (like Lambda or EC2) to interact with other AWS services securely.
