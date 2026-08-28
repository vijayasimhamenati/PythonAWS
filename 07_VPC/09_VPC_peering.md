# AWS VPC Peering: Connecting Networks

By default, every Virtual Private Cloud (VPC) you create in AWS is a completely isolated network. But what happens when you have a database in one VPC and an application server in another, and they need to talk to each other securely?

**VPC Peering** is a networking connection between two VPCs that enables you to route traffic between them using private IPv4 or IPv6 addresses. Instances in either VPC can communicate with each other as if they are within the exact same network.

## 1. The Core Requirements of VPC Peering

To successfully peer two VPCs, you must adhere to several strict networking rules:

### A. Non-Overlapping CIDR Blocks

This is the most critical rule. If `VPC A` uses the CIDR block `10.0.0.0/16` and `VPC B` _also_ uses `10.0.0.0/16`, **they cannot be peered**. The AWS routers would not know which network a packet belongs to. You must design your networks with distinct IP ranges (e.g., peering `10.0.0.0/16` with `10.1.0.0/16`).

### B. Manual Route Table Updates

Establishing the peering connection itself is only half the battle. Just like an Internet Gateway, a VPC Peering connection does nothing until you update the Route Tables. You must manually add a route in `VPC A` pointing to `VPC B`'s CIDR block (with the target being the peering connection `pcx-...`), and do the exact same in reverse for `VPC B`.

### C. VPC Peering is NOT Transitive

Transitive routing means "jumping" through a middleman. AWS strictly prohibits this.

If you peer `VPC A` to `VPC B`, and then peer `VPC B` to `VPC C`:

- A can talk to B.
- B can talk to C.
- **A CANNOT talk to C.**

If you want `VPC A` and `VPC C` to communicate, you must explicitly create a separate, direct peering connection between them. In large organizations, this creates a "full mesh" network topology which can become complex to manage (this is why AWS created Transit Gateway, but for simpler setups, Peering is perfect).

---

## 2. Advanced Peering Capabilities

VPC Peering is highly flexible and extends beyond just your local account.

- **Cross-Account Peering:** You can peer a VPC in your AWS Account with a VPC owned by a completely different AWS Account (e.g., connecting your infrastructure to a vendor or a different corporate department). This requires a handshake: the requester initiates the connection, and the owner of the accepter VPC must explicitly accept the request in their console.
- **Cross-Region Peering (Inter-Region):** You can peer a VPC in `us-east-1` (Virginia) with a VPC in `eu-west-1` (Ireland). Traffic remains on the AWS global private backbone and never traverses the public internet, ensuring high security and consistent latency.

---

## 3. Cross-VPC Security Group Referencing

In previous modules, we learned that the most secure way to configure a Security Group is to reference the ID of _another_ Security Group (e.g., allowing traffic only from `sg-123456`) rather than using hardcoded IP addresses.

**The Magic Feature:** If you peer two VPCs that reside in the **same AWS Region**, you can actually reference Security Groups across the peering connection!

If you have a Web Server in `Account A` and a Database in `Account B` (peered in the same region), you do not need to figure out the exact private IP of the web server. You can simply edit the Database Security Group in `Account B` to allow Port 3306 traffic originating from `<Account-A-ID>/sg-webserver`.

_(Note: Cross-account/Cross-VPC Security Group referencing is ONLY supported if both VPCs are in the exact same AWS Region)._

---

## Interview Preparation: VPC Peering

### Summary

Expect exam and interview questions to focus heavily on the **non-transitive** rule, the **non-overlapping CIDR** rule, and the requirement to manually update **Route Tables**.

### Q&A Details

**Q1: We have three VPCs. The Production VPC is peered with the Shared Services VPC. The Development VPC is also peered with the Shared Services VPC. A developer in the Development VPC is trying to ping a server in the Production VPC, but it is failing. Why?**
**Answer:** VPC Peering is non-transitive. Just because both Development and Production are connected to the central Shared Services VPC does not mean they can route traffic through it to reach each other. To allow communication between Development and Production, you must create a direct, dedicated VPC Peering connection between them.

**Q2: A company just acquired a startup. They want to peer the startup's AWS VPC with their corporate AWS VPC. The peering connection request was sent and accepted successfully. However, instances still cannot communicate across the peering link. What two things must the network administrator check?**
**Answer:** First, the administrator must check the **Route Tables** in both VPCs. They must manually add routes pointing the destination CIDR of the opposite VPC to the Peering Connection target (`pcx-...`). Second, they must check the **Security Groups** and **NACLs** to ensure traffic from the peered CIDR block is allowed inbound and outbound on the required ports.

**Q3: We are planning our cloud network topology. We want to connect a new Analytics VPC (`10.0.0.0/16`) to our existing Production VPC (`10.0.0.0/16`) using a VPC Peering connection. Is this possible?**
**Answer:** No. You cannot create a VPC Peering connection between VPCs with matching or overlapping IPv4 CIDR blocks. Because both VPCs use `10.0.0.0/16`, the AWS routing infrastructure cannot determine which network a packet is destined for. One of the VPCs must be rebuilt with a distinct CIDR block (e.g., `10.1.0.0/16`).

---

# Practical Guide: Configuring VPC Peering

In this hands-on guide, we will connect our custom `DemoVPC` (`10.0.0.0/16`) to the AWS Default VPC (`172.31.0.0/16`) so that EC2 instances in both networks can communicate privately.

## 1. Preparing the Environment

First, we need instances in both VPCs to prove that the connection works.

1. **DemoVPC:** Ensure your Bastion Host is running and serving the `hello world` webpage (as configured in the previous NACL module). Take note of its Private IPv4 address (e.g., `10.0.0.72`).
2. **Default VPC:** Launch a new Amazon Linux 2 instance (e.g., `t2.micro`) into the Default VPC. Ensure it has a Security Group allowing SSH and HTTP.
3. **The Test (Failure):** SSH into the new Default VPC instance. Attempt to curl the private IP of the Bastion Host:

```bash
curl 10.0.0.72:80

```

_Result:_ The command will time out. Because the networks are completely isolated, the Default VPC has no idea where `10.0.0.72` is.

---

## 2. Creating the VPC Peering Connection

We must explicitly establish a link between the two networks.

1. Navigate to the **VPC Console** > **Peering Connections**.
2. Click **Create peering connection**.
3. **Name:** `demo-peering-connection`
4. **Local VPC to peer with (Requester):** Select your `DemoVPC` (`10.0.0.0/16`).
5. **Select another VPC to peer with (Accepter):**

- _Account:_ My account
- _Region:_ Another region (if applicable, but for this demo, leave as local).
- _VPC (Accepter):_ Select the **Default VPC** (`172.31.0.0/16`).

6. Click **Create peering connection**.

### The Handshake

The connection is now in a `Pending Acceptance` state. Because both VPCs are in the same account, you can accept the request yourself.

1. Select the pending connection.
2. Click **Actions** > **Accept Request**.
3. Click **Accept**. The status will change to `Active`.

_(Note: Even though the peering connection is active, the networks still cannot communicate. The routing is missing)._

---

## 3. Updating the Route Tables (Bi-Directional)

This is the most critical step and the most common source of errors. You must update the Route Tables in **both** VPCs to teach them how to find each other.

### Step A: Update the DemoVPC Route Table

We need to tell the `DemoVPC` how to find the `172.31.x.x` network.

1. Navigate to **Route Tables** and select your `PublicRouteTable` (which is associated with the Bastion Host).
2. Click **Routes** > **Edit routes** > **Add route**.
3. **Destination:** Enter the exact CIDR block of the Default VPC (`172.31.0.0/16`).
4. **Target:** Select **Peering Connection**, and choose the `demo-peering-connection` (`pcx-...`).
5. Click **Save changes**.

### Step B: Update the Default VPC Route Table

We need to tell the `Default VPC` how to find the `10.0.x.x` network.

1. In **Route Tables**, select the main route table associated with the Default VPC.
2. Click **Routes** > **Edit routes** > **Add route**.
3. **Destination:** Enter the exact CIDR block of the DemoVPC (`10.0.0.0/16`).
4. **Target:** Select **Peering Connection**, and choose the `demo-peering-connection`.
5. Click **Save changes**.

---

## 4. Testing the Peering Connection

Now that the routing is complete in both directions, we can test the connection.

1. Return to the terminal where you are SSH'd into the Default VPC instance.
2. Run the exact same curl command as before:

```bash
curl 10.0.0.72:80

```

_Result:_ The command will now instantly return `hello world`. The traffic traversed the private AWS backbone through the peering connection, successfully connecting the two isolated networks.
