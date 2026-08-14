# EC2 Storage: EBS Volume Types (SSD vs. HDD)

When creating an EBS volume, you must choose a volume type. AWS categorizes these into **Solid State Drives (SSD)** for transactional workloads (like databases) and **Hard Disk Drives (HDD)** for streaming workloads (like big data).

---

## 1. The Golden Rule of Boot Volumes

Before diving into the types, memorize this absolute rule for the AWS exams:

> **Only SSD volumes (`gp2`, `gp3`, `io1`, `io2`) can be used as Boot Volumes** (the drive where your Operating System lives). You cannot boot an EC2 instance from an HDD (`st1`, `sc1`).

---

## 2. General Purpose SSD (gp2 vs gp3)

These are your daily drivers. They balance price and performance for a wide variety of workloads (virtual desktops, test environments, standard web servers).

* **gp2 (Older Generation):**
* The size of the drive and its speed are mathematically linked.
* If you want more IOPS (Input/Output Operations Per Second), you must buy a larger drive, maxing out at 16,000 IOPS (at around 5.3 TB).


* **gp3 (Newer Generation & Recommended):**
* Provides a baseline of 3,000 IOPS and 125 MB/s throughput regardless of how small the drive is.
* **The Killer Feature:** You can scale IOPS (up to 16,000) and throughput (up to 1,000 MB/s) independently from the storage capacity. It is usually 20% cheaper than `gp2`.



---

## 3. Provisioned IOPS SSD (io1 & io2 Block Express)

These are the absolute highest-performance drives AWS offers. Use these for mission-critical, low-latency, or high-throughput workloads (like a massive, heavy-traffic production database).

* **io1:**
* Allows you to provision exactly the IOPS you need independently of storage size.
* Max IOPS: 64,000 (if attached to a specialized EC2 Nitro instance) or 32,000 on standard instances.


* **io2 Block Express:**
* The ultimate sports car of EBS.
* Delivers sub-millisecond latency.
* Max IOPS: A staggering 256,000 IOPS.
* Storage: Can go up to 64 TB.


* **EBS Multi-Attach:** Only `io1` and `io2` volumes support being attached to multiple EC2 instances simultaneously within the same Availability Zone.

---

## 4. Hard Disk Drives (HDD)

HDDs are optimized for throughput (streaming large sequential files) rather than IOPS (quick, random reads/writes). They **cannot** be boot volumes.

* **st1 (Throughput Optimized HDD):**
* Great for Big Data, Data Warehousing, and Log Processing.
* Max throughput is 500 MB/s.


* **sc1 (Cold HDD):**
* The absolute lowest-cost EBS volume.
* Designed for archive data that is infrequently accessed.



---

---

> 💡 **Practical Developer Tip (Python / Boto3)**
> One of the greatest features of AWS is that you can change an EBS volume type on the fly without stopping the EC2 instance!
> If your company is wasting money on older `gp2` volumes, you can write a Python script to instantly upgrade them to `gp3` to save 20% and get independent IOPS scaling.

```python
import boto3

ec2 = boto3.client('ec2', region_name='us-east-1')

# The ID of the old gp2 volume you want to upgrade
volume_id = 'vol-0abcd1234efgh5678'

try:
    # Modify the volume to gp3 on the fly!
    response = ec2.modify_volume(
        VolumeId=volume_id,
        VolumeType='gp3',
        Iops=3000, # Baseline gp3 IOPS
        Throughput=125 # Baseline gp3 Throughput in MB/s
    )
    
    print(f"✅ Volume {volume_id} is successfully migrating to gp3!")
    print(f"Current State: {response['VolumeModification']['ModificationState']}")

except Exception as e:
    print(f"❌ Failed to modify volume: {e}")

```

---

## Interview Preparation: EBS Volume Types

### Summary

The exam will not ask you to memorize exact megabytes per second. Instead, it will give you a business requirement and ask you to pick the correct volume prefix (`gp3`, `io2`, `st1`, `sc1`).

**Keyword Cheat Sheet:**

* "More than 16,000 IOPS" or "Mission critical database" ➡️ **`io1` or `io2**`
* "Cost-effective baseline" or "Independent scaling" ➡️ **`gp3`**
* "Big Data" or "Data Warehousing" or "Log processing" ➡️ **`st1`**
* "Lowest cost" or "Infrequently accessed" ➡️ **`sc1`**

### Q&A Details

**Q1: We are deploying a new PostgreSQL database on EC2 that requires 25,000 IOPS to handle peak traffic. The storage size only needs to be 500 GB. Which EBS volume type should we choose?**
**Answer:** We must use Provisioned IOPS SSD (`io1` or `io2`). General Purpose SSDs (`gp2`/`gp3`) max out at a hard limit of 16,000 IOPS. Because our requirement exceeds that limit, we have to use Provisioned IOPS volumes, which support up to 64,000 or 256,000 IOPS.

**Q2: We need to provision a massive 10 TB volume to hold server access logs. The data is written sequentially and we need high throughput, but we want to keep costs as low as possible. What volume type is best?**
**Answer:** Throughput Optimized HDD (`st1`). Since this volume is for log processing and sequential writes, an HDD is the perfect fit. `st1` provides the necessary high throughput for big data and logging at a much lower cost per GB than an SSD.

**Q3: A developer wants to migrate a legacy operating system to AWS. They provision a `t3.large` instance and attempt to attach a Cold HDD (`sc1`) as the primary boot volume to save money, but the launch fails. Why?**
**Answer:** HDD volumes (`st1` and `sc1`) cannot be used as boot volumes (root volumes) for EC2 instances. Boot volumes require the random read/write capabilities of an SSD. The developer must change the boot volume to `gp2` or `gp3`.