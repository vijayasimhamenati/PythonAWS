# Hybrid Cloud Networking: AWS Site-to-Site VPN

While VPCs isolate your cloud resources from the public internet, enterprises often need their cloud infrastructure to communicate securely with their on-premises physical data centers. This is where **Hybrid Cloud Networking** comes in.

The most common and cost-effective way to achieve this is by establishing an **AWS Site-to-Site VPN**.

---

## 1. The Core Components of a Site-to-Site VPN

A Site-to-Site VPN establishes a secure, encrypted IPSec tunnel over the public internet. It requires two anchor points—one on the AWS side, and one on your corporate side.

### The AWS Side: Virtual Private Gateway (VGW)

- The VGW acts as the VPN concentrator on the AWS side of the connection.
- You create the VGW and attach it directly to your target VPC.
- _(Note: You can optionally customize the ASN—Autonomous System Number—for routing purposes if your networking team requires it)._

### The Corporate Side: Customer Gateway (CGW)

- The CGW represents the physical or software appliance (like a Cisco ASA or Palo Alto firewall) sitting in your corporate data center.
- In the AWS Console, you create a "Customer Gateway" resource, which is essentially just a configuration file telling AWS the IP address and routing protocol of your physical firewall.

**The IP Address Rule (Exam Focus):**
When configuring the CGW in AWS, which IP address do you provide?

1. **Public Device:** If your physical firewall has a direct, internet-routable IP address, you provide that public IP.
2. **Private Device behind NAT:** If your physical firewall has a private IP and sits behind a NAT device (using NAT Traversal / NAT-T), you must provide the **public IP address of the NAT device**, not the private IP of the firewall.

---

## 2. Enabling the Connection

Just creating the VGW and CGW is not enough to pass traffic. Two crucial steps remain:

1. **Route Propagation:** You must go into the AWS Route Tables associated with your subnets and enable **Route Propagation**. This allows the VGW to automatically inject the network routes from your corporate data center into the VPC route table. Without this, your EC2 instances won't know how to route traffic back to the office.
2. **Security Groups:** If an administrator in the corporate office tries to `ping` an EC2 instance in the VPC, it will fail unless the EC2 instance's Security Group has an inbound rule allowing **ICMP (Ping)** traffic from the corporate network's CIDR block.

---

## 3. AWS VPN CloudHub

What if you have multiple branch offices (e.g., New York, London, and Tokyo), and they all need to connect to AWS, but they _also_ need to communicate securely with each other?

You could buy expensive, dedicated leased lines between all the offices. Or, you can use **AWS VPN CloudHub**.

**How CloudHub Works:**

- It is a **hub-and-spoke** model. The single Virtual Private Gateway (VGW) in your VPC acts as the central Hub.
- You establish separate Site-to-Site VPN connections from each branch office (the spokes) to that central VGW.
- Once dynamic routing (BGP) is configured, the branch offices can not only communicate with the AWS VPC, but they can securely route traffic _through_ the VGW to reach the other branch offices.
- **Security:** All traffic still traverses the public internet, but it is entirely encrypted via IPSec VPN tunnels. It is a highly cost-effective way to link global corporate networks.

---

## Interview Preparation: Hybrid Networking

### Summary

Interviews focusing on hybrid architecture will test your knowledge of the gateway components (VGW vs. CGW), the routing requirements, and how to connect multiple disparate sites efficiently.

### Q&A Details

**Q1: We are establishing a Site-to-Site VPN between our VPC and our corporate data center. The VPN tunnels show an 'Up' status in the AWS Console, but our EC2 instances cannot reach the internal corporate servers. What is the most likely missing configuration?**
**Answer:** The network administrator most likely forgot to enable **Route Propagation** on the VPC Route Tables. Even though the VPN tunnel is established, the Route Table must be updated (either manually or via propagation) so the VPC knows to route the corporate IP addresses to the Virtual Private Gateway (VGW).

**Q2: Our company has five retail stores across the country. They all need to securely access our inventory application hosted in a single AWS VPC. Furthermore, the retail stores occasionally need to transfer files directly to each other. We have a limited budget and cannot afford dedicated fiber lines. What is the recommended architecture?**
**Answer:** You should implement an **AWS VPN CloudHub** architecture. You attach a single Virtual Private Gateway (VGW) to the VPC. Then, you establish five separate Site-to-Site VPN connections from the Customer Gateway (CGW) at each retail store to the central VGW. Using dynamic routing, the stores can access the inventory app, and also use the VGW as a central hub to route encrypted traffic to each other over the public internet.

**Q3: When configuring the Customer Gateway (CGW) in the AWS Console for a new Site-to-Site VPN, the wizard asks for an IP address. Our physical firewall appliance sits in a private network and routes traffic out through a NAT device. Which IP address should we input into the AWS console?**
**Answer:** You must input the **public IP address of the NAT device**. AWS needs a public, internet-routable IP address to establish the external IPSec tunnel. Providing the private IP of the firewall would fail because private IPs cannot be routed across the public internet.

---

# Practical Guide: Configuring an AWS Site-to-Site VPN

While configuring a real Site-to-Site VPN requires physical networking hardware in an on-premises data center, we can walk through the exact steps required in the AWS Console to provision the cloud side of the infrastructure.

To connect an on-premises network to an AWS VPC, you must provision three distinct resources in a specific order:

1. **The Customer Gateway (CGW)**
2. **The Virtual Private Gateway (VGW)**
3. **The Site-to-Site VPN Connection**

---

---

## Step 1: Create the Customer Gateway (CGW)

The Customer Gateway is an AWS resource that acts as a logical representation of your physical on-premises firewall (e.g., a Cisco ASA or Palo Alto device).

1. Navigate to the **VPC Console**. Scroll down the left-hand menu to the **Virtual Private Network (VPN)** section.
2. Click **Customer gateways** > **Create customer gateway**.
3. **Name tag:** Enter a descriptive name (e.g., `Corporate-HQ-Firewall`).
4. **BGP ASN:** (Border Gateway Protocol Autonomous System Number). Unless your networking team provides a specific custom ASN for dynamic routing, leave the default setting.
5. **IP address:** This is the most critical field. You must enter the **public, internet-routable IP address** of your physical on-premises firewall. _(Note: If your firewall is behind a NAT device, enter the public IP of the NAT device)_.
6. **Certificate ARN:** Leave blank unless you are using highly advanced certificate-based authentication instead of standard pre-shared keys.
7. Click **Create customer gateway**.

## Step 2: Create the Virtual Private Gateway (VGW)

The Virtual Private Gateway is the AWS side of the VPN connection. It is the concentrator that attaches directly to your VPC.

1. In the left-hand menu, click **Virtual private gateways** > **Create virtual private gateway**.
2. **Name tag:** Enter a name (e.g., `Demo-VPC-VGW`).
3. **ASN:** Leave as the Amazon default ASN.
4. Click **Create virtual private gateway**.
5. **Crucial Step - Attach to VPC:** The VGW is currently detached. Select it, click the **Actions** dropdown, and choose **Attach to VPC**. Select your target VPC (e.g., `DemoVPC`) and attach it.

## Step 3: Create the Site-to-Site VPN Connection

Now that both the AWS and on-premises anchors exist logically in the console, we must link them together with a VPN Connection.

1. In the left-hand menu, click **Site-to-Site VPN connections** > **Create VPN connection**.
2. **Name tag:** Enter a name (e.g., `AWS-to-Corp-VPN`).
3. **Target Gateway Type:** Select **Virtual private gateway**.
4. **Virtual Private Gateway:** Select the `Demo-VPC-VGW` you created in Step 2.
5. **Customer Gateway:** Select **Existing**, then choose the `Corporate-HQ-Firewall` you created in Step 1.
6. **Routing Options:**

- Select **Dynamic (requires BGP)** if your physical firewall supports the Border Gateway Protocol. This allows the networks to automatically learn each other's IP ranges.
- Select **Static** if your firewall does not support BGP. You will have to manually enter the IP prefixes of your corporate network here.

7. Click **Create VPN connection**.

---

---

## Next Steps (Outside the AWS Console)

Once the VPN connection is created in AWS, the status will show as `Pending`. To complete the setup, your network administrator must perform physical work on the corporate side.

AWS provides a **Download Configuration** button on the VPN Connection page. The network administrator downloads this text file (selecting their specific firewall vendor, like Cisco or Juniper) and applies the provided Pre-Shared Keys (PSKs) and IPSec configurations to the physical firewall in the data center.

Once the physical firewall is configured and initiates the handshake, the AWS Console status will change from `Pending` to `Available`, and the encrypted tunnel will be fully operational.
