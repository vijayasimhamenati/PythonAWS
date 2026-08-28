# AWS VPC Security: NACLs and Security Groups

In AWS networking, there are two distinct layers of defense that control traffic moving in and out of your resources: **Security Groups (SGs)** and **Network Access Control Lists (NACLs)**. Understanding the difference between them—specifically the concept of statefulness—is critical for passing AWS certification exams.

---

## 1. Security Groups vs. NACLs: The Core Differences

Here is a quick cheat sheet summarizing the fundamental differences:

| Feature         | Security Group (SG)                                    | Network ACL (NACL)                                                            |
| --------------- | ------------------------------------------------------ | ----------------------------------------------------------------------------- |
| **Scope**       | Operates at the **Instance** level.                    | Operates at the **Subnet** level.                                             |
| **State**       | **Stateful**: Return traffic is automatically allowed. | **Stateless**: Return traffic must be explicitly allowed.                     |
| **Rules**       | Supports **Allow** rules only.                         | Supports **Allow** and **Deny** rules.                                        |
| **Evaluation**  | Evaluates all rules before deciding to allow traffic.  | Evaluates rules in numerical order (lowest to highest); the first match wins. |
| **Application** | Must be manually assigned to an EC2 instance.          | Automatically applies to all instances within the associated subnet.          |

---

## 2. Stateful vs. Stateless: The Packet Journey

To truly understand these firewalls, let's trace a network packet.

### Security Groups are Stateful

If an EC2 instance initiates an outbound request to `google.com` on Port 443, the Security Group outbound rules are checked. If allowed, the request goes out.
When `google.com` sends the HTML response back, the Security Group **remembers** the outbound request. It automatically allows the inbound response to pass through, regardless of what the inbound rules say.

### NACLs are Stateless

NACLs have no memory. If that same request to `google.com` goes out, the NACL outbound rules are checked and the packet leaves.
However, when the response from `google.com` comes back, the NACL treats it as a brand new, unrelated packet. The NACL **inbound** rules are evaluated. If there isn't a specific inbound rule allowing that traffic, it is blocked.

---

## 3. Network ACL Mechanics

- **One per Subnet:** Every subnet must be associated with exactly one NACL.
- **The Default NACL:** When you create a VPC, a default NACL is created. It is heavily tested on exams: **The default NACL allows ALL inbound and ALL outbound traffic by default**. (It is highly recommended you do not modify the default NACL; instead, create custom ones).
- **Rule Evaluation:** Rules are numbered (1 to 32766). They are evaluated from the lowest number to the highest.
- _Example:_ Rule 100 allows IP `1.2.3.4`. Rule 200 denies IP `1.2.3.4`. Because Rule 100 is evaluated first, the IP is allowed.
- _The Catch-All:_ There is always a final rule marked with an asterisk (`*`). This rule cannot be modified and **denies** all traffic that didn't match a previous rule.

---

## 4. The Complexity of Ephemeral Ports

Because NACLs are stateless, managing return traffic requires understanding **Ephemeral Ports**.

When a client (like your web browser or an EC2 instance) connects to a server (like a web server on Port 80), the client doesn't use Port 80 for its own side of the connection. Instead, the client's operating system opens a random, temporary port (an "ephemeral port") to receive the response.

- **Linux Range:** Typically `32768 - 60999`
- **Windows Range:** Typically `49152 - 65535`

### The Scenario

Imagine a web server in a public subnet connecting to a database in a private subnet.

1. **The Outbound Request:** The Web NACL must allow outbound traffic on Port `3306` (MySQL) to the DB Subnet CIDR. The DB NACL must allow inbound traffic on Port `3306` from the Web Subnet CIDR.
2. **The Return Response:** The database processes the query and sends the data back. Because NACLs are stateless, the DB NACL must explicitly allow outbound traffic, and the Web NACL must explicitly allow inbound traffic.

- _The Catch:_ The database isn't sending the data back to Port 80 or 3306. It is sending it back to the temporary ephemeral port the web server opened!
- **The Fix:** The DB NACL outbound rules and the Web NACL inbound rules must allow TCP traffic on the entire Ephemeral Port range (e.g., `1024 - 65535`) targeting the other subnet's CIDR.

---

## Interview Preparation: NACLs & Security Groups

### Summary

- If you need to block a specific IP address (like a malicious attacker), you must use a **NACL**. Security Groups cannot explicitly deny traffic.
- If connectivity fails in one direction but not the other, or if it involves complex multi-tier subnet communication, check the **NACL Ephemeral Port rules**.

### Q&A Details

**Q1: We are experiencing a DDoS attack originating from a specific IP address (`203.0.113.45`). A junior administrator attempted to block this IP by adding it to the Web Server's Security Group, but the traffic is still hitting our instances. Why did this fail, and how do we fix it?**
**Answer:** The attempt failed because Security Groups only support `ALLOW` rules; you cannot explicitly `DENY` an IP address using a Security Group. To block a specific IP, you must add an inbound `DENY` rule to the **Network ACL (NACL)** associated with the public subnet, ensuring it has a lower rule number (higher priority) than any existing `ALLOW` rules.

**Q2: We deployed a new EC2 instance into a private subnet. The instance can successfully initiate a connection to download updates from the internet via a NAT Gateway, but the incoming responses are being dropped before reaching the instance. The Security Group outbound rules are completely open. What is the most likely cause?**
**Answer:** The issue is likely a misconfiguration in the **Network ACL (NACL)** associated with the private subnet. Because NACLs are stateless, they do not automatically allow return traffic from an outbound request. The NACL must have an inbound `ALLOW` rule configured for the **Ephemeral Port range** (typically `1024-65535`) to accept the returning packets from the NAT Gateway.

**Q3: In our production VPC, we want to ensure that all EC2 instances launched into the database subnet are automatically protected by the same firewall rules, regardless of whether a developer remembers to attach a specific Security Group. How can we achieve this?**
**Answer:** You should implement a **Network ACL (NACL)** and associate it with the database subnet. Because NACLs operate at the subnet level, their rules are automatically applied to every single EC2 instance launched within that subnet, providing a mandatory layer of defense that does not rely on developer action.

---

# Practical Guide: NACLs vs. Security Groups in Action

In this hands-on guide, we will prove the theoretical concepts of rule precedence, statefulness, and statelessness by actively breaking and fixing network connectivity to an EC2 web server.

## 1. Setting the Stage: The Web Server

First, we need a target to test our network rules against. We will connect to our Bastion Host (which resides in a public subnet) and convert it into a basic web server.

1. SSH into your Bastion Host.
2. Install and start the Apache web server (`httpd`), and create a simple `index.html` file:

```bash
sudo yum install -y httpd
sudo systemctl enable httpd
sudo systemctl start httpd
sudo su
echo "hello world" > /var/www/html/index.html

```

3. **Update the Security Group:** Navigate to the Security Group attached to the Bastion Host. Add an inbound rule allowing **HTTP (Port 80)** from anywhere (`0.0.0.0/0`).
4. Copy the Public IPv4 address of the Bastion Host and paste it into a new browser tab. You should see the message: `hello world`.

---

## 2. Proving NACL Rule Precedence

Every subnet is associated with a Default NACL. By default, it contains a rule numbered `100` that allows ALL traffic, and an unmodifiable asterisk rule (`*`) that denies all traffic.

Because NACL rules are evaluated from the lowest number to the highest (the **first match wins**), we can test how precedence overrides conflicting rules.

### Test 1: The Higher Priority Deny

1. Navigate to **VPC Console** > **Network ACLs** and select the NACL associated with your public subnet.
2. Edit the **Inbound Rules**.
3. Add a new rule:

- **Rule number:** `80`
- **Type:** `HTTP (80)`
- **Source:** `0.0.0.0/0`
- **Allow/Deny:** `DENY`

4. Save the changes.
5. **The Result:** Refresh your browser tab. The page will hang in an infinite loading state. The firewall blocked your request because rule `80` (Deny) was evaluated before rule `100` (Allow).

### Test 2: The Lower Priority Deny

1. Edit the inbound rules again.
2. Change the rule number from `80` to `140`. Save the changes.
3. **The Result:** Refresh your browser tab. The page instantly loads `hello world`. Even though there is an explicit `DENY` rule for HTTP traffic, the request matched rule `100` (Allow All) first. The evaluation stopped immediately, and rule `140` was completely ignored.

---

## 3. Proving NACL Statelessness

A firewall is "stateless" if it has no memory. If it allows a request _in_, it does not automatically allow the response _out_.

1. Ensure your NACL Inbound Rules are set to allow HTTP traffic (e.g., remove the deny rule).
2. Navigate to the **Outbound Rules** of the NACL.
3. Edit the default rule `100` (which currently allows all traffic) and change it to **DENY**. Save the changes.
4. **The Result:** Refresh your browser tab. The page hangs in an infinite loading state.

**What happened?**
The inbound rule successfully allowed your HTTP request into the subnet. The web server generated the `hello world` response and attempted to send it back. However, because the NACL is stateless, it treated the response as a brand-new packet. It checked the outbound rules, saw a `DENY`, and blocked the response from leaving the subnet.

_(Revert the outbound rule back to `ALLOW` before proceeding)._

---

## 4. Proving Security Group Statefulness

A firewall is "stateful" if it remembers the connections that pass through it. If a request is allowed _in_, the response is automatically allowed _out_, regardless of the outbound rules.

1. Navigate to the **Security Group** attached to your Bastion Host.
2. Ensure the Inbound Rules allow HTTP (Port 80).
3. Navigate to the **Outbound Rules**.
4. Delete all outbound rules so the list is completely empty (which implicitly denies all outbound traffic). Save the changes.
5. **The Result:** Refresh your browser tab. The page loads `hello world` perfectly.

**What happened?**
Even though the Security Group explicitly denies all outbound traffic, the firewall _remembered_ that your browser initiated the connection from the outside. Because SGs are stateful, the return traffic was automatically permitted to exit the instance.

_(Note: While return traffic works, because there are no outbound rules, the EC2 instance itself can no longer initiate new outbound connections, such as running `ping google.com` or `yum update`)._

---

## Interview Preparation: Rule Troubleshooting

### Summary

Interviews often present scenarios where connectivity is broken, and you must deduce whether the issue lies in the Security Group or the NACL based on the symptoms.

### Q&A Details

**Q1: An administrator configures a NACL to explicitly deny traffic from a known malicious IP address on Rule 500. However, the malicious IP is still successfully reaching the web servers. What is the architectural error?**
**Answer:** The NACL likely has a broader `ALLOW` rule (such as the default Rule 100 that allows `0.0.0.0/0`) with a lower number than the custom deny rule. Because NACLs process rules in numerical order and stop evaluating at the first match, the traffic is permitted by Rule 100 before Rule 500 is ever evaluated. The administrator must change the rule number of the `DENY` rule to a value lower than 100 (e.g., Rule 90).

**Q2: We want to restrict an EC2 instance so that it can only receive inbound HTTP requests but can never initiate its own outbound connections to the internet. Can we achieve this using only a Network ACL?**
**Answer:** No. Because Network ACLs are stateless, if you block all outbound traffic on the NACL, you will also block the return responses to the inbound HTTP requests, breaking the web server entirely. To achieve this, you must use a **Security Group**. You can allow inbound HTTP and remove all outbound rules; the stateful nature of the Security Group will allow the web responses to leave, while preventing the instance from initiating new outbound connections.
