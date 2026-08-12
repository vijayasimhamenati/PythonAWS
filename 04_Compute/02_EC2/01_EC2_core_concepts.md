# EC2 Part 1: The Core Concepts & User Data

## 1. What is Amazon EC2?
**EC2 stands for Elastic Compute Cloud.** It represents the core of **Infrastructure as a Service (IaaS)** on AWS. 

Instead of buying physical hardware, you rent virtual machines (called **EC2 instances**) on-demand. "Elastic" means you can increase or decrease your compute capacity in minutes.

While we often just say "EC2", it is actually an ecosystem composed of several integrated pieces that we will cover in this course:
*   **EC2 Instances:** The virtual machines themselves.
*   **EBS Volumes:** The virtual hard drives attached to the instances.
*   **Elastic Load Balancers (ELB):** Distributing traffic across multiple machines.
*   **Auto Scaling Groups (ASG):** Automatically adding or removing machines based on load.

## 2. Options When Launching an EC2 Instance
When you launch an instance, you are essentially building a custom computer. You must choose:
1.  **Operating System (OS):** Linux (most popular), Windows, or macOS.
2.  **Compute Power (CPU) & Memory (RAM):** How many cores and gigabytes of memory you need.
3.  **Storage Space:** Network-attached storage (EBS) or physically attached hardware storage (Instance Store).
4.  **Network Card:** Fast networking capabilities and Public IP addresses.
5.  **Security Group:** The firewall rules (which ports are open to the internet).
6.  **EC2 User Data:** The bootstrap script.

## 3. EC2 User Data (Bootstrapping)
**Bootstrapping** means launching commands automatically when a machine starts up. 

Instead of launching a blank Linux server, manually SSHing into it, and typing `yum install python3`, you pass a bash script to AWS called the **EC2 User Data**.

**Crucial Rules to Memorize:**
*   The User Data script runs **only ONCE** at the very first launch of the instance. (If you reboot the machine, it does not run again).
*   The script runs with **root (sudo) privileges**. You do not need to type `sudo` before your commands in the script.
*   **Use Cases:** Installing software (Python, Docker, Apache), downloading configuration files from S3, or starting background services.

---

## 💡 Practical Developer Tip (Python / Boto3)

As a developer, clicking through the AWS Console to launch servers is too slow. You can use Python and `boto3` to launch an EC2 instance and pass it a User Data script so it configures itself automatically!

```python
import boto3

# Connect to EC2
ec2 = boto3.resource('ec2', region_name='us-east-1')

# This is our bash script that installs a basic web server
user_data_script = """#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello from Python & Boto3!</h1>" > /var/www/html/index.html
"""

# Launch the instance
instances = ec2.create_instances(
    ImageId='ami-0abcdef1234567890', # An Amazon Linux 2 AMI
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    UserData=user_data_script,       # Pass the script here!
    KeyName='my-ssh-key'
)

print(f"✅ Bootstrapping new EC2 Instance: {instances[0].id}")
```

---

# Interview Preparation: EC2 Basics & User Data

## Summary
Interviewers and exam questions will constantly try to trick you regarding how and when EC2 User Data runs. You must know that it is a one-time execution and runs with full administrative (root) rights.

## Q&A Details

**Q1: We need to ensure that every time an EC2 instance is rebooted or restarted, a specific Python script downloads the latest configuration file from S3. Should we put this script in the EC2 User Data?**
* **Answer:** No. EC2 User Data only executes exactly once during the initial launch (bootstrapping) of the instance. It does not run on subsequent reboots or starts. To run a script on every reboot, we should configure a standard Linux `cron` job (like `@reboot`) or a `systemd` service on the instance.

**Q2: A junior developer complains that their EC2 User Data script is failing to install a software package. Their script looks like this: `apt-get install python3 -y`. They think it's failing because they didn't include `sudo`. Are they correct?**
* **Answer:** No, they are incorrect. EC2 User Data scripts execute by default with `root` privileges, so `sudo` is not required. The script is likely failing for another reason, such as the instance not having internet access to download the package, or the script missing the `#!/bin/bash` shebang at the very top.

**Q3: What is the primary difference between Infrastructure as a Service (IaaS) like EC2, and Platform as a Service (PaaS)?**
* **Answer:** With IaaS like EC2, AWS provides the virtual hardware, but the customer is entirely responsible for patching the Operating System, managing the runtime environment, and configuring the network. With PaaS, AWS manages the underlying OS and runtime, allowing the developer to focus purely on deploying their application code.
