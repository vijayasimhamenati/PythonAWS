# Enabling Internet Access: Internet Gateways and Route Tables

Currently, our custom VPC has subnets, but they are entirely isolated. Even if an EC2 instance is launched inside them with a public IP address, it cannot reach the internet, and the internet cannot reach it.

To fix this, we need to understand the relationship between **Internet Gateways (IGW)** and **Route Tables**.

## 1. What makes a Subnet "Public" or "Private"?

A common misconception is that naming a subnet "PublicSubnet" makes it public. This is false. A subnet's public/private status is determined by exactly two things:

1. **Auto-assign Public IPv4:** Instances launched in the subnet must be automatically assigned a public IP address.
2. **The Route Table:** The subnet must be associated with a Route Table that has a specific route directing internet-bound traffic (`0.0.0.0/0`) to an Internet Gateway.

If _both_ conditions are met, the subnet is considered **Public**. If the Route Table does not have a route to the Internet Gateway, the subnet is considered **Private**.

---

## 2. The Internet Gateway (IGW)

An Internet Gateway is a horizontally scaled, redundant, and highly available VPC component that allows communication between instances in your VPC and the internet.

**Key Rules:**

- You must create it separately from the VPC.
- One VPC can only be attached to **one** Internet Gateway.
- One Internet Gateway can only be attached to **one** VPC.
- An IGW on its own does nothing; it relies on Route Tables to direct traffic to it.

### Step 1: Creating and Attaching the IGW

1. Navigate to the **VPC Console** > **Internet Gateways**.
2. Click **Create internet gateway** and name it `DemoIGW`.
3. Once created, its state will be _Detached_.
4. Select the `DemoIGW`, click **Actions** > **Attach to VPC**, and select your `DemoVPC`.

---

## 3. Configuring Route Tables

A Route Table contains a set of rules (called routes) that determine where network traffic from your subnet or gateway is directed.

When you create a VPC, AWS automatically creates a "Main Route Table." It is best practice to leave the Main Route Table alone and create explicitly defined custom route tables.

### Step 2: Creating Custom Route Tables

1. Navigate to **Route Tables** and click **Create route table**.
2. Create one named `PublicRouteTable` (select `DemoVPC`).
3. Create another named `PrivateRouteTable` (select `DemoVPC`).

### Step 3: Explicit Subnet Associations

We must tell our subnets which Route Table rules they should follow.

1. Select the `PublicRouteTable`.
2. Go to the **Subnet associations** tab and click **Edit subnet associations**.
3. Select both of your public subnets (`PublicSubnetA` and `PublicSubnetB`) and click **Save associations**.
4. Repeat this process for the `PrivateRouteTable`, associating it with your two private subnets.

### Step 4: Adding the Internet Route

Now, we must tell the `PublicRouteTable` how to find the internet.

1. Select the `PublicRouteTable` and click the **Routes** tab.
2. You will notice a default route already exists: `10.0.0.0/16` pointing to `local`. This rule ensures all resources _inside_ the VPC can talk to each other without leaving the internal network. You cannot delete this.
3. Click **Edit routes** > **Add route**.
4. **Destination:** Enter `0.0.0.0/0` (This CIDR block represents "all other IP addresses," i.e., the public internet).
5. **Target:** Select **Internet Gateway**, and choose the `DemoIGW` you created earlier.
6. Click **Save changes**.

### The Result

Because `PublicSubnetA` and `PublicSubnetB` are associated with the `PublicRouteTable`, and that table has a route to the Internet Gateway, those subnets are now officially **Public Subnets**. Any EC2 instance launched inside them (with a public IP assigned) can now ping `google.com` or serve traffic to external users.

The instances in the private subnets are still completely isolated from the internet. We will address their architecture (NAT Gateways) in the next lesson.

---

## Interview Preparation: Public Routing

If an interviewer asks you to troubleshoot connectivity issues, you must methodically check the networking layers.

### Q&A Details

**Q1: A developer launches an EC2 instance into a custom VPC. They assigned it a public IP address and ensured the Security Group allows inbound SSH on Port 22. However, they are getting a "Connection Timed Out" error when trying to connect from their laptop. What is the most likely missing component?**
**Answer:** The subnet the instance was launched into is likely missing a route to the Internet Gateway. Just having a public IP and open Security Groups is not enough. The subnet's associated Route Table must have a specific route mapping destination `0.0.0.0/0` to an attached Internet Gateway target.

**Q2: In an AWS Route Table, what is the purpose of the default route that points to `local`, and can it be removed?**
**Answer:** The default route (e.g., `10.0.0.0/16` targeting `local`) matches the primary CIDR block of the VPC. Its purpose is to ensure that all internal traffic between subnets and resources within the VPC is routed locally without leaving the AWS network boundary. This is a fundamental, built-in rule of the VPC and it cannot be deleted or modified.

**Q3: What fundamentally makes a subnet "Public" versus "Private" in an AWS VPC?**

- **Answer:** The distinction is based entirely on the Route Table associated with the subnet. A subnet is considered "Public" if its associated Route Table contains a route directing `0.0.0.0/0` traffic to an attached Internet Gateway (IGW). If it lacks this route, it is a "Private" subnet.

**Q4: You launched an EC2 instance into a custom VPC. The instance has a Public IP address, and its Security Group explicitly allows Inbound Port 22 (SSH). However, when you try to connect via EC2 Instance Connect, it times out. What is the most likely architectural issue?**

- **Answer:** Because this is a custom VPC, the timeout is almost certainly a routing issue. The subnet where the EC2 instance resides likely does not have an Internet Gateway attached to the VPC, or the subnet's associated Route Table is missing the `0.0.0.0/0` route pointing to the Internet Gateway.

**Q5: We expect massive amounts of public internet traffic for an upcoming product launch. To ensure the network doesn't bottleneck, the lead engineer suggests attaching three Internet Gateways to our production VPC. Is this a valid strategy?**

- **Answer:** No, that is not possible or necessary. AWS enforces a strict one-to-one relationship between a VPC and an Internet Gateway; a VPC can only have one IGW attached. Furthermore, an IGW is a highly available, redundant, horizontally scaled AWS managed service that will not bottleneck your network traffic.

---

💡 Practical Developer Tip (Python / Boto3)

As a developer, configuring routing manually in the console is tedious. Here is how you can use Python to programmatically add the "Internet Route" to a Route Table!

```python
import boto3

ec2_client = boto3.client('ec2', region_name='us-east-1')

route_table_id = 'rtb-0abcd1234efgh5678'
igw_id = 'igw-0123456789abcdef0'

try:
    print(f"🚀 Adding Internet Route to {route_table_id}...")

    ec2_client.create_route(
        RouteTableId=route_table_id,
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw_id
    )

    print("✅ Successfully routed 0.0.0.0/0 to the Internet Gateway!")

except Exception as e:
    print(f"❌ Failed to create route: {e}")
```
