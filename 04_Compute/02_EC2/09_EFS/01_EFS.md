# 1. Core Concepts & Characteristics

* **Multi-AZ by Default:** EFS is highly available and scalable. You can have web servers in `us-east-1a`, `us-east-1b`, and `us-east-1c` all reading and writing to the exact same EFS drive at the same time.
* **Linux Only:** EFS uses the standard Linux POSIX file system. It is not compatible with Windows EC2 instances (for Windows, you must use Amazon FSx for Windows File Server).
* **Pay-per-use:** Unlike EBS (where you provision a 50GB drive and pay for 50GB even if it's empty), EFS has no provisioned capacity. If you put 1 GB of data in it, you pay for 1 GB. If it grows to 100 TB, it scales automatically.
* **Cost:** Because it is highly available and scalable, it is expensive. EFS is roughly 3x the cost of a standard `gp2` EBS volume.

---

## 2. EFS Performance & Throughput Modes

When you create an EFS system, you must configure how it performs.

### Performance Modes

* **General Purpose (Default):** Best for 99% of workloads (web servers, content management systems, general file sharing). It provides the lowest possible latency.
* **Max I/O:** Best for highly parallelized workloads (Big Data, media processing) where hundreds of servers are hammering the drive. It provides massive throughput but at the cost of slightly higher latency.

### Throughput Modes

* **Elastic (Recommended):** The default and most modern setting. The throughput automatically scales up and down based entirely on your workload. You only pay for the exact data read/written. Perfect for unpredictable workloads.
* **Provisioned:** You explicitly specify the throughput you need (e.g., "Give me 1 GB/s") regardless of how much data is stored on the drive. You pay a high premium for this guaranteed speed.
* **Bursting (Legacy):** Throughput scales directly with storage size (e.g., 1 TB of storage = 50 MB/s baseline throughput).

---

## 3. Storage Classes & Lifecycle Management

To offset the high cost of EFS, AWS provides automated lifecycle policies to move older files to cheaper storage tiers.

* **Standard:** For frequently accessed, hot data. Highest cost.
* **Infrequent Access (EFS-IA):** For data you rarely access (but need immediately when requested). It is significantly cheaper to store files here, but you are charged a fee every time you retrieve a file.
* **Archive:** For very cold data. The absolute lowest storage cost.

> **Lifecycle Policies:** You can tell AWS: "If a file in Standard is not touched for 30 days, automatically move it to EFS-IA. If it's not touched for 90 days, move it to Archive. If someone opens an archived file, move it back to Standard."

---

---

## 4. EFS Network Security (Security Groups)

Just like EC2 instances, EFS is secured by Security Groups.
To allow an EC2 instance to talk to EFS, you must create an **Inbound Rule** on the EFS Security Group that allows NFS traffic (**Port 2049**) from the EC2 instance's Security Group.

---

> 💡 **Practical Developer Tip (Python / Boto3)**
> As a developer, you might need to build an EFS drive using Python so multiple servers can share processing logs.
> Here is how you provision a scalable EFS file system using Boto3:

```python
import boto3

efs_client = boto3.client('efs', region_name='us-east-1')

try:
    response = efs_client.create_file_system(
        PerformanceMode='generalPurpose',
        ThroughputMode='elastic', # The recommended setting!
        Encrypted=True,           # Always encrypt your data at rest
        Tags=[
            {
                'Key': 'Name',
                'Value': 'SharedApplicationLogs'
            }
        ]
    )
    
    fs_id = response['FileSystemId']
    print(f"✅ Successfully provisioned EFS File System: {fs_id}")

except Exception as e:
    print(f"❌ Failed to create EFS: {e}")

```

---

## Interview Preparation: EFS vs. EBS

### Summary

The absolute most common exam and interview question is choosing between EBS and EFS.

**The Golden Rule:**

* If the scenario mentions "Multiple EC2 instances sharing files simultaneously," the answer is **EFS**.
* If the scenario mentions "A single EC2 instance needs a high-performance database drive," the answer is **EBS**.
* If the scenario mentions "Windows servers sharing files," the answer is **FSx**.

### Q&A Details

**Q1: Our company has an Auto Scaling Group of Linux web servers that dynamically spin up and down based on traffic. They all need to read images from the exact same shared directory. Should we use an EBS Multi-Attach `io2` volume or EFS?**
**Answer:** We must use **Amazon EFS**. EBS Multi-Attach is limited to a single Availability Zone and a maximum of 16 instances. Because Auto Scaling Groups dynamically scale across multiple AZs, and potentially beyond 16 instances, a highly available network file system like EFS is the only valid architectural choice.

**Q2: We are migrating a massive legacy application to AWS. The application generates unpredictable bursts of log files to a shared directory. We need the storage size to automatically scale indefinitely without us ever provisioning gigabytes in advance. What storage service meets these criteria?**
**Answer:** **Amazon EFS**. Unlike EBS, which requires you to manually provision the exact capacity in advance (e.g., paying for a 500GB drive), EFS is completely elastic. It automatically scales as files are added or removed, and you only pay for the storage you actually consume. We should also configure the throughput mode to 'Elastic' to handle the unpredictable bursts.

**Q3: A developer attempts to mount an EFS file system to a brand new Amazon Linux 2 EC2 instance, but the mount command simply hangs and eventually times out. The EFS drive is in the same VPC. What is the most likely cause?**
**Answer:** A "timeout" almost always points to a firewall issue. The developer likely forgot to configure the Security Group attached to the EFS file system. The EFS Security Group must have an Inbound Rule allowing **NFS traffic (Port 2049)**, and the source of that rule should be set to the Security Group ID of the EC2 instance.