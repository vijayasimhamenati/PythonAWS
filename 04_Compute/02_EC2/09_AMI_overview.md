# EC2 AMIs & Instance Store

## 1. Amazon Machine Images (AMI)

An **AMI** is essentially a blueprint or a snapshot of an entire EC2 instance's root drive (Operating System + any installed software) saved at a specific point in time.

**Why Use AMIs?**
In previous configurations, you might use an EC2 User Data script to install an Apache web server when the instance booted. That takes 2-3 minutes.

* **The Problem:** If you need to instantly scale up 100 web servers to handle a traffic spike, waiting 3 minutes for each one to download and install software is too slow.
* **The Solution (Golden AMI):** You boot one server, let the User Data script install everything, and then create an AMI from that server. Any new instances you launch from that custom AMI will boot up almost instantly with the web server already installed!

**AMI Key Facts:**

* AMIs are **Regionally scoped**. If you create an AMI in `us-east-1`, it cannot be directly used to launch instances in `eu-west-1`. You must first copy the AMI to the target region.
* You can use AMIs provided by AWS (like Amazon Linux 2), AMIs you create yourself, or AMIs bought from the AWS Marketplace.

---

## 2. EC2 Instance Store (The Need for Speed)

We know that EBS Volumes are network-attached drives. They are durable, and your data survives if the instance stops. However, because they use the network, there is an inherent speed limit (latency).

*What if you have a massive caching application or a NoSQL database that requires millions of operations per second (IOPS) with zero latency?*

**Enter the Instance Store**
An EC2 Instance Store is a physical hard drive directly, physically bolted onto the motherboard of the host server running your virtual EC2 instance.

* **Extreme Performance:** Because it is physically attached, you get millions of IOPS and maximum throughput.
* **The Catch (Ephemeral Storage):** The storage is strictly temporary. If you STOP or TERMINATE your EC2 instance, you lose all the data on the Instance Store permanently. *(Data does survive a standard OS reboot, however).*
* **No Backups:** Unlike EBS, you cannot take an EBS Snapshot of an Instance Store.
* **Your Responsibility:** If the underlying hardware fails, your data is gone. You are completely responsible for building replication or backup mechanisms into your application if you use Instance Store.

---

## EBS vs. Instance Store (Exam Cheat Sheet)

| Feature | Elastic Block Store (EBS) | EC2 Instance Store |
| --- | --- | --- |
| **Attachment** | Network-attached | Physically attached (Hardware) |
| **Performance** | High (but network-limited) | Extreme (Millions of IOPS) |
| **Durability** | Persistent (Data survives stop) | Ephemeral (Data lost on stop) |
| **Backups** | Native EBS Snapshots | None (Your responsibility) |
| **Best For** | Databases, OS drives, general data | Caches, buffers, temporary scratch data |

---

> 💡 **Practical Developer Tip (Python / Boto3)**
> As a developer, you might need to find the latest "Golden AMI" your DevOps team created for your region before launching a server. You can use Python to search for the most recent AMI by name!

```python
import boto3

ec2 = boto3.client('ec2', region_name='us-east-1')

# Search for our custom Web Server AMIs
response = ec2.describe_images(
    Owners=['self'], # Only look at AMIs we own
    Filters=[
        {
            'Name': 'name',
            'Values': ['DemoImage-WebServer-*']
        }
    ]
)

# Sort them by creation date to find the newest one
images = response['Images']
images.sort(key=lambda x: x['CreationDate'], reverse=True)

if images:
    latest_ami_id = images[0]['ImageId']
    print(f"✅ Found the latest Golden AMI: {latest_ami_id}")
else:
    print("❌ No matching AMIs found.")

```

---

## Interview Preparation: AMIs & Instance Store

### Summary

Interviewers (and exam questions) will almost always test your knowledge of Instance Store vs. EBS. If they mention "millions of IOPS" or "temporary cache," they want you to say **Instance Store**. If they mention "data must survive a server stop," they want **EBS**.

### Q&A Details

**Q1: We have an application that processes massive amounts of temporary scratch data, requiring over 1 million IOPS with virtually zero latency. If the server is stopped or crashes, we don't care if the scratch data is lost. What EC2 storage option should we use?**
**Answer:** We should use an EC2 Instance Store. Because the data is temporary and requires extreme IOPS and minimal latency, physically attached hardware storage (Instance Store) is the perfect fit. EBS would be too slow due to network latency overhead.

**Q2: A junior developer created a custom AMI in the `us-west-2` (Oregon) region containing our proprietary application. They are trying to use an Auto Scaling Group to launch instances in `eu-central-1` (Frankfurt) using that AMI ID, but it keeps failing. Why?**
**Answer:** AMIs are bounded by the AWS Region they are created in. The AMI ID created in `us-west-2` simply does not exist in `eu-central-1`. The developer must first initiate an AMI Copy operation to copy the image to the Frankfurt region, which will generate a brand new, region-specific AMI ID for the Auto Scaling Group to use.

**Q3: We are running a PostgreSQL database on an EC2 instance. The database requires extreme IOPS, so the engineer suggests putting the database data files on an EC2 Instance Store. Why is this a terrible architectural decision?**
**Answer:** EC2 Instance Store is ephemeral storage. If the EC2 instance is ever stopped, or if the underlying hardware host fails, all data on the Instance Store is immediately and permanently lost. For a database requiring persistent, durable data, we must use high-performance EBS volumes (like `io2` Block Express) instead.