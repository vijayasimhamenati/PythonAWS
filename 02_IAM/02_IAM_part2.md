## 1. Anatomy of an IAM Policy (JSON)

IAM Policies are written in JSON. For the exam and the real world, remember the acronym **PARC** (or sometimes referred to as the Statement elements):

- **P**rincipal: _Who_ is this applied to? (Usually only used in Resource-based policies, like S3 bucket policies).
- **A**ction: _What_ API call are you allowing/denying? (e.g., `s3:GetObject`, `dynamodb:PutItem`).
- **R**esource: _Which_ specific AWS resource? (e.g., `arn:aws:s3:::my-python-app-bucket/*`).
- **C**ondition: _When_ does this apply? (e.g., Only if the IP address is `192.168.0.1`, or only if the user has MFA enabled).

## 2. IAM Evaluation Logic

This is a massive topic for AWS certifications. AWS evaluates policies based on a strict hierarchy.

**The Golden Rules of Evaluation:**

1. **Default Deny:** By default, all requests are implicitly denied.
2. **Explicit Allow:** If a valid policy explicitly allows the action, it overrides the default deny.
3. **Explicit Deny ALWAYS wins:** If there is an explicit deny anywhere in the user's policies, it will override _any_ explicit allows. No exceptions!

## 3. Identity Federation & STS

What if you have 10,000 employees in your corporate Active Directory, or 100,000 users logging into your Python mobile app via Google/Facebook? You _do not_ create IAM Users for them! You use **Federation**.

Federation allows users outside of AWS to assume temporary privileges inside AWS.

- **SAML 2.0 Federation:** Used for corporate enterprises (Active Directory).
- **Web Identity Federation:** Used for apps (Google, Apple, Facebook logins). As an AWS developer, you will almost always use **Amazon Cognito** to handle this.
- **AWS STS (Security Token Service):** The engine behind the scenes. It generates the temporary, short-lived credentials (Access Key, Secret Key, and Session Token) when a role is assumed.

### Practical Developer Tip (Python / Boto3)

Sometimes your Python script in _Account A_ needs to read a database in _Account B_. You use `boto3` to call the STS `assume_role` API. It gives you temporary credentials to act as a Role in Account B!

```python
import boto3

# 1. Call STS to assume the cross-account role
sts_client = boto3.client('sts')
assumed_role_object = sts_client.assume_role(
    RoleArn="arn:aws:iam::ACCOUNT_B_ID:role/CrossAccountDBReader",
    RoleSessionName="PythonScriptSession"
)

# 2. Extract the temporary credentials
credentials = assumed_role_object['Credentials']

# 3. Create a new boto3 client using these temporary keys
dynamodb = boto3.client(
    'dynamodb',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken']
)

# Now you can query Account B's database!

```

---

# Interview Preparation: Advanced IAM & Federation

## Summary

For Developer and Solutions Architect interviews, you must demonstrate a rock-solid understanding of policy conflicts (Deny wins) and cross-account or external access using STS (Security Token Service) and IAM Roles.

## Q&A Details

**Q1: An IAM User belongs to the 'Developers' group which has an Explicit Allow for `s3:PutObject`. However, a custom policy attached directly to the user has an Explicit Deny for all S3 actions. Can the user upload a file to S3?**

- **Answer:** No, the user will be denied. In AWS IAM evaluation logic, an Explicit Deny always overrides an Explicit Allow, regardless of whether the allow comes from a group, a managed policy, or an inline policy.

**Q2: We are building a B2C (Business to Consumer) Python web application. Users will log in using their Google or Apple accounts, and they need to upload profile pictures directly to our S3 bucket. How do we architect this securely?**

- **Answer:** I would use Web Identity Federation via Amazon Cognito. Users will authenticate with Google/Apple, and Cognito will exchange that authentication token for temporary AWS credentials via AWS STS. These temporary credentials will be mapped to a highly restricted IAM Role that only allows the user to upload to their specific folder in the S3 bucket using condition keys like `${cognito-identity.amazonaws.com:sub}`.

**Q3: How do you securely allow a Lambda function in AWS Account A to read data from a DynamoDB table in AWS Account B?**

- **Answer:** I would create an IAM Role in Account B that has permissions to read the DynamoDB table. The trust policy of this role must allow Account A to assume it. Then, the Lambda function in Account A needs an execution role with `sts:AssumeRole` permissions. My Python code in Lambda will use `boto3.client('sts').assume_role()` to get temporary credentials for Account B to perform the read operation.
