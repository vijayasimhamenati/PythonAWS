As a developer, there are exactly three ways you can interact with AWS. Under the hood, _all three methods are just making API calls to AWS_.

1.  **AWS Management Console:** The web-based user interface. Great for learning, viewing billing, or doing one-off tasks. Authenticated via Username + Password + MFA.
2.  **AWS Command Line Interface (CLI):** A tool that allows you to interact with AWS services using commands in your terminal/command prompt. Great for quick testing and writing bash/shell scripts. Authenticated via **Access Keys**.
3.  **AWS Software Development Kit (SDK):** Language-specific libraries (like Python, Java, Node.js) that allow you to write application code that interacts with AWS. This is what you use 99% of the time as an AWS Developer! Authenticated via **Access Keys** (locally) or **IAM Roles** (in the cloud).

---

## 1. Access Keys (The Keys to the Kingdom)

To use the CLI or the SDK on your local machine, you need **Access Keys**.
An Access Key consists of two parts (think of them as a programmatic username and password):

- **Access Key ID:** (e.g., `AKIAIOSFODNN7EXAMPLE`)
- **Secret Access Key:** (e.g., `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)

### Who can create them and how?

- **Who:** The AWS Account Root User (not recommended), an IAM Administrator, or the IAM User themselves (if they have been granted the `iam:CreateAccessKey` permission).
- **How:**
  1. Log into the AWS Console.
  2. Go to the **IAM** service.
  3. Click on **Users**, select your user, and go to the **Security credentials** tab.
  4. Click **Create access key**.
  5. _Stephane's Warning:_ You will only see the Secret Access Key **ONCE**. Download the `.csv` file. If you lose it, you must delete the key and create a new one!

---

## 2. Setting up the AWS CLI & Local System

The AWS CLI is an open-source tool built on top of the Python SDK.

### Why do we need a local setup?

When you type `aws s3 ls` in your terminal, how does AWS know who you are? You must configure your local system to store your Access Keys securely so the CLI and SDK can find them automatically.

### The Setup Process

1.  Download and install the AWS CLI from the official AWS documentation for your OS (Windows/Mac/Linux).
2.  Open your terminal and type: `aws configure`
3.  You will be prompted to enter four pieces of information:
    - `AWS Access Key ID`: Paste your key.
    - `AWS Secret Access Key`: Paste your secret.
    - `Default region name`: (e.g., `us-east-1`). _Why? So you don't have to specify the region in every single command._
    - `Default output format`: Usually `json`.

### What happens under the hood? (Important!)

Running `aws configure` creates a hidden folder in your home directory (`~/.aws/` on Mac/Linux or `C:\Users\Username\.aws\` on Windows) with two files:

- **`credentials` file:** Stores your Access Key ID and Secret Access Key.
- **`config` file:** Stores your default region and output format.

---

## 3. Setting up the AWS SDK for Python (Boto3)

**Boto3** is the official name of the AWS SDK for Python.

### Local System Setup

1.  Ensure Python is installed on your machine.
2.  Install the SDK using pip: `pip install boto3`

### Why Boto3 is magic

You _do not_ need to pass your Access Keys directly into your Python code. Boto3 uses the **Default Credential Provider Chain**. It automatically searches your computer in a specific order to find credentials:

1.  It checks for Environment Variables.
2.  It checks the `~/.aws/credentials` file (which you created using `aws configure`!).
3.  If running on an EC2 instance, it fetches temporary credentials from the attached IAM Role.

### 💡 Practical Developer Tip (Python / Boto3)

Here is how simple it is to use Boto3 once your CLI is configured. Notice there are NO hardcoded passwords here!

```python
import boto3

# Boto3 automatically reads your ~/.aws/credentials file!
s3 = boto3.client('s3')

# List all your S3 buckets
response = s3.list_buckets()
for bucket in response['Buckets']:
    print(f"Found bucket: {bucket['Name']}")
```

---

## 1. What is the AWS CDK?

The **AWS Cloud Development Kit (CDK)** is an open-source software development framework provided by AWS. It allows you to define your cloud infrastructure (servers, databases, networks) using familiar programming languages—like **Python**, TypeScript, Java, or C#.

Instead of clicking through the AWS Console, you write Python code to say: _"Give me an S3 bucket and a DynamoDB table."_

### 2. Why do we use it? (The Pain it Solves)

Before the CDK, the standard way to write Infrastructure as Code (IaC) on AWS was using **AWS CloudFormation**.

- **The Problem with CloudFormation:** You had to write thousands of lines of static JSON or YAML. It was tedious, error-prone, and you couldn't use logic like `if` statements or `for` loops.
- **The CDK Solution:** Because CDK uses Python, you get all the power of a real programming language! You get IDE autocomplete, type checking, `for` loops (e.g., `for i in range(5): create_bucket()`), and you can even write unit tests for your infrastructure.

## 3. How it Works Internally (The Magic)

This is a crucial concept for the AWS Developer exam. **The CDK does not directly talk to AWS services to create resources.** Under the hood, it is essentially a translation engine for CloudFormation.

Here is the exact lifecycle:

1.  **Code:** You write your infrastructure in Python.
2.  **Synthesis (`cdk synth`):** When you run this command, the CDK engine executes your Python code and _translates (synthesizes)_ it into a massive, perfectly formatted AWS CloudFormation JSON/YAML template.
3.  **Deploy (`cdk deploy`):** This command takes that generated CloudFormation template and sends it to the AWS CloudFormation service. CloudFormation then provisions the actual S3 buckets, EC2 instances, etc., in your account safely.

_Stephane's Summary:_ **CDK is just a high-level developer wrapper around CloudFormation.**

## 4. Local System Setup for Python CDK

Even though you are writing Python, the core CDK engine is actually built in Node.js. Therefore, your local machine needs both environments.

**Prerequisites:**

1.  **AWS CLI Configured:** You must have run `aws configure` so the CDK has your Access Keys to deploy to your account.
2.  **Node.js:** Download and install Node.js (which includes `npm`).
3.  **Python 3:** Ensure Python is installed.

**Installation & Initialization Steps:**

1.  Install the global CDK command-line tool via npm:
    `npm install -g aws-cdk`
2.  Create an empty directory for your project and navigate into it:
    `mkdir my-cdk-project && cd my-cdk-project`
3.  Initialize a new Python CDK project:
    `cdk init app --language python`
4.  Activate the virtual environment that CDK just created:
    `source .venv/bin/activate` (Mac/Linux) OR `.venv\Scripts\activate.bat` (Windows)
5.  Install the core AWS CDK library for Python:
    `pip install -r requirements.txt` (This installs `aws-cdk-lib`)

---

## 💡 Practical Developer Tip (Python / CDK)

Here is an example of how incredibly simple it is to provision an S3 bucket with versioning enabled using the CDK in Python. Just 3 lines of code!

```python
from aws_cdk import Stack
from aws_cdk import aws_s3 as s3
from constructs import Construct

class MyStorageStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 Bucket!
        my_bucket = s3.Bucket(self, "MyFirstCdkBucket",
            versioned=True
        )
```

---

## 4. SDK vs. CDK (Crucial Concept!)

As a modern AWS Developer, you will hear both of these terms constantly. They sound similar, but they do completely different jobs.

| Feature              | AWS SDK (e.g., Boto3)                                                                                 | AWS CDK (Cloud Development Kit)                                                                       |
| :------------------- | :---------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------- |
| **What does it do?** | Interacts with _existing_ AWS resources. Reads/writes data.                                           | Creates/Destroys the _actual infrastructure_.                                                         |
| **When to use it?**  | Inside your application code (e.g., inside a Lambda function to query a database or upload an image). | Before your application runs, to provision the database or S3 bucket itself (Infrastructure as Code). |
| **Under the hood**   | Makes direct REST API calls to AWS.                                                                   | Synthesizes your Python code into an AWS CloudFormation template, which then builds the resources.    |

**The "Stephane" Summary:**
Use the **CDK** to _build_ the house (servers, databases, networks). Use the **SDK** _inside_ the house to live your life (saving files, reading data).

---

# Interview Preparation: Access, CLI, & SDKs

## Summary

Interviewers want to see that you understand local security best practices (never hardcode keys) and that you understand the architectural difference between provisioning infrastructure (CDK) and interacting with data (SDK).

## Q&A Details

**Q1: A junior developer pushed a Python script to GitHub, and you noticed they hardcoded their AWS Access Key and Secret Key inside the code. What are the risks, and how would you fix this?**

- **Answer:** This is a critical security breach. Bots constantly scrape GitHub for exposed keys and can spin up thousands of dollars of Bitcoin-mining EC2 instances in our account within minutes. First, I would immediately deactivate and delete those Access Keys in IAM. Second, I would instruct the developer to use `aws configure` to store their keys locally in the `~/.aws/credentials` file, allowing `boto3` to securely read them from the local environment rather than the codebase.

**Q2: We need to automate the creation of an S3 bucket, a DynamoDB table, and an EC2 instance. Would you use the AWS SDK for Python (Boto3) or the AWS CDK for Python to achieve this, and why?**

- **Answer:** I would highly recommend the AWS CDK. While you _can_ technically create infrastructure using Boto3, Boto3 is imperative and doesn't track state. The CDK is declarative Infrastructure as Code (IaC). It synthesizes into CloudFormation, meaning if a deployment fails halfway through, it automatically rolls back. It also makes it much easier to update or tear down the infrastructure later.

**Q3: When Boto3 makes an API call, how does it know which credentials to use if you haven't explicitly provided them in the code?**

- **Answer:** Boto3 uses the Default Credential Provider Chain. It looks for credentials in a specific order: first checking environment variables (like `AWS_ACCESS_KEY_ID`), then checking the local `~/.aws/credentials` file, and finally looking for instance metadata if it is running on an AWS service like EC2 or ECS with an attached IAM Role.

---

# Interview Preparation: AWS CDK

## Summary

For modern AWS Developer or DevOps roles, interviewers want to see that you embrace Infrastructure as Code (IaC). They will ask you to compare CDK against traditional CloudFormation or third-party tools like Terraform, and they will want to know that you understand the "Synth" process.

## Q&A Details

**Q1: We are starting a new project. Should we write our infrastructure using AWS CloudFormation (YAML) or the AWS CDK (Python)? Why?**

- **Answer:** We should absolutely use the AWS CDK with Python. While CloudFormation is the underlying engine, writing raw YAML is static and prone to typos. With the CDK, our developers can use their existing Python skills, benefit from IDE auto-completion, use conditional logic (like `if/else` for different environments), and implement unit tests for our infrastructure. Plus, the CDK requires significantly fewer lines of code because it comes with secure defaults out of the box.

**Q2: What exactly happens when you run the command `cdk synth`?**

- **Answer:** `cdk synth` (synthesize) executes our CDK Python application code and compiles it down into a standard AWS CloudFormation template (JSON or YAML). It doesn't actually deploy anything to AWS; it just prepares the instructions that CloudFormation will eventually need.

**Q3: If the AWS CDK relies on Node.js to run, how can we use Python to write our infrastructure?**

- **Answer:** AWS created a technology called **jsii**. It allows modules written in TypeScript (the core CDK engine) to be delivered and interacted with in other languages like Python, Java, and C#. When we write Python CDK code, `jsii` acts as a bridge, translating our Python calls into the underlying Node.js CDK engine during synthesis.
