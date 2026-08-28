# AWS VPC: NAT Instances (Legacy)

In the previous lecture, we discovered that EC2 instances launched in a Private Subnet cannot reach the internet (e.g., they cannot `ping google.com` or download software updates).

To solve this, we can use **Network Address Translation (NAT)**. While AWS now strongly recommends using the fully managed **NAT Gateway** (covered in the next lecture), you must still understand the legacy **NAT Instance** for the exam.

---

## 1. What is a NAT Instance?

A NAT Instance is a standard EC2 instance specifically configured to route traffic from private subnets to the internet.

- **Placement:** It must be launched into a **Public Subnet** (because it needs a route to the Internet Gateway).
- **IP Address:** It must be assigned a fixed **Elastic IP Address** so the outside world can respond to it.
- **The Route Table:** You must update the Route Table of your _Private Subnet_ so that any outbound internet traffic (`0.0.0.0/0`) targets the NAT Instance.

### How the Packet Flow Works (The Translation)

When an instance in your private subnet tries to download a file from a public server, here is what happens:

1. **Outbound Request:** The private instance (e.g., IP `10.0.0.20`) sends a request to the public server (e.g., IP `50.60.4.10`).
2. **The Interception:** The Route Table sends this packet to the NAT Instance.
3. **The Translation (NAT):** The NAT Instance receives the packet. It strips away the private source IP (`10.0.0.20`) and replaces it with its own public Elastic IP (`12.34.56.78`). It then sends the packet out to the internet.
4. **The Response:** The public server receives the request. It thinks the request came from `12.34.56.78` and sends the response back there.
5. **Reverse Translation:** The NAT Instance receives the response, remembers who originally asked for it, rewrites the destination back to `10.0.0.20`, and forwards the file to the private instance.

---

## 2. The Golden Rule: Disable Source/Destination Check

This is the most highly tested concept regarding NAT Instances on AWS exams.

By default, every EC2 instance performs a **Source/Destination Check**. This is a security feature that ensures an instance only accepts network packets that are explicitly addressed to its own IP, and only sends packets where it is the original source.

Because a NAT Instance is essentially a "middleman" that receives traffic meant for a public server and sends traffic on behalf of a private server, **it will fail this security check and drop the packets.**

> ⚠️ **Exam Tip:** You MUST manually select the NAT Instance in the EC2 console, go to Networking actions, and **Disable the Source/Destination Check**. If you do not do this, the NAT Instance will not work.

---

---

## 3. Why NAT Instances are Outdated

AWS provides pre-configured Amazon Linux AMIs for NAT Instances, but they reached the end of standard support in 2020. They have severe limitations:

- **Not Highly Available:** If the NAT Instance crashes, your entire private subnet loses internet access. You would have to manually build complex Auto Scaling Groups to fix this.
- **Bandwidth Bottlenecks:** The internet speed of your entire private subnet is limited by the size of the NAT Instance. If you use a `t2.micro`, your entire backend will have slow internet. To get more bandwidth, you must pay for a larger, more expensive instance.
- **Maintenance Overhead:** You must manage the underlying EC2 operating system, patch it, and carefully manage its Security Groups (allowing inbound HTTP/HTTPS from the private subnet).

---

## Interview Preparation: NAT Instances

### Summary

If an exam question asks about NAT _Instances_, the answer will almost certainly revolve around the **Source/Destination Check**, the need to place it in a **Public Subnet**, or highlighting its operational disadvantages compared to a NAT Gateway.

### Q&A Details

**Q1: A junior engineer provisions a NAT Instance in a Public Subnet and configures the Private Subnet's route table to point `0.0.0.0/0` to the NAT Instance. However, the EC2 instances in the private subnet still cannot reach the internet. What did the engineer forget to do?**
**Answer:** The engineer forgot to disable the **Source/Destination Check** on the NAT EC2 instance. By default, EC2 instances drop packets that are not explicitly destined for them. Because a NAT instance routes traffic for other instances, this check must be disabled in the EC2 networking console.

**Q2: We are hosting a high-traffic video rendering farm in a private subnet. We deployed a `t2.micro` NAT Instance to allow the rendering servers to download software updates. The instances are experiencing extreme latency when downloading files. How can we fix this using the current architecture?**
**Answer:** The bandwidth of a NAT Instance is strictly limited by its EC2 instance size. A `t2.micro` has low network performance, creating a severe bottleneck for the entire private subnet. To fix this within the current architecture, you must stop the NAT Instance, upgrade it to a larger instance type (like an `m5.large` or an instance with enhanced networking), and restart it. _(Alternatively, replace it entirely with a managed NAT Gateway)._

**Q3: Is a single NAT Instance a highly available architecture? What happens if the Availability Zone hosting the NAT Instance goes down?**
**Answer:** No, a NAT Instance is a single point of failure. If the EC2 instance crashes or the AZ goes down, all private subnets relying on it will instantly lose internet connectivity. To make it highly available, you would need to engineer a complex solution involving Auto Scaling Groups across multiple AZs and scripted route table updates, which is why AWS recommends migrating to NAT Gateways.

---

# Practical Guide: Setting up a NAT Instance

In this hands-on guide, we will walk through the process of provisioning a legacy NAT Instance to provide outbound internet access to EC2 instances located in a Private Subnet.

> **Note:** While NAT Gateways (covered in the next module) are the modern standard, understanding how to configure a NAT Instance is still valuable for AWS exams and legacy architectures.

---

## 1. Finding and Launching the NAT AMI

Unlike standard EC2 instances, a NAT Instance requires a specific operating system configuration (specifically, IP forwarding must be enabled within the OS). AWS provides pre-configured community AMIs for this.

1. Navigate to the **EC2 Console** and click **Launch Instances**.
2. **Name:** Give it a name like `NAT-Instance`.
3. **OS/AMI Selection:**

- Do _not_ use a standard Amazon Linux 2 AMI.
- Click **Browse more AMIs**.
- Search for `NAT` and look under the **Community AMIs** tab.
- Find an image provided by Amazon (e.g., `amzn-ami-vpc-nat...`) with an `x86_64` architecture. (Even if it is dated 2018 or 2022, it is sufficient for this demo).

4. **Instance Type:** Select a Free Tier eligible type like `t2.micro`.
5. **Key Pair:** Select your existing key pair (e.g., `demo-key-pair`).

## 2. Configuring the NAT Security Group

The NAT Instance must be able to accept web traffic from your private instances and forward it out.

1. Under **Network Settings**, ensure the instance is launching into your **Custom VPC** (`DemoVPC`).
2. **Subnet:** You MUST launch this into a **Public Subnet** (e.g., `PublicSubnetA`) so it has access to the Internet Gateway.
3. **Security Group:** Create a new security group named `NAT-Instance-SG` with the following Inbound Rules:

- **SSH (Port 22):** From anywhere (or your specific IP).
- **HTTP (Port 80):** Set the source to the CIDR block of your VPC (e.g., `10.0.0.0/16`).
- **HTTPS (Port 443):** Set the source to the CIDR block of your VPC (`10.0.0.0/16`).
- _(Optional but recommended for testing)_ **All ICMP - IPv4:** Set the source to `10.0.0.0/16` so you can test connectivity with the `ping` command.

4. Click **Launch Instance**.

---

## 3. The Golden Rule: Disable Source/Destination Check

Before the NAT Instance can route any traffic, you must disable the default EC2 security check that drops forwarded packets.

1. Select the running NAT Instance in the EC2 Console.
2. Click the **Actions** dropdown > **Networking** > **Change source/destination check**.
3. Check the box to **Stop** the check and click **Save**.

---

## 4. Updating the Private Route Table

Currently, the private instances don't know the NAT Instance exists. We must update the network routing rules.

1. Navigate to the **VPC Console** > **Route Tables**.
2. Select your **PrivateRouteTable** (the one associated with your private subnets).
3. Click the **Routes** tab > **Edit routes** > **Add route**.
4. **Destination:** Enter `0.0.0.0/0` (the internet).
5. **Target:** Select **Instance**, and choose the specific Instance ID of your NAT Instance.
6. Click **Save changes**.

You have now told the network: _"If any server in a private subnet wants to reach the internet, send its traffic to the NAT EC2 Instance."_

---

## 5. Testing the Connection

Now we can test if the private instance can finally reach the outside world.

1. Use **EC2 Instance Connect** to log into your Bastion Host.
2. From the Bastion Host, SSH into your Private Instance using its private IP:

```bash
ssh -i demo-key-pair.pem ec2-user@<PRIVATE_IP>

```

3. Once inside the private instance, run a ping test:

```bash
ping google.com

```

_(If you configured the ICMP rule on the NAT Security Group, you should see successful replies)._ 4. Run a curl test to pull a webpage:

```bash
curl example.com

```

_(You should see the raw HTML of the webpage returned)._

**Success!** Your private instance now has outbound internet access without being directly exposed to the internet.

_Because NAT Instances are deprecated, be sure to stop or terminate the NAT instance when you are done testing to save costs._
