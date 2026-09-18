# Practical Guide: Updating and Deleting CloudFormation Stacks

In this hands-on lab, we will take our existing CloudFormation stack (which currently only contains a single, basic EC2 instance) and update it. We will add an Elastic IP, attach two custom Security Groups, and introduce dynamic Parameters.

Finally, we will demonstrate the correct way to delete infrastructure to avoid orphaned resources and runaway costs.

---

## 1. The Updated YAML Template

Save the following code as `1-ec2-with-sg-eip.yaml` on your local machine.

```yaml
---
Parameters:
  SecurityGroupDescription:
    Description: Security Group Description
    Type: String

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      AvailabilityZone: us-east-1a
      ImageId: ami-0453ec754f44f9a4a
      InstanceType: t3.micro
      SecurityGroups:
        - !Ref SSHSecurityGroup
        - !Ref ServerSecurityGroup

  # an elastic IP for our instance
  MyEIP:
    Type: AWS::EC2::EIP
    Properties:
      InstanceId: !Ref MyInstance

  # our EC2 security group
  SSHSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Enable SSH access via port 22
      SecurityGroupIngress:
        - CidrIp: 0.0.0.0/0
          FromPort: 22
          IpProtocol: tcp
          ToPort: 22

  # our second EC2 security group
  ServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: !Ref SecurityGroupDescription
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 192.168.1.1/32

Outputs:
  ElasticIP:
    Description: Elastic IP Value
    Value: !Ref MyEIP
...
```

### Code Breakdown:

* **`Parameters:`** We added a parameter block. This allows the user to input a custom string when they run the template in the console. We reference this parameter later in the `ServerSecurityGroup` using the intrinsic function `!Ref`.
* **`MyElasticIP:`** We declared an Elastic IP. Notice how we use `!Ref MyInstance`. This tells CloudFormation: "Create this IP, wait for the EC2 instance to be built, get the EC2 instance's ID, and attach the IP to it."
* **`SecurityGroupIds:`** We modified the EC2 instance configuration to explicitly attach the two new security groups we are creating at the bottom of the file.

---

## 2. Updating the Stack & The Change Set

You cannot edit the YAML code directly inside the AWS Console. You must update your local file and upload the new version.

1. Navigate to the **CloudFormation Console**.
2. Select the `EC2InstanceDemo` stack you created in the previous lab.
3. Click **Update**.
4. Select **Replace current template** > **Upload a template file**.
5. Upload the `1-ec2-with-sg-eip.yaml` file and click **Next**.
6. **Specify stack details:** You will now see a text box for `SecurityGroupDescription`. This is the Parameter we defined! You can change the text or leave the default. Click **Next**.
7. Click **Next** through the options page.
8. **The Change Set Preview:** Scroll to the very bottom of the Review page. CloudFormation provides a **Change set preview**. This is a critical feature that tells you exactly what the engine is about to do *before* it does it.
* You will see **Add** actions for the Elastic IP and the two Security Groups.
* Look closely at the `MyInstance` row. Under the "Replacement" column, it says **True**.



### Understanding "Replacement: True" (Exam Focus)

Why is the EC2 instance being replaced instead of just updated?
In AWS, certain properties of a resource are immutable (they cannot be changed after creation). If you update a CloudFormation template to change an immutable property, CloudFormation has no choice but to **terminate the existing resource and create a brand new one from scratch** to apply the change.

In this lab, we altered the Security Group attachment at launch, which triggered the replacement logic for the EC2 instance.

9. Click **Submit**.

---

## 3. Monitoring the Update

Navigate to the **Events** tab. You will see CloudFormation executing a complex orchestration dance:

1. It creates the two new Security Groups.
2. It provisions a *brand new* EC2 instance (because of the `Replacement: True` flag).
3. It provisions the Elastic IP and attaches it to the *new* EC2 instance.
4. It waits for the new instance to pass health checks.
5. Finally, it issues a termination signal to the *old* EC2 instance and deletes it.

The stack update is complete when the status reads `UPDATE_COMPLETE`.

---

## 4. Deleting the Stack (The Right Way)

If you manually went into the EC2 console and terminated the instance, the Elastic IP and Security Groups would be left behind as orphaned resources, continuing to incur charges on your bill.

Because CloudFormation built this environment, CloudFormation must destroy it.

1. In the CloudFormation console, ensure the `EC2InstanceDemo` stack is selected.
2. Click **Delete**.
3. Confirm the deletion.

Watch the **Events** tab one last time. CloudFormation will determine the correct deletion order (e.g., detaching the Elastic IP, terminating the EC2 instance, then deleting the Security Groups) and wipe the slate clean. When the stack disappears from your list, you are guaranteed that all associated resources have been destroyed and you will not be billed.

---

## 5. Boto3 Implementation

Here is how you execute a Stack Update and a clean Deletion using `boto3`.

```python
import boto3
import botocore.exceptions
import time

region = 'us-east-1'
stack_name = 'EC2InstanceDemo-Boto3'

# The updated YAML template
updated_yaml = """
Parameters:
  SecurityGroupDescription:
    Type: String
    Default: "Updated via Boto3"

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties: 
      AvailabilityZone: us-east-1a
      ImageId: ami-0c55b159cbfafe1f0
      InstanceType: t2.micro
      SecurityGroupIds:
        - !Ref SSHSecurityGroup
        - !Ref ServerSecurityGroup

  MyElasticIP:
    Type: AWS::EC2::EIP
    Properties:
      InstanceId: !Ref MyInstance

  SSHSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Allow SSH inbound
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0

  ServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: !Ref SecurityGroupDescription
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
"""

cfn_client = boto3.client('cloudformation', region_name=region)

def update_stack():
    try:
        print(f"🔄 Initiating update for stack: '{stack_name}'...")
        
        # Call the Update Stack API
        # Note: We pass the Parameter dynamically at runtime here!
        cfn_client.update_stack(
            StackName=stack_name,
            TemplateBody=updated_yaml,
            Parameters=[
                {
                    'ParameterKey': 'SecurityGroupDescription',
                    'ParameterValue': 'This description was injected by the Python script!'
                }
            ]
        )
        
        print("⏳ Waiting for AWS to apply updates (Replacement: True takes a few minutes)...")
        waiter = cfn_client.get_waiter('stack_update_complete')
        waiter.wait(StackName=stack_name)
        
        print("✅ Stack update complete!")
        
    except botocore.exceptions.ClientError as e:
        error_message = e.response['Error']['Message']
        if 'No updates are to be performed' in error_message:
            print("ℹ️  No changes detected in the template.")
        else:
            print(f"❌ Update failed: {error_message}")

def clean_deletion():
    """Safely destroy all resources tracked by the stack."""
    print(f"\n🗑️  Initiating clean deletion of stack: '{stack_name}'...")
    try:
        cfn_client.delete_stack(StackName=stack_name)
        
        print("⏳ Waiting for AWS to destroy the resources...")
        waiter = cfn_client.get_waiter('stack_delete_complete')
        waiter.wait(StackName=stack_name)
        print("✅ Stack successfully deleted. No orphaned resources left behind!")
        
    except botocore.exceptions.ClientError as e:
        print(f"❌ Deletion failed: {e.response['Error']['Message']}")

if __name__ == "__main__":
    # 1. Update the existing stack
    update_stack()
    
    # Optional: Pause before deleting so you can verify the resources in the AWS Console
    # print("Sleeping for 60 seconds. Go check the AWS Console!")
    # time.sleep(60)
    
    # 2. Cleanly delete the stack
    clean_deletion()

```