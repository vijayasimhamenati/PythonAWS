# AWS VPC: Bastion Hosts (Jump Servers)

When you design a secure AWS architecture, you place your most sensitive resources (like databases or backend application servers) inside **Private Subnets**. Because these instances do not have public IP addresses and their subnets do not have a route to the Internet Gateway, they are completely isolated from the public internet.

However, as a system administrator sitting at your laptop, you still need a way to SSH into these private instances to perform maintenance, view logs, or troubleshoot issues.

**The Solution:** A Bastion Host.

---

## 1. What is a Bastion Host?

A Bastion Host (sometimes called a "Jump Box" or "Jump Server") is simply a standard EC2 instance that serves as a secure gateway to your private network.

- **Placement:** It must be placed in a **Public Subnet** so it can be reached from the public internet via the Internet Gateway.
- **Workflow:** Instead of trying to connect to your private database directly (which is impossible), you perform a two-step "jump":

1. First, you SSH from your local computer into the Bastion Host.
2. Second, from the terminal of the Bastion Host, you initiate a _new_ SSH connection to the private IP address of the target EC2 instance in the Private Subnet.

Because both the Bastion Host and the target instance live inside the same VPC, they can communicate with each other using their private IP addresses.

---

## 2. Security Group Configuration (Exam Focus!)

The most critical part of setting up a Bastion Host is configuring the firewalls (Security Groups) correctly. If you configure this poorly, you leave your entire private network vulnerable to attackers.

### The Bastion Host Security Group

The Bastion Host sits on the edge of the internet, making it a prime target for hackers running automated port-scanning scripts.

- **Inbound Rule:** Allow SSH (Port 22).
- **Source Restriction:** Do **NOT** allow `0.0.0.0/0` (everyone on the internet). You must restrict the source to a specific, known IP address, such as your corporate office's public IP address or your personal VPN's IP address.

### The Private Instance Security Group

The EC2 instances in your private subnet must be configured to reject traffic from anywhere except the Bastion Host.

- **Inbound Rule:** Allow SSH (Port 22).
- **Source Restriction:** You must set the source to either the **Private IP address** of the Bastion Host, or (best practice) the **Security Group ID** of the Bastion Host.

---

## Interview Preparation: Bastion Hosts

### Summary

If a scenario asks how administrators can access internal, private instances securely from the outside world, the answer is always a **Bastion Host** (or alternatively, AWS Systems Manager Session Manager).

### Q&A Details

**Q1: Our database administrators need SSH access to a new RDS cluster and EC2 backend servers located in a private subnet. The security team mandates that the database servers cannot have public IP addresses and cannot be exposed to the internet. How can we facilitate access?**

**Answer:** We should deploy a **Bastion Host** (an EC2 instance) into a Public Subnet. The administrators will first SSH into the Bastion Host over the internet, and from there, SSH into the private backend instances. We will secure this by configuring the Bastion Host's Security Group to only accept inbound SSH traffic from the administrators' corporate IP addresses.

**Q2: A junior developer configured a Bastion Host in a public subnet to access a private web server. They successfully connected to the Bastion Host, but the connection times out when they try to SSH from the Bastion Host to the private web server. What is the most likely misconfiguration?**

**Answer:** The Security Group attached to the private web server is incorrectly configured. It is likely missing an inbound rule allowing SSH (Port 22) traffic originating from the Bastion Host. To fix this, the developer should add an inbound rule on the private server's Security Group, setting the _Source_ to the Security Group ID of the Bastion Host.

---

# Practical Guide: Connecting to a Private Instance via Bastion Host

In this hands-on guide, we will walk through the process of launching an EC2 instance into a Private Subnet and accessing it securely using a Bastion Host.

## 1. Launching the Private EC2 Instance

Before we can connect, we need to provision the target instance inside our isolated network.

1. **Key Pair:** Ensure you have an SSH Key Pair created (e.g., `demo-key-pair.pem`). Save this file securely on your local machine.
2. **Launch Instance:** Navigate to the EC2 Console and click **Launch Instances**.
3. **AMI & Instance Type:** Select **Amazon Linux 2** and choose the `t2.micro` (Free Tier eligible) instance type.
4. **Network Settings:**

- Select your custom VPC (`DemoVPC`).
- Choose a **Private Subnet** (e.g., `PrivateSubnetA`).

5. **Security Group:** Create a new Security Group named `PrivateSG`.

- **Inbound Rule:** Allow **SSH (Port 22)**.
- **Source:** Do not allow `0.0.0.0/0`. Instead, select **Custom** and choose the Security Group ID of your Bastion Host. This explicitly permits SSH traffic _only_ if it originates from the Bastion Host.

6. Click **Launch instance**.

---

## 2. Connecting to the Bastion Host

Because the private instance is isolated, you cannot connect to it directly from your computer. You must first connect to the Bastion Host.

1. Select your Bastion Host instance in the EC2 console.
2. Connect to it using **EC2 Instance Connect** (directly in the browser) or via your local terminal using SSH.
3. You are now inside the Public Subnet.

---

## 3. Key Management on the Bastion Host

To SSH from the Bastion Host into the private instance, the Bastion Host needs access to your `.pem` key file.

_(Note: While SSH Agent Forwarding is the industry best practice, the manual copy-paste method below is often used for quick testing)._

1. On the Bastion Host terminal, create a new file using a text editor like `nano` or `vi`:

```bash
vi demo-key-pair.pem

```

2. Open the original `.pem` file on your local computer, copy its entire contents (including the `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----` lines), and paste it into the editor on the Bastion Host. Save and exit the editor.
3. **Permissions Fix:** SSH is highly secure and will reject keys with open permissions. You must restrict the file so only you can read it:

```bash
chmod 400 demo-key-pair.pem

```

---

## 4. SSH into the Private Instance

Now that you are on the Bastion Host and have the private key ready, you can make the final jump into the private network.

1. Find the **Private IPv4 Address** of your target EC2 instance in the AWS Console (e.g., `10.0.16.55`).
2. From the Bastion Host terminal, run the standard SSH command using the key you just created and the target's private IP:

```bash
ssh -i demo-key-pair.pem ec2-user@<PRIVATE_IP_ADDRESS>

```

3. Type `yes` to accept the fingerprint. You are now successfully connected to your isolated backend instance!

---

## 5. Testing Internet Access

Now that you are inside the private instance, let's test its network connectivity.

Run the following command:

```bash
ping google.com

```

**The Result:** The command will hang and fail.
Because this instance is in a Private Subnet (meaning its Route Table does not have a route to the Internet Gateway), it has zero outbound internet access. It cannot download patches, software updates, or reach external APIs.
