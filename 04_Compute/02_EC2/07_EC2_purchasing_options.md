# EC2 Part 4: Purchasing Options

When you launch an EC2 instance, AWS gives you multiple ways to pay for it. As an AWS Developer or Solutions Architect, choosing the right purchasing option is critical because it balances cost against flexibility and availability.

---

## 1. The 7 Purchasing Options

* **On-Demand:** Pay for what you use (per second for Linux/Windows, per hour for others). Highest cost, but zero upfront payment and no long-term commitment.
* **Reserved Instances (RI):** Up to 72% discount. You commit to 1 or 3 years. You reserve specific attributes (instance type, region, OS). Best for steady-state applications like databases.
* **Convertible Reserved Instances:** Up to 66% discount. Similar to RIs, but allows you to change the instance family, OS, or tenancy over time.
* **Savings Plans:** Up to 72% discount. Instead of committing to a specific instance type, you commit to a specific dollar amount per hour (e.g., $10/hour for 1 or 3 years). Any usage beyond that is billed at On-Demand rates. Highly flexible.
* **Spot Instances:** Up to 90% discount. You bid on spare AWS capacity. **Warning:** AWS can reclaim these instances at any time with a 2-minute warning. Best for workloads that are resilient to failure (batch processing, image rendering).
* **Dedicated Hosts:** You book an entire physical server. Required for compliance needs or when you bring your own server-bound software licenses (BYOL - billed per socket/core). Most expensive option.
* **Capacity Reservations:** Reserve capacity in a specific Availability Zone for any duration. You pay the On-Demand rate whether you run the instance or not. No billing discounts, purely for ensuring capacity is there when you need it.

---

## 2. Stephane's "Resort" Analogy

To easily memorize this for the exam, imagine EC2 instances as booking a stay at a resort:

* **On-Demand:** You walk into the resort whenever you want, stay as long as you want, and pay the full rack rate.
* **Reserved:** You plan ahead. You tell the resort, "I will stay for exactly 1 year in the Ocean View suite," so they give you a massive 72% discount.
* **Savings Plan:** You tell the resort, "I promise to spend $300 a month here for the next year. I might sleep in the suite, or I might downgrade to a standard room."
* **Spot Instances:** The resort has empty rooms at the last minute and auctions them off for 90% off. However, if a full-paying customer walks in, the hotel kicks you out of your room immediately!
* **Dedicated Host:** You rent the entire physical hotel building so no other guests can be near you.
* **Capacity Reservation:** You book a room indefinitely. You pay the full nightly rate even if you don't sleep in the bed, just to guarantee nobody else can take it.

---

Use this interactive tool to visualize how these options compare based on your workload characteristics:

---

> 💡 **Practical Developer Tip (Python / Boto3)**
> As a developer, you might want to automate workloads to use **Spot Instances** to save your company money on data processing tasks. Instead of the traditional `request_spot_instances` API, the modern AWS best practice is to use the standard `run_instances` command but pass in `InstanceMarketOptions`.

```python
import boto3

ec2_client = boto3.client('ec2', region_name='us-east-1')

# Launching a Spot Instance to save up to 90% on a temporary background job!
try:
    response = ec2_client.run_instances(
        ImageId='ami-0abcdef1234567890', # Example Amazon Linux 2 AMI
        InstanceType='t3.large',
        MinCount=1,
        MaxCount=1,
        InstanceMarketOptions={
            'MarketType': 'spot',
            'SpotOptions': {
                'SpotInstanceType': 'one-time',
                'InstanceInterruptionBehavior': 'terminate'
            }
        }
    )
    instance_id = response['Instances'][0]['InstanceId']
    print(f"✅ Successfully requested Spot Instance: {instance_id}")

except Exception as e:
    print(f"❌ Failed to request Spot Instance: {e}")

```

---

## Interview Preparation: Purchasing Options

### Summary

The exam will give you a business scenario and ask you to pick the most cost-effective EC2 purchasing option. Look for key phrases:

* "Bring your own license" or "Regulatory compliance" ➡️ **Dedicated Host**
* "Batch processing" or "Can withstand interruptions" ➡️ **Spot Instances**
* "Predictable, steady state 24/7 database" ➡️ **Reserved Instances**
* "Needs to commit to 3 years but wants to change instance families later" ➡️ **Savings Plan** (or Convertible RI)

### Q&A Details

**Q1: We have a nightly data processing job that takes 4 hours to run. If the job fails or is interrupted, it can automatically resume where it left off without data loss. We want to run this as cheaply as possible. Which EC2 purchasing option should we use?**
**Answer:** We should use **Spot Instances**. Because the workload is flexible and resilient to failure, it perfectly matches the Spot model, allowing us to save up to 90% compared to On-Demand pricing. If AWS reclaims the instance, the job will simply resume later when capacity is available.

**Q2: A financial institution is migrating a legacy database to AWS. The database software has strict licensing that bills based on the physical CPU sockets and cores of the underlying server. Which purchasing option is strictly required here?**
**Answer:** **Dedicated Hosts**. Whenever you have server-bound software licenses (BYOL) that rely on underlying physical hardware metrics (like sockets or cores), you must use Dedicated Hosts. Dedicated Instances will not work because they do not provide visibility into or control over the underlying physical server.

**Q3: We have an application running steadily on an `m5.large` instance. We want to commit to a 1-year term to get a discount, but our engineering team plans to migrate the application to a newer compute-optimized `c6g.large` instance in 6 months. What is the most flexible billing option?**
**Answer:** We should purchase an **EC2 Savings Plan** (specifically a Compute Savings Plan) or a Convertible Reserved Instance. A Savings Plan is generally the most modern and flexible choice, as it commits to a dollar amount per hour rather than a specific instance family, allowing the team to freely change instance types and families while still retaining the massive discount.