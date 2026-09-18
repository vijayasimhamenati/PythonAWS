# Practical Guide: Authoring CloudFormation Resources

Understanding how to read the AWS documentation is the secret to mastering CloudFormation. You don't need to memorize the properties of all 700+ AWS resources; you just need to know how to declare them and where to find their specific configuration keys.

Because CloudFormation transforms your architecture into plain text, these YAML files belong right alongside your application code in a version-controlled Git repository. Managing your infrastructure with the same professional rigor you apply to your Python scripts ensures clean code practices and provides a perfect historical record of your architecture's evolution.

Let's build a practical template and deploy it using `boto3`.

---

## 1. The Infrastructure as Code (YAML)

We will author a template that provisions an EC2 instance, an Elastic IP, and a Security Group.

Notice that we are opening TCP Port `8000` in the Security Group. This is the default port used by ASGI servers like Uvicorn when running Python backend frameworks like FastAPI.

Save this file locally as `backend-infrastructure.yaml` so it can be committed to your repository.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Provisions a foundational EC2 environment with an Elastic IP and Security Group.

Resources:
  # 1. The Security Group Resource
  BackendSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Allow SSH and typical Python API traffic (Port 8000)
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 8000
          ToPort: 8000
          CidrIp: 0.0.0.0/0

  # 2. The EC2 Instance Resource
  MyInstance:
    Type: AWS::EC2::Instance
    Properties: 
      AvailabilityZone: us-east-1a
      ImageId: ami-0c55b159cbfafe1f0  # Amazon Linux 2023 in us-east-1
      InstanceType: t2.micro
      SecurityGroupIds:
        - !Ref BackendSecurityGroup # References the SG created above

  # 3. The Elastic IP Resource
  MyElasticIP:
    Type: AWS::EC2::EIP
    Properties:
      InstanceId: !Ref MyInstance # Attaches the IP to the EC2 instance

```

---

## 2. The Boto3 Implementation

Instead of hardcoding the YAML string directly into our Python file like we did in previous labs, this `boto3` script is designed to read the `backend-infrastructure.yaml` file from your local disk.

This mimics a real-world continuous deployment script that you might run after pulling the latest commits from your repository.

```python
import boto3
import botocore.exceptions

# Define variables
region = 'us-east-1'
stack_name = 'PythonBackendEnv'
template_file_path = 'backend-infrastructure.yaml'

# Initialize the CloudFormation client
cfn_client = boto3.client('cloudformation', region_name=region)

def read_template(file_path: str) -> str:
    """Reads the YAML template from the local filesystem."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"❌ Error: Could not find the template file at {file_path}")
        exit(1)

def deploy_infrastructure():
    yaml_body = read_template(template_file_path)
    
    try:
        print(f"🚀 Deploying CloudFormation stack: '{stack_name}'...")
        
        # Submit the template to the CloudFormation engine
        cfn_client.create_stack(
            StackName=stack_name,
            TemplateBody=yaml_body
        )
        
        print("⏳ Waiting for AWS to provision resources (VPC, EC2, EIP)...")
        waiter = cfn_client.get_waiter('stack_create_complete')
        waiter.wait(StackName=stack_name)
        
        print("✅ Stack deployment complete!")
        
        # Extract the allocated Elastic IP to show the user
        response = cfn_client.describe_stack_resources(StackName=stack_name)
        for resource in response['StackResources']:
            if resource['ResourceType'] == 'AWS::EC2::EIP':
                print(f"🌐 Infrastructure is live. Elastic IP Physical ID: {resource['PhysicalResourceId']}")
                
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AlreadyExistsException':
            print(f"⚠️  Stack '{stack_name}' already exists. Use update_stack() instead.")
        else:
            print(f"❌ Deployment failed: {e.response['Error']['Message']}")

if __name__ == "__main__":
    deploy_infrastructure()

```

### Key Takeaways for the Exam & Real-World Use:

1. **Resource Block:** The `Resources` block is the absolute minimum requirement for a valid CloudFormation template.
2. **Intrinsic Functions (`!Ref`):** Notice how `!Ref BackendSecurityGroup` is used. CloudFormation inherently understands the dependency graph. It knows it must build the Security Group *first* so that it has an ID to inject into the EC2 instance upon creation.
3. **Custom Resources:** As the lecture mentioned, if you ever need to provision a brand-new AWS service that CloudFormation doesn't natively support yet, or you need to run custom code during a deployment, you would use a **CloudFormation Custom Resource** (which delegates the creation logic to an AWS Lambda function).