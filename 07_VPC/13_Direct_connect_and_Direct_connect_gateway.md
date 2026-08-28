# AWS Direct Connect (DX)

While a Site-to-Site VPN is a great way to connect an on-premises network to AWS, it relies on the public internet. The public internet is inherently unpredictable; traffic can be re-routed, latency can spike during peak hours, and bandwidth is shared.

For enterprise workloads that require massive data transfers, consistent millisecond latency, or strict regulatory compliance prohibiting internet transit, AWS offers **Direct Connect (DX)**.

---

## 1. What is Direct Connect?

AWS Direct Connect is a physical, dedicated fiber-optic network connection from your corporate data center directly into an AWS facility. **Traffic never touches the public internet.**

### Key Benefits

- **Massive Bandwidth:** You can provision dedicated connections of 1 Gbps, 10 Gbps, or even 100 Gbps.
- **Predictable Performance:** Because the connection is dedicated and private, latency remains consistently low, making it ideal for real-time data feeds or synchronous database replication.
- **Lower Egress Costs:** AWS charges significantly less for data transferred out of AWS over Direct Connect compared to data transferred over the public internet.

### Virtual Interfaces (VIFs)

Once the physical fiber line is installed, you carve it up logically using Virtual Interfaces (VIFs):

1. **Private VIF:** Used to access your private VPC resources (like EC2 instances or RDS databases). It connects to the **Virtual Private Gateway (VGW)** attached to your VPC.
2. **Public VIF:** Used to access public AWS services (like Amazon S3, DynamoDB, or Glacier) privately over the DX line without going through a VPC or the internet.

---

## 2. Setting Up Direct Connect (The Reality Check)

On AWS Certification exams, they will test your understanding of the **time** it takes to provision Direct Connect.

Setting up DX is not a software configuration you can click through in 5 minutes. It requires physical hardware provisioning. You must work with an AWS Direct Connect Partner (like an ISP or telecom provider) to run a physical fiber cable from your data center to an AWS Direct Connect Location facility.

> **Exam Tip:** Establishing a Direct Connect link typically takes **over a month**. If an exam scenario states, _"We need to securely transfer 50 TB of data to AWS by next week,"_ Direct Connect is the **wrong answer**. (You would use an AWS Snowball device or a Site-to-Site VPN instead).

---

## 3. Direct Connect + VPN (The Security Combo)

Is Direct Connect encrypted? **No.**

Because Direct Connect is a private, dedicated fiber line, AWS assumes it is secure from external interception, so data in transit is sent in plaintext by default.

However, many enterprise security compliance frameworks (like HIPAA or PCI) mandate that _all_ data in transit must be encrypted, even on private leased lines.

To achieve this, you **combine Direct Connect with a Site-to-Site VPN**. You establish the physical DX connection, and then you build an encrypted IPSec VPN tunnel that rides _over_ that dedicated line. This provides the best of both worlds: the consistent latency of DX and the military-grade encryption of a VPN.

---

## 4. Architecting for Resiliency

Direct Connect is a physical cable. Physical cables can be accidentally cut by construction crews, or a network switch can fail. Therefore, you must architect for resiliency. AWS exams test two specific resiliency models:

### High Resiliency (Critical Workloads)

- **Architecture:** You provision **two** separate physical connections terminating at **two** different Direct Connect Locations.
- **Result:** If one physical location experiences an outage, traffic automatically fails over to the second location.

### Maximum Resiliency (Mission Critical Workloads)

- **Architecture:** You provision **four** separate physical connections. You have two active connections terminating at Direct Connect Location A, and two active connections terminating at Direct Connect Location B.
- **Result:** This ensures that even if an entire facility goes down, _and_ a router fails at the backup facility simultaneously, your connectivity remains uninterrupted.

---

## Interview Preparation: Direct Connect

### Summary

Focus on the physical nature of DX, the time it takes to deploy, the difference between Public and Private VIFs, and how to encrypt the connection.

### Q&A Details

**Q1: Our financial institution is migrating a massive, real-time trading database to AWS. The database requires strict millisecond latency, and compliance mandates that all data in transit must be IPSec encrypted. The data center is already equipped with enterprise-grade internet, but we are worried about network jitter. What connectivity solution should we implement?**
**Answer:** You should implement a **Direct Connect** line combined with a **Site-to-Site VPN**. Direct Connect provides the dedicated, low-latency, jitter-free physical connection required for real-time trading. However, because Direct Connect is not encrypted by default, you must establish an IPSec VPN tunnel over the Direct Connect line to satisfy the compliance mandate.

**Q2: A client wants to establish a secure connection between their on-premises network and their AWS VPC. They have a hard deadline to complete the migration and establish connectivity by the end of next week. Should they use AWS Direct Connect or a Site-to-Site VPN?**
**Answer:** They must use a **Site-to-Site VPN**. Because it utilizes the public internet, a VPN can be provisioned and configured in a matter of minutes. AWS Direct Connect involves coordinating with third-party telecom vendors and physically laying fiber optic cable in a colocation facility, a process that almost always takes longer than a month.

**Q3: We have successfully established a Direct Connect connection with a Private VIF to our VPC. Our on-premises servers can access the EC2 instances perfectly. However, the on-premises servers need to upload daily backups to Amazon S3. The traffic to S3 is currently routing out over our regular internet connection instead of the Direct Connect line. How do we fix this?**
**Answer:** To route traffic to Amazon S3 over the Direct Connect line, you must provision a **Public Virtual Interface (Public VIF)** on the existing Direct Connect connection. The Private VIF only allows access to resources within the VPC. The Public VIF provides dedicated access to all AWS public service endpoints (like S3 and DynamoDB) without traversing the internet.

---

# Direct Connect + VPN Backup Architecture

In a previous module, we learned that AWS Direct Connect (DX) provides a dedicated, physical fiber connection from an on-premises data center to an AWS VPC.

However, physical connections can fail. Fiber lines can be accidentally severed by construction equipment, or a router at the DX location could experience a hardware failure.

To ensure high availability, you must have a backup plan.

---

## 1. The Cost-Effective Backup Strategy

If you require **maximum resiliency** with zero tolerance for internet jitter, the solution is to purchase multiple, redundant Direct Connect lines terminating at different physical locations. However, this is incredibly expensive.

A highly common, cost-effective alternative heavily tested on AWS exams is the **Direct Connect + Site-to-Site VPN Backup** architecture.

### How It Works

1. **The Primary Path:** You establish an AWS Direct Connect link. Because it offers the highest bandwidth and lowest latency, you configure your on-premises routers (using BGP routing protocols) to heavily prefer this path. This carries 100% of your production traffic under normal circumstances.
2. **The Secondary Path:** You configure a standard AWS Site-to-Site VPN connection to the exact same Virtual Private Gateway (VGW) in AWS. You configure the routing metrics so this path is treated as the "least preferred" backup route.
3. **The Failover:** If the physical Direct Connect fiber line is cut, the BGP routing protocol detects the failure. It automatically stops attempting to send traffic over the DX line and instantly fails over to the Site-to-Site VPN tunnel. Traffic now routes securely over the public internet until the fiber line is repaired.

---

---

## Interview Preparation: Hybrid Failover

### Summary

When an exam scenario asks for a highly available hybrid network connection that balances reliability with cost-effectiveness, look for the combination of **Direct Connect** (Primary) and **Site-to-Site VPN** (Secondary/Backup).

### Q&A Details

**Q1: We are architecting a hybrid cloud environment for a hospital. The primary requirement is a dedicated, 10 Gbps connection to transfer medical imagery. However, the budget is tight, and the CIO refuses to approve the cost of a secondary 10 Gbps dedicated line for redundancy. What is the most cost-effective way to provide an automated backup connection in case the primary line fails?**
**Answer:** The most cost-effective architecture is to configure an **AWS Site-to-Site VPN** as a backup connection. You would establish the primary 10 Gbps Direct Connect line and a secondary IPSec VPN tunnel over the hospital's existing public internet connection. By configuring BGP routing weights, traffic will automatically failover to the encrypted VPN tunnel if the Direct Connect link goes offline, providing redundancy at a fraction of the cost of a second dedicated line.
