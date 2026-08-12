# Practical Guide: Launching Your First EC2 Instance

This guide walks through the process of provisioning an Amazon EC2 instance (a virtual server) via the AWS Management Console, configuring it as a web server using User Data, and managing its lifecycle.

## Provisioning Steps

### Step 1: Naming and Tags

* Navigate to the **EC2 Console** > **Instances** > **Launch Instances**.
* **Name:** Give your instance a clear name (e.g., *My First Instance*). AWS automatically applies this as a "Name" tag.

### Step 2: Choose an Amazon Machine Image (AMI)

The AMI is the base operating system for your server.

* **Selection:** Choose the **Amazon Linux 2 AMI** from the Quick Start menu.
* **Note:** Ensure it is marked as *Free Tier eligible* to avoid unexpected charges. Leave the architecture as 64-bit (x86).

### Step 3: Choose an Instance Type

Instance types dictate the compute power (CPU) and memory (RAM) of your server.

* **Selection:** Choose `t2.micro` (or `t3.micro` depending on your region's availability).
* **Pricing:** The `t2.micro` is Free Tier eligible, allowing 750 hours of usage per month for the first year.

### Step 4: Configure a Key Pair (For SSH Access)

A Key Pair is a secure file used to log into your instance via the command line (SSH), acting as a replacement for a password.

* **Create New Key Pair:** Name it (e.g., *EC2 Tutorial*).
* **Type:** RSA
* **Format:**
* Use `.pem` for Mac, Linux, or Windows 10/11.
* Use `.ppk` only if using older Windows versions (7 or 8) with the PuTTY tool.


* **Note:** The file will download to your computer immediately. Do not lose it!

### Step 5: Network Settings & Security Groups

Security Groups act as a virtual firewall, controlling inbound and outbound traffic. AWS will create a default group (e.g., `launch-wizard-1`).

* **Required Inbound Rules:**
* **SSH (Port 22):** Allow from anywhere (to log in via terminal).
* **HTTP (Port 80):** Allow from anywhere (to allow users to view your web server).


* **Important:** Do not enable HTTPS for this basic tutorial, as we don't have an SSL certificate yet.

### Step 6: Configure Storage

* **Default:** 8 GB General Purpose SSD (gp2) root volume. This is well within the 30 GB Free Tier limit.
* **Advanced Detail:** By default, "Delete on termination" is enabled. If you terminate the instance, this hard drive is permanently destroyed.

### Step 7: EC2 User Data (Bootstrapping)

Scroll down to **Advanced Details** to find the **User Data** section. This allows you to pass a script to configure the instance automatically.

* **The Script:** Paste your bash script here. For a web server, the script typically updates the OS (`yum update`), installs Apache (`httpd`), starts the service, and creates a basic `index.html` file.
```bash
#!/bin/bash
# Use this for your user data (script from top to bottom)
# install httpd (Linux 2 version)
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.html
```
* **Crucial Rule:** The User Data script executes *only once* during the very first boot cycle of the instance.

### Step 8: Launch and Verify

* Click **Launch Instance** and wait ~15 seconds for the state to turn to *Running*.
* Select the instance to view its details.
* **Public IPv4:** Copy this address and paste it into your browser.
* *Troubleshooting:* Ensure your browser uses `http://` and not `https://`. If it defaults to HTTPS, the page will endlessly load.


* **Private IPv4:** This is the internal network IP. It often shows up in the `index.html` output if configured in your bash script.

---

## ⚙️ Managing the Instance Lifecycle

Once your instance is running, you can change its state from the **Instance State** menu:

* **Stop Instance:** Shuts down the operating system. You stop paying for hourly compute charges (though you still pay pennies for the stored EBS volume).
* *Warning:* When you start the instance again, AWS will assign it a brand new Public IPv4 address. The Private IP remains unchanged.


* **Start Instance:** Boots up a stopped instance.
* **Terminate Instance:** Permanently deletes the virtual machine and its attached root storage volume. This action cannot be undone.