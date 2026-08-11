# IAM Part 5: The Shared Responsibility Model

When you use AWS, security is a partnership. The **Shared Responsibility Model** dictates who is responsible for what.

The easiest way to remember it is:

- **AWS** is responsible for the Security **OF** the Cloud.
- **You (The Customer)** are responsible for the Security **IN** the Cloud.

Let's look at exactly how this applies to Identity and Access Management (IAM).

## 1. AWS's Responsibility (Security OF the Cloud)

AWS manages the underlying infrastructure and the actual IAM software engine.

- **Infrastructure:** AWS protects the physical data centers, servers, and network infrastructure that run the IAM service globally.
- **High Availability:** AWS ensures the IAM API is always online so your applications can authenticate.
- **Evaluation Logic:** AWS guarantees that the mathematical policy evaluation logic (Explicit Deny > Explicit Allow) functions flawlessly.
- **Compliance:** AWS ensures their internal systems meet global security standards (SOC, PCI, HIPAA).

## 2. Customer's Responsibility (Security IN the Cloud)

AWS provides the tools, but **you** have to configure them correctly. AWS will not stop you from giving everyone `AdministratorAccess`—that is your responsibility!

- **Managing Users, Groups, and Roles:** You are responsible for creating identities and offboarding employees when they leave.
- **Applying Least Privilege:** You must write strict JSON IAM policies that only grant exact permissions needed.
- **Enforcing MFA:** You must configure and mandate Multi-Factor Authentication (MFA) for your users, especially the Root account.
- **Credential Rotation:** You are responsible for rotating IAM Access Keys regularly and ensuring they are never leaked to public repositories like GitHub.
- **Analyzing Access:** Using tools like IAM Access Analyzer to ensure your resources aren't accidentally exposed to the public.

---

## 💡 Practical Developer Tip (Python / Boto3)

As a Developer or DevOps engineer, part of your shared responsibility is ensuring Access Keys don't get too old (which makes them vulnerable). You can use Python to automate this security check!

Here is a quick script to list all IAM users and find access keys that exist in your account. You could easily expand this to alert you if keys are over 90 days old.

```python
import boto3
from datetime import datetime, timezone

# Create IAM client using your local AWS profile or EC2 Role
iam = boto3.client('iam')

# Get all users in the AWS account
users = iam.list_users()

print("--- IAM Access Key Audit ---")
for user in users['Users']:
    username = user['UserName']

    # Fetch the access keys for each user
    keys = iam.list_access_keys(UserName=username)

    for key in keys['AccessKeyMetadata']:
        key_id = key['AccessKeyId']
        create_date = key['CreateDate']

        # Calculate how old the key is
        age_in_days = (datetime.now(timezone.utc) - create_date).days

        print(f"User: {username} | Key: {key_id} | Age: {age_in_days} days")

        if age_in_days > 90:
            print(f"  [WARNING] Key for {username} is over 90 days old! Rotate immediately.")
```

---

# Interview Preparation: Shared Responsibility in IAM

## Summary

Interviewers love this topic because it reveals whether you have a mature security mindset. If there is a data breach, they want to know if you understand who is at fault based on the shared model. Always remember: data, policies, and credentials belong to the customer.

## Q&A Details

**Q1: A junior developer accidentally commits their AWS Access Key and Secret Key to a public GitHub repository. Ten minutes later, a bot finds the keys and spins up 100 expensive EC2 instances for crypto-mining. Under the Shared Responsibility Model, who is responsible for paying this bill?**

- **Answer:** The customer is 100% responsible. AWS guarantees the security _of_ the cloud (the physical hardware and hypervisors), but the customer is responsible for security _in_ the cloud, which strictly includes the protection and management of their IAM credentials. Leaking credentials is a failure of customer responsibility.

**Q2: We want to ensure that no IAM user in our account can log in without a physical hardware token or an authenticator app. Is it AWS's responsibility to enforce this by default?**

- **Answer:** No, it is the customer's responsibility. While AWS provides the _capability_ to use Multi-Factor Authentication (MFA), it is the customer's responsibility to actually configure it, enable it, and write IAM policies that deny access unless `aws:MultiFactorAuthPresent` is evaluated as true.

**Q3: We noticed that the IAM service was completely down globally for 5 minutes, preventing our application from authenticating users. Whose responsibility is this?**

- **Answer:** This falls under AWS's responsibility. AWS is responsible for the highly available infrastructure and software that runs the global IAM service. The operational uptime of the cloud APIs is strictly part of "Security OF the Cloud."
