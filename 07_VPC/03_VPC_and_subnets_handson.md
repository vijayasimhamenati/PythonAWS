# Practical Guide: Creating a VPC and Subnets

In this hands-on guide, we will walk through the process of building a foundational network architecture in AWS from scratch. We will create a Virtual Private Cloud (VPC) and provision multiple subnets across different Availability Zones.

## 1. Creating the Custom VPC

A VPC acts as your isolated, logical data center within an AWS Region.

1. Navigate to the **VPC Console** and select **Your VPCs**.
2. Click **Create VPC** (Choose the _VPC only_ option to build step-by-step, rather than using the VPC wizard).
3. **Name Tag:** Enter `DemoVPC`.
4. **IPv4 CIDR block:** Enter `10.0.0.0/16`.

- _Note:_ A `/16` is the maximum allowed size for an AWS VPC, providing 65,536 IP addresses (from `10.0.0.0` to `10.0.255.255`).

5. **IPv6 CIDR block:** Select **No IPv6 CIDR block**.
6. **Tenancy:** Leave as **Default**. (Dedicated tenancy ensures your instances run on single-tenant hardware, which is significantly more expensive).
7. Click **Create VPC**.

### Expanding VPC CIDRs

Once created, your VPC has a primary CIDR block. If you need more IP addresses later, you can select the VPC, click **Actions > Edit CIDRs**, and associate up to four additional secondary IPv4 CIDR blocks (e.g., adding `10.1.0.0/16`).

---

## 2. Understanding Subnet Constraints

Before we create subnets inside our `DemoVPC`, you must understand how AWS handles IP allocation within them.

### The 5 Reserved IPs Rule (Exam Focus!)

AWS reserves exactly **five IP addresses** in every single subnet you create. They are always the first four IPs and the last IP in the block.

For example, in the subnet `10.0.0.0/24` (which mathematically holds 256 IPs):

1. `10.0.0.0`: Network Address.
2. `10.0.0.1`: Reserved for the VPC Router.
3. `10.0.0.2`: Reserved for the Amazon-provided DNS.
4. `10.0.0.3`: Reserved by AWS for future use.
5. `10.0.0.255`: Network Broadcast Address (AWS doesn't support broadcast, but reserves the IP).

> **Scenario:** If you need exactly 29 IP addresses for EC2 instances, a `/27` subnet (32 IPs) is **too small** because `32 - 5 = 27 usable IPs`. You must provision a `/26` subnet (64 IPs).

---

## 3. Creating the Subnets

We will create four non-overlapping subnets (two public, two private) spanning two different Availability Zones to ensure high availability.

Navigate to **Subnets** in the VPC console and click **Create subnet**. Select your `DemoVPC` from the dropdown.

### A. The Public Subnets

Public subnets are typically kept smaller (e.g., `/24` providing 251 usable IPs) as they usually only host load balancers, NAT Gateways, or bastion hosts.

1. **Subnet 1:**

- **Name:** `PublicSubnetA`
- **Availability Zone:** Select the first AZ (e.g., `eu-central-1a`).
- **IPv4 CIDR block:** `10.0.0.0/24`

2. **Subnet 2:**

- **Name:** `PublicSubnetB`
- **Availability Zone:** Select the second AZ (e.g., `eu-central-1b`).
- **IPv4 CIDR block:** `10.0.1.0/24` (This picks up right where Subnet A ended at `.0.255`).

### B. The Private Subnets

Private subnets are usually much larger (e.g., `/20` providing 4,091 usable IPs) because they host the bulk of your application: web servers, application servers, and databases.

3. **Subnet 3:**

- **Name:** `PrivateSubnetA`
- **Availability Zone:** Select the first AZ (e.g., `eu-central-1a`).
- **IPv4 CIDR block:** `10.0.16.0/20` (This range goes from `.16.0` to `.31.255`).

4. **Subnet 4:**

- **Name:** `PrivateSubnetB`
- **Availability Zone:** Select the second AZ (e.g., `eu-central-1b`).
- **IPv4 CIDR block:** `10.0.32.0/20` (The next available `/20` block).

Click **Create subnets**. If your CIDR blocks do not overlap, they will be created successfully.

### Verifying the Setup

If you look at the Subnets dashboard, you will notice the "Available IPv4 addresses" column displays exactly **5 fewer IPs** than the mathematical size of the CIDR block (e.g., the `/24` subnets will show 251 available, and the `/20` subnets will show 4,091 available).

_Note: At this stage, all four subnets are technically identical. In the next steps, we will configure Internet Gateways and Route Tables to dictate which of these subnets act as "Public" and which act as "Private."_

---

💡 Practical Developer Tip (Python / Boto3)

As a developer, writing infrastructure as code means you don't click around the console to build networks. Here is how you can use Python to programmatically create a VPC and a Subnet!

```python

import boto3

# Create the EC2/VPC client
ec2_client = boto3.client('ec2', region_name='us-east-1')

try:
    print("🚀 Creating a new VPC...")
    # 1. Create the VPC
    vpc_response = ec2_client.create_vpc(
        CidrBlock='10.0.0.0/16',
        TagSpecifications=[
            {'ResourceType': 'vpc', 'Tags': [{'Key': 'Name', 'Value': 'DemoVPC-Python'}]}
        ]
    )
    vpc_id = vpc_response['Vpc']['VpcId']
    print(f"✅ Successfully created VPC: {vpc_id}")

    # 2. Create a Subnet inside that VPC
    print(f"🚀 Creating a Subnet in {vpc_id}...")
    subnet_response = ec2_client.create_subnet(
        VpcId=vpc_id,
        CidrBlock='10.0.1.0/24',
        AvailabilityZone='us-east-1a',
        TagSpecifications=[
            {'ResourceType': 'subnet', 'Tags': [{'Key': 'Name', 'Value': 'PublicSubnet-A'}]}
        ]
    )
    subnet_id = subnet_response['Subnet']['SubnetId']
    print(f"✅ Successfully created Subnet: {subnet_id}")

except Exception as e:
    print(f"❌ Failed to provision network: {e}")
```

# Interview Preparation: VPCs & Subnets

## Summary

Interviewers will test your understanding of network boundaries. You must articulate that VPCs are regional, but subnets are bound to specific Availability Zones. The "minus 5" IP rule is a classic technical screen question to ensure you have practical experience.

## Q&A Details

**Q1: We are architecting a new application that will be deployed in the `eu-west-1` (Ireland) region. To ensure high availability, the senior architect requests that we span our VPC across the `eu-west-1` and `eu-central-1` (Frankfurt) regions. Is this possible?**

- **Answer:** No, that is not possible. A VPC is fundamentally bound to a single AWS Region. To achieve the architect's goal, we would need to create two separate VPCs—one in Ireland and one in Frankfurt—and then connect them using a technology like VPC Peering or AWS Transit Gateway.

**Q2: We need to provision a private subnet specifically for our backend database cluster. We anticipate needing exactly 14 IP addresses for the database nodes. A junior engineer suggests creating a `/28` subnet, which contains 16 IP addresses. Is this a valid configuration?**

- **Answer:** No, the junior engineer's suggestion will fail. While a `/28` block mathematically contains 16 IP addresses, AWS automatically reserves 5 IP addresses in every subnet for routing, DNS, and broadcast purposes. This leaves only 11 usable IP addresses, which is insufficient for the 14 required nodes. We must provision a `/27` subnet instead.

**Q3: When configuring the CIDR block for a brand new VPC, what is the most critical consideration regarding the chosen IP range?**

- **Answer:** The most critical consideration is to ensure that the chosen CIDR block does not overlap with any existing corporate on-premises networks or other AWS VPCs. If IP ranges overlap, routing conflicts will occur, making it impossible to establish private network connections (like VPNs, Direct Connect, or VPC Peering) between the environments in the future.
