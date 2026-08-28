# AWS Advanced Network Topologies: Transit Gateway

As organizations scale in the cloud, managing individual **VPC Peering** connections quickly becomes an operational bottleneck. If you have $N$ VPCs, a full mesh peering design requires $\frac{N(N-1)}{2}$ connections. Adding VPNs, Direct Connect gateways, and multi-account setups on top of that turns your cloud network into an unmanageable mesh.

**AWS Transit Gateway (TGW)** is a regional hub-and-service router designed to solve this complexity by centralizing and simplifying infrastructure connectivity at scale.

---

## 1. What is AWS Transit Gateway?

An AWS Transit Gateway acts as a cloud router acting as a central **hub**. Instead of connecting VPCs and on-premises networks individually, every network connects once to the Transit Gateway (as a "spoke").

- **Transitive Routing:** Unlike VPC Peering (which is strictly non-transitive), Transit Gateway enables full transitive routing. If `VPC A` is attached to the TGW, and `VPC B` is attached to the TGW, they can communicate automatically, and both can communicate with your on-premises data center.
- **Regional & Global Scope:** A Transit Gateway is deployed within a specific AWS Region, but it can be peered with other Transit Gateways across different regions.
- **Cross-Account Sharing:** Using **AWS Resource Access Manager (RAM)**, you can share a Transit Gateway with other AWS accounts within your organization, allowing separate business units to tie into the same central network hub.
- **Granular Control:** You use **Transit Gateway Route Tables** to control precisely which attached VPCs or VPNs can communicate with one another, providing enterprise-grade network segmentation.
- **IP Multicast Support:** Transit Gateway is the **only** native AWS networking service that supports IP multicast traffic. If an exam question mentions multicast requirements, the answer is always Transit Gateway.

---

## 2. Scaling VPN Throughput with ECMP

By default, an individual AWS Site-to-Site VPN connection consists of two tunnels and has throughput limits (historically 1.25 Gbps per tunnel, though newer features support higher limits). If your on-premises office requires higher bandwidth over a VPN, a single connection will bottleneck.

Transit Gateway solves this by supporting **Equal-Cost Multi-Path (ECMP)** routing.

- **How ECMP Works:** ECMP is a routing strategy where packets are forwarded over multiple best paths simultaneously.
- **Aggregating Bandwidth:** By establishing **multiple** Site-to-Site VPN connections from your data center into the same Transit Gateway and using dynamic routing (BGP), AWS aggregates the tunnels.
- If one VPN connection provides baseline capacity, adding a second and third VPN connection multiplies your total aggregate throughput linearly across the paths using ECMP traffic load balancing.

---

## 3. Centralized Direct Connect Sharing

Transit Gateway also integrates smoothly with **Direct Connect Gateways**.

Instead of provisioning individual private virtual interfaces (VIFs) for every single VPC across multiple accounts, you can attach a Direct Connect Gateway directly to a Transit Gateway. This allows an entire multi-account AWS environment to share a single high-speed Direct Connect fiber connection cleanly and securely.

---

## Interview Preparation: Transit Gateway

### Summary

If an exam question or architectural review involves connecting "hundreds of VPCs," "sharing a Direct Connect across multiple accounts," "IP multicast," or "scaling VPN bandwidth past single-tunnel limits," the definitive answer is **AWS Transit Gateway**.

### Q&A Details

**Q1: A company has 40 distinct VPCs across 3 different AWS accounts. They need every VPC to be able to communicate with every other VPC, as well as with their on-premises data center via a Site-to-Site VPN. Managing VPC peering meshes has become impossible. What is the most scalable AWS service to implement?**
**Answer:** You should implement **AWS Transit Gateway**. It provides a hub-and-spoke architecture that eliminates complex peering meshes, supports transitive routing between all attached VPCs and VPNs, and can be shared across multiple AWS accounts using AWS Resource Access Manager (RAM).

**Q2: An engineering team needs to push data from their on-premises data center into AWS over a Site-to-Site VPN at speeds exceeding the standard single-tunnel cap of 1.25 Gbps. They are using dynamic routing (BGP). How can they optimize their architecture to achieve higher VPN throughput?**
**Answer:** They can establish **multiple Site-to-Site VPN connections** to an **AWS Transit Gateway** and leverage **Equal-Cost Multi-Path (ECMP)** routing. By configuring dynamic BGP routing across multiple parallel VPN attachments, the Transit Gateway will automatically load-balance traffic across the independent tunnels, aggregating the bandwidth.

**Q3: Which native AWS networking service must be used if an enterprise application deployed inside an Amazon VPC requires support for IP multicast communication with external clients?**
**Answer:** **AWS Transit Gateway**. Transit Gateway is the only routing service within AWS that natively supports IP multicast traffic across VPC attachments.
