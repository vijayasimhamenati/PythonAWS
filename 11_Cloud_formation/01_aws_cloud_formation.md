# AWS CloudFormation: Infrastructure as Code (IaC)

Until now, we have provisioned infrastructure by clicking through the AWS Management Console—creating VPCs, configuring routing tables, and launching EC2 instances manually. While this is great for learning, it is entirely unscalable for production.

**AWS CloudFormation** introduces the concept of **Infrastructure as Code (IaC)**. It allows you to declare exactly what resources you need in a YAML or JSON text file. When you submit this file, AWS automatically provisions and connects the resources in the correct order.

---

## 1. Why Use CloudFormation?

For modern software teams moving rapidly through development sprints, manually configuring infrastructure creates bottlenecks and introduces human error. CloudFormation solves this by treating your infrastructure exactly like application code.

- **Version Control:** Your infrastructure is defined in a text file. You can commit it to Git, track changes over time, and subject infrastructure updates to standard code reviews.
- **Cost & Lifecycle Management:** If you need an isolated environment for automated testing, CloudFormation can spin up a complete replica of your production architecture in minutes. To save costs, you can automate the deletion of the entire environment at 5:00 PM and spin it back up at 8:00 AM.
- **Separation of Concerns:** You do not have to put your entire company in one massive template. You can create a "Network Stack" for your VPCs, a "Database Stack" for your RDS instances, and an "Application Stack" for your compute layer.
- **Automated Diagramming:** AWS provides a tool called Infrastructure Composer that can read your CloudFormation code and automatically generate visual architecture diagrams.

---

## 2. How CloudFormation Works (The Engine)

CloudFormation uses a **declarative** model. You do not write scripts telling AWS _how_ to build things (e.g., "Create a VPC, wait 5 seconds, then create a subnet"). You simply declare the desired end state (e.g., "I need a VPC and a Subnet"), and the CloudFormation engine figures out the dependency graph and the correct order of operations.

1. **The Template:** You write your YAML/JSON file defining the resources.
2. **Amazon S3:** The template is uploaded to an S3 bucket (often automatically by the CLI).
3. **The Stack:** CloudFormation reads the template from S3 and provisions the resources as a single unit called a **Stack**.
4. **Updates & Deletions:** If you need to change a security group port, you do not edit the live resource. You update the code in your template and submit it to CloudFormation. If you delete the Stack, every single resource created by that template is cleanly and automatically destroyed.

---

## 3. Anatomy of a CloudFormation Template

A CloudFormation template is broken down into specific logical blocks. Understanding these building blocks is heavily tested on AWS exams.

### 1. Resources (The Only Mandatory Section)

This is the core of the template. It is where you declare the actual AWS components you want to create (e.g., `AWS::EC2::Instance`, `AWS::S3::Bucket`). If a template does not have a Resources section, it is invalid.

### 2. Parameters

Parameters act as dynamic inputs for your template. Instead of hardcoding values, you can use Parameters to pass data in at runtime.

- _Example:_ Creating an `InstanceType` parameter so the user can choose between `t2.micro` for dev environments and `m5.large` for production environments when launching the stack.

### 3. Mappings

Mappings are static variables hardcoded into the template. They function like a lookup table.

- _Example:_ An Amazon Machine Image (AMI) ID for Linux changes depending on the AWS Region. You can create a Mapping that tells CloudFormation: "If the region is us-east-1, use AMI 123; if the region is eu-west-1, use AMI 456."

### 4. Outputs

Outputs allow you to export specific values from your stack so they can be viewed in the console or imported by other stacks.

- _Example:_ If your Network Stack creates a VPC, you can export the `VPC-ID` in the Outputs section. Your Application Stack can then import that ID to know exactly where to deploy its EC2 instances.

### 5. Conditionals

Conditionals allow you to apply logical `If/Then` statements to resource creation.

- _Example:_ "If the environment is set to 'Production', create a Multi-AZ database. If it is set to 'Test', only create a Single-AZ database."

---

## Interview Preparation: AWS CloudFormation

### Summary

Focus on the benefits of Infrastructure as Code, the atomic nature of stack deployments (if one resource fails, the whole stack rolls back), and the specific functions of the template building blocks.

### Q&A Details

**Q1: We deployed a CloudFormation stack that provisions a VPC, several subnets, and an Auto Scaling Group. During the deployment, the VPC and subnets were created successfully, but the Auto Scaling Group failed to provision due to an invalid parameter. What is the state of the VPC and subnets?**
**Answer:** They have been deleted. CloudFormation treats stack deployments as single atomic operations. If any resource in the template fails to provision, CloudFormation automatically triggers a **Rollback**, destroying any resources that were successfully created during that deployment attempt to ensure the environment does not end up in a corrupted, half-deployed state.

**Q2: We have a single CloudFormation template used to deploy our application globally. However, the AMI IDs for our EC2 instances differ in every AWS region. How can we author the template so it automatically selects the correct AMI ID based on the region it is being deployed in, without requiring the user to manually input the ID?**
**Answer:** You should use the **Mappings** section of the CloudFormation template. You can create a lookup table mapping each AWS Region code to its corresponding AMI ID. Within the Resources section, you can use the intrinsic function `Fn::FindInMap` to dynamically retrieve the correct AMI ID based on the region the stack is currently deploying into.

**Q3: Our network team manages a CloudFormation stack that provisions the corporate VPCs and Security Groups. Our application teams manage separate CloudFormation stacks for their microservices. How can the application stacks dynamically reference the Subnet IDs created by the network team's stack?**
**Answer:** The network team should use the **Outputs** section of their CloudFormation template to `Export` the specific Subnet IDs. The application teams can then use the intrinsic function `Fn::ImportValue` in their templates to dynamically reference those exported Subnet IDs, allowing for a clean separation of concerns.

---

# Practical Guide: Deploying Your First CloudFormation Stack

In this hands-on lab, we will use AWS CloudFormation to automatically provision a single EC2 instance using a YAML template.

**Important Pre-requisite:** For this specific exercise, ensure your AWS console is set to the **us-east-1 (N. Virginia)** region. AMI IDs are unique to each region, and the AMI ID hardcoded in the sample template below will only work in `us-east-1`.

---

## 1. Understanding the YAML Template

Instead of clicking through the EC2 launch wizard, we will define our instance using code.

Save the following code to a file named `0-just-ec2.yaml` on your local machine.

```yaml
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      AvailabilityZone: us-east-1a
      ImageId: ami-0c55b159cbfafe1f0 # Amazon Linux 2023 AMI in us-east-1
      InstanceType: t2.micro
```

### Code Breakdown:

- **`Resources:`** This is the only mandatory section of a CloudFormation template. It tells AWS that the following block defines the infrastructure to build.
- **`MyInstance:`** This is the **Logical ID**. It is the name you use _inside the code_ to refer to this specific resource.
- **`Type: AWS::EC2::Instance`** This tells the CloudFormation engine exactly what kind of AWS resource to provision.
- **`Properties:`** This defines the configuration of the resource (the AZ, the AMI, and the size).

---

## 2. Deploying the Stack

Let's hand this code over to AWS so it can build the instance.

1. Navigate to the **CloudFormation Console** (Ensure you are in `us-east-1`).
2. Click **Create stack** > **With new resources (standard)**.
3. **Prepare template:** Select **Template is ready**.
4. **Template source:** Select **Upload a template file**.
5. Click **Choose file** and upload your `0-just-ec2.yaml` file.
   _(Behind the scenes, AWS automatically uploads this file to a hidden S3 bucket so the CloudFormation engine can read it)._
6. Click **Next**.
7. **Stack name:** Enter `EC2InstanceDemo`.
8. Click **Next** through the _Configure stack options_ page (leave all defaults).
9. Click **Submit** on the final review page.

---

## 3. Monitoring the Deployment

Once you hit submit, CloudFormation takes over. You do not need to do anything else.

1. You will be redirected to the **Stack details** page.
2. Click the **Events** tab. You will see a chronological log of what the engine is doing.

- First, you will see the stack status change to `CREATE_IN_PROGRESS`.
- Then, you will see `MyInstance` (your Logical ID) change to `CREATE_IN_PROGRESS`.
- Finally, you will see `MyInstance` change to `CREATE_COMPLETE`.

3. Click the **Resources** tab.

- You will see a link under **Physical ID**.
- The Logical ID (`MyInstance`) is what you called it in your code. The Physical ID (e.g., `i-0abcd1234efgh5678`) is the actual ID AWS assigned to the real server it just built.

4. Click the Physical ID link. It will open a new tab taking you directly to the EC2 console, highlighting your brand new, fully provisioned server!

---

## 4. Automatic Resource Tagging

If you inspect the tags on your new EC2 instance in the console, you will notice three tags you didn't explicitly create:

- `aws:cloudformation:stack-name` (Value: EC2InstanceDemo)
- `aws:cloudformation:logical-id` (Value: MyInstance)
- `aws:cloudformation:stack-id`

AWS automatically injects these tags into every resource provisioned via CloudFormation. This allows you to easily track costs in AWS Billing by filtering for specific Stack Names, and ensures you know exactly which code deployment is responsible for which live server.

> **Cleanup Step:** To destroy this server, **do not** terminate it from the EC2 console. Go back to the CloudFormation console, select the `EC2InstanceDemo` stack, and click **Delete**. CloudFormation will automatically find the EC2 instance it created and terminate it for you.

---

Here is the `boto3` implementation to automate the CloudFormation deployment we just did in the console.

This script demonstrates how to pass your infrastructure as code (the YAML template) directly to the AWS API, use a **Waiter** to pause the script until AWS finishes building the server, and extract the Physical ID of the new instance.

### Prerequisites

Make sure you have `boto3` installed (`pip install boto3`) and your AWS credentials configured.

### The Boto3 Script

```python
import boto3
import botocore.exceptions

# Define variables
region = 'us-east-1'
stack_name = 'EC2InstanceDemo-Boto3'

# The exact YAML template from the hands-on lab
yaml_template = """
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      AvailabilityZone: us-east-1a
      ImageId: ami-0c55b159cbfafe1f0  # Amazon Linux 2023 AMI in us-east-1
      InstanceType: t2.micro
"""

# 1. Initialize the CloudFormation client
cfn_client = boto3.client('cloudformation', region_name=region)

def deploy_stack():
    try:
        print(f"🚀 Deploying CloudFormation stack: '{stack_name}'...")

        # 2. Call the Create Stack API
        cfn_client.create_stack(
            StackName=stack_name,
            TemplateBody=yaml_template
        )

        # 3. Use a Boto3 Waiter to pause the script until deployment is finished
        print("⏳ Waiting for AWS to provision resources (this takes a couple of minutes)...")
        waiter = cfn_client.get_waiter('stack_create_complete')
        waiter.wait(StackName=stack_name)

        print("✅ Stack deployment complete!")

        # 4. Fetch the Physical ID of the created EC2 instance
        response = cfn_client.describe_stack_resources(StackName=stack_name)

        for resource in response['StackResources']:
            if resource['LogicalResourceId'] == 'MyInstance':
                physical_id = resource['PhysicalResourceId']
                print(f"💻 Successfully provisioned EC2 Instance. Physical ID: {physical_id}")

    except botocore.exceptions.ClientError as e:
        print(f"❌ Deployment failed: {e.response['Error']['Message']}")

def destroy_stack():
    """Helper function to clean up resources so you aren't charged."""
    print(f"\n🗑️  Initiating deletion of stack: '{stack_name}'...")
    cfn_client.delete_stack(StackName=stack_name)

    print("⏳ Waiting for AWS to destroy the resources...")
    waiter = cfn_client.get_waiter('stack_delete_complete')
    waiter.wait(StackName=stack_name)
    print("✅ Stack successfully deleted. No more charges!")

if __name__ == "__main__":
    # Deploy the infrastructure
    deploy_stack()

    # Uncomment the line below to automatically destroy the instance after it builds
    # destroy_stack()

```

### Key Boto3 Concepts Used:

1. **`create_stack()`**: This is the equivalent of clicking "Submit" in the console. You pass it the `StackName` and the `TemplateBody` (which expects a raw string of your YAML or JSON code).
2. **Waiters (`get_waiter`)**: CloudFormation deployments are asynchronous. If you run `create_stack()`, AWS returns a success message immediately to acknowledge receipt, but the server is still building in the background. `waiter.wait()` forces your Python script to pause and poll AWS automatically until the stack reaches the `CREATE_COMPLETE` state.
3. **`describe_stack_resources()`**: This allows your script to look inside the deployed stack and map the **Logical ID** (`MyInstance`) from your YAML file to the real-world **Physical ID** (the `i-0abcd...` identifier) of the EC2 instance AWS just created.
