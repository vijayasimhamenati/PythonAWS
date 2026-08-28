# AWS VPC Endpoints: Private Access to AWS Services

When an EC2 instance in a private subnet needs to access a public AWS service—like Amazon S3, DynamoDB, or SNS—the default behavior is to route that traffic through a NAT Gateway and out to the public internet.

**The Problem:**

1. **Cost:** Data processed through a NAT Gateway incurs a per-GB charge.
2. **Security:** Even though the traffic is encrypted (HTTPS), it still leaves the AWS private network and traverses the public internet before hitting the AWS service endpoint.

**The Solution:**
**VPC Endpoints** allow you to connect your VPC directly to supported AWS services using the private AWS network. Traffic never leaves the AWS backbone, completely bypassing the need for a NAT Gateway or an Internet Gateway.

---

## 1. Gateway Endpoints vs. Interface Endpoints

AWS provides two entirely different types of VPC Endpoints. Understanding the difference is heavily tested on certification exams.

### Type 1: Gateway Endpoints

Gateway Endpoints function at the routing layer.

- **How it works:** You create the endpoint and simply add it as a "Target" in your Route Table.
- **Supported Services:** It supports exactly two services: **Amazon S3** and **Amazon DynamoDB**. _(Memorize this!)_
- **Network Layer:** It does NOT use an IP address and does NOT use Security Groups.
- **Cost:** **Completely Free.**

### Type 2: Interface Endpoints (AWS PrivateLink)

Interface Endpoints function at the network interface layer.

- **How it works:** AWS provisions an Elastic Network Interface (ENI) directly inside your subnet. This ENI gets a private IP address from your subnet's CIDR block. Your applications send traffic directly to this private IP.
- **Supported Services:** It supports almost every other AWS service (SNS, SQS, CloudWatch, Kinesis, etc.), as well as third-party SaaS applications hosted on AWS.
- **Network Layer:** Because it uses an ENI, you **MUST** attach a Security Group to it to control inbound traffic.
- **Cost:** You are charged an hourly rate per endpoint, plus a per-GB data processing fee.

---

## 2. The Amazon S3 Dilemma

Amazon S3 is unique because it supports _both_ Gateway Endpoints and Interface Endpoints. Which one should you use?

**The Default Choice: Gateway Endpoint**
For 95% of use cases, you should use the Gateway Endpoint for S3. It is free, highly scalable, and requires only a simple Route Table update.

**When to use an Interface Endpoint for S3?**
Gateway Endpoints have a major limitation: they can only be accessed by resources _inside_ the exact VPC where they are deployed.
You must use an Interface Endpoint for S3 only if:

1. You need to access S3 privately from an **on-premises data center** over AWS Direct Connect or a Site-to-Site VPN.
2. You need to access S3 privately from a **different VPC** over a VPC Peering connection.

---

## Interview Preparation: VPC Endpoints

### Summary

Interviews often present scenarios where a company wants to reduce network costs or improve security when transferring massive amounts of data to S3. The answer is almost always a VPC Endpoint.

### Q&A Details

**Q1: Our backend EC2 instances in a private subnet process TBs of log files daily and upload them to Amazon S3. We are seeing massive data transfer costs on our AWS bill associated with our NAT Gateway. How can we eliminate these costs while keeping the instances private?**
**Answer:** The current architecture forces the heavy S3 traffic to route through the NAT Gateway, incurring per-GB data processing fees. We should provision a **Gateway VPC Endpoint** for Amazon S3 and update the private subnet's Route Table to point S3 traffic to the new endpoint. The traffic will now route directly to S3 over the free private AWS network, bypassing the NAT Gateway entirely and eliminating the data processing costs.

**Q2: We created an Interface Endpoint for Amazon SNS in our private subnet so our application can publish messages securely. However, the application is returning a connection timeout error when trying to reach SNS. The route tables are correct. What is the most likely issue?**
**Answer:** Interface Endpoints provision an Elastic Network Interface (ENI) inside the subnet. Therefore, they rely on **Security Groups**. The connection timeout is almost certainly caused by an improperly configured Security Group attached to the Interface Endpoint. Ensure the endpoint's Security Group has an inbound rule allowing HTTPS (Port 443) traffic originating from the EC2 instances.

**Q3: We have a Gateway VPC Endpoint configured for Amazon DynamoDB in our primary VPC. We recently connected our corporate on-premises data center to this VPC using AWS Direct Connect. However, the on-premises servers cannot reach DynamoDB through the Gateway Endpoint. Why?**
**Answer:** Gateway Endpoints cannot be accessed from outside their local VPC. They do not support connections over AWS Direct Connect, Site-to-Site VPNs, or VPC Peering. To allow on-premises servers to access DynamoDB privately, you would need to implement a proxy server architecture within the VPC, or rely on an Interface Endpoint if the service supports it for that specific access pattern.

---

# Practical Guide: Configuring a Gateway VPC Endpoint for S3

In this hands-on guide, we will completely sever an EC2 instance's access to the public internet, and then restore its ability to communicate with Amazon S3 using a free, private Gateway VPC Endpoint.

---

## 1. Severing Internet Access

To prove the VPC Endpoint works, we must first prove the instance has no other way to reach the outside world.

1. Navigate to the **VPC Console** > **Route Tables**.
2. Select your **PrivateRouteTable**.
3. Click the **Routes** tab and select **Edit routes**.
4. Find the route pointing to `0.0.0.0/0` (which currently targets your NAT Gateway) and **Remove** it.
5. Click **Save changes**.

Your private subnets are now completely isolated.

### Verifying the Isolation

1. Connect to your Bastion Host, and SSH into your Private EC2 instance.
2. Run `curl google.com`. It will time out.
3. Run `aws s3 ls`. It will time out, proving the instance cannot reach Amazon S3 over the public internet.

---

## 2. Preparing the EC2 Instance (IAM Roles)

Before the EC2 instance can list S3 buckets, it needs permission to do so. AWS manages permissions using IAM Roles.

1. Navigate to the **EC2 Console** and select your Private Instance.
2. Click **Actions** > **Security** > **Modify IAM role**.
3. Click **Create new IAM role** (this will open the IAM console in a new tab).
4. **Trusted entity type:** Select **AWS service**, then select **EC2**. Click Next.
5. **Permissions:** Search for and select the `AmazonS3ReadOnlyAccess` managed policy. Click Next.
6. **Role name:** Name it `DemoRoleEC2-S3ReadOnly`. Click **Create role**.
7. Return to the EC2 tab, click the refresh icon next to the IAM role dropdown, select the new role, and click **Update IAM role**.

_(Note: It may take a minute or two for the credentials to propagate to the instance)._

---

## 3. Creating the Gateway Endpoint

Now we will create the private link to Amazon S3.

1. Navigate to the **VPC Console** > **Endpoints** (Do not click Endpoint Services).
2. Click **Create endpoint**.
3. **Endpoint Name:** Enter `Demo-S3-Gateway-Endpoint`.
4. **Service category:** Select **AWS services**.
5. **Services:** In the search box, type `s3`.
6. **The Critical Choice:** You will see multiple options for S3. Look at the "Type" column. Ensure you select the service name ending in `.s3` where the type is **Gateway**. _(Do not select the Interface type for this exercise)._
7. **VPC:** Select your `DemoVPC`.
8. **Route tables:** This is the most important step for Gateway Endpoints. Select your **PrivateRouteTable**. AWS will automatically inject the necessary routing rules into this table.
9. **Policy:** Leave as **Full Access**.
10. Click **Create endpoint**.

---

## 4. Verifying the Automated Routing

Let's check what AWS did behind the scenes.

1. Navigate to **VPC Console** > **Route Tables**.
2. Select your **PrivateRouteTable** and click the **Routes** tab.
3. You will notice a new, uneditable route has appeared. The destination looks like `pl-xxxxxxx` (a Prefix List representing all AWS S3 IP addresses), and the target is your new VPC Endpoint (`vpce-xxxxxxx`).

You did not have to configure Security Groups or ENIs; the routing handles the connection automatically.

---

## 5. Testing the Private Connection

Let's return to the terminal and see if the isolated instance can reach S3.

1. Ensure you are still SSH'd into the Private Instance.
2. Run the S3 list command, explicitly specifying your AWS region (e.g., if your bucket is in Ireland, use `eu-west-1`):

```bash
aws s3 ls --region eu-west-1

```

3. **The Result:** You will instantly see a list of the S3 buckets in your account!

Even though a standard `curl google.com` still times out (proving the instance has zero internet access), the AWS CLI command succeeds because the traffic is being routed privately through the Gateway Endpoint directly to S3.

**Success!** You have securely and privately connected your backend infrastructure to Amazon S3.
