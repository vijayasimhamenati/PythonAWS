# EC2 Access Methods (SSH vs. EC2 Instance Connect)

Once your EC2 instance is running, you need a way to log into it to run commands, check logs, or install software.

There are two primary ways to access a Linux EC2 instance:

* **SSH (Secure Shell):** A terminal-based protocol requiring a `.pem` or `.ppk` key file.
* **EC2 Instance Connect:** A modern, browser-based terminal provided by AWS.

---

## 1. SSH Access (Operating System Guide)

The tool you use depends entirely on your local computer's operating system.

### Mac & Linux

Mac and Linux natively support the `ssh` command.

1. Open your terminal.
2. Ensure you are in the directory where your `.pem` key was downloaded (e.g., `cd ~/Downloads`).
3. **CRITICAL STEP:** You must lock down the permissions of your key file, or AWS will reject the connection.
```bash
chmod 400 EC2Tutorial.pem

```


4. Run the SSH command:
```bash
ssh -i EC2Tutorial.pem ec2-user@<Public-IP-Address>

```



### Windows 10 & Windows 11

Modern versions of Windows now include the native `ssh` command via Command Prompt or PowerShell.

1. Open PowerShell or Command Prompt.
2. Navigate to where your `.pem` file is located (e.g., `cd .\Desktop`).
3. Run the SSH command:
```bash
ssh -i EC2Tutorial.pem ec2-user@<Public-IP-Address>

```



> **Troubleshooting Windows "Bad Permissions" Error:**
> If Windows throws an error stating your key is "too open" or "unprotected":
> 1. Right-click the `.pem` file > **Properties** > **Security** tab > **Advanced**.
> 2. Click **Disable inheritance** and remove all inherited permissions.
> 3. Add only your specific Windows user account, and give it "Full Control". Remove "System" and "Administrators".
> 4. Click **Apply**. Try the `ssh` command again.
> 
> 

### Windows 7 & 8 (Legacy)

Older versions of Windows do not have native `ssh`. You must download a third-party tool called **PuTTY**.

1. You must use the `.ppk` version of your key file (PuTTY Private Key).
2. Open PuTTY, enter the `ec2-user@<Public-IP-Address>` in the Host Name box.
3. Navigate to **Connection** > **SSH** > **Auth** > **Credentials**, and browse for your `.ppk` file to connect.

---

## 2. EC2 Instance Connect (The Stephane Recommended Way)

If you do not want to deal with terminal permissions, PuTTY, or finding your `.pem` file, use **EC2 Instance Connect** [1].

* **How it works:** It provides a fully functional SSH terminal directly inside your web browser.
* **Prerequisites:**
* Your instance must be running Amazon Linux 2 (or Ubuntu 20.04+).
* Your Security Group must allow Inbound SSH (Port 22).


* **How to use:** In the EC2 Console, select your instance, click "Connect" at the top right, choose the "EC2 Instance Connect" tab, and click **Connect**.

---

## Interview Preparation: EC2 Access

### Summary

Interviewers rarely test you on PuTTY configurations, but they will test your fundamental understanding of why SSH connections fail. You must immediately recognize the difference between a Security Group timeout and a Key Pair permission rejection.

### Q&A Details

**Q1: A junior developer complains that when they try to run `ssh -i key.pem ec2-user@IP`, the terminal immediately returns a "WARNING: UNPROTECTED PRIVATE KEY FILE!" error and drops the connection. What is wrong?**
**Answer:** The permissions on the `.pem` key file are too open. SSH requires private keys to be strictly secured so that only the owner can read them. The developer needs to run `chmod 400 key.pem` on Mac/Linux, or restrict the file security properties to only their user on Windows.

**Q2: You try to SSH into an EC2 instance. The terminal hangs for 30 seconds without returning any error, and then finally says "Connection timed out." What is the first thing you should investigate?**
**Answer:** A "timeout" almost universally points to a network or firewall block. I would immediately check the Security Group attached to the EC2 instance to ensure there is an Inbound Rule explicitly allowing Port 22 (SSH) from my current IP address.

**Q3: We want developers to be able to access the command line of our Amazon Linux 2 EC2 instances, but we strictly forbid downloading `.pem` keys to personal laptops due to security policies. How can they access the servers?**
**Answer:** We should mandate the use of EC2 Instance Connect. It allows developers to securely access a browser-based terminal directly through the authenticated AWS Console, eliminating the need to download, store, or manage long-term private `.pem` keys on their local machines.
