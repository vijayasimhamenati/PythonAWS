# AWS Networking: CIDR, IPv4, and VPC Basics

To understand networking in AWS (Security Groups, Route Tables, and VPCs), you must first understand how IP addresses are allocated and structured. This is handled using **CIDR** (Classless Inter-Domain Routing).

## 1. What is CIDR?

CIDR is a method for allocating IP addresses and IP routing. It helps define entire _ranges_ of IP addresses using a simple, compact string rather than listing every single IP out individually.

A CIDR block has two components:

- **Base IP:** The starting IP address of the range (e.g., `10.0.0.0` or `192.168.0.0`).
- **Subnet Mask:** The slash number (e.g., `/16`, `/24`) that defines how many bits of the IP address are fixed, and how many are allowed to change.

### How Subnet Masks Work

An IPv4 address is made of 4 "octets" (e.g., `X.X.X.X`). The subnet mask dictates how many IPs are available in that range:

- **`/32` (1 IP):** No octets can change. Represents a single, specific computer (e.g., `192.168.1.5/32`).
- **`/24` (256 IPs):** The last octet can change. (e.g., `192.168.1.0/24` covers `192.168.1.0` to `192.168.1.255`).
- **`/16` (65,536 IPs):** The last two octets can change. (e.g., `10.0.0.0/16` covers `10.0.0.0` to `10.0.255.255`).
- **`/8` (16.7 million IPs):** The last three octets can change.
- **`/0` (All IPs):** All octets can change. `0.0.0.0/0` means the entire internet.

---

## 2. Public vs. Private IPv4 Ranges

The Internet Assigned Numbers Authority (IANA) reserved specific blocks of IPv4 addresses strictly for **private, local networks** (LANs). These IP addresses cannot be routed over the public internet.

When creating a Virtual Private Cloud (VPC) in AWS, it is highly recommended to use these private ranges:

- `10.0.0.0/8` (Used for large enterprise networks)
- `172.16.0.0/12` (AWS Default VPC uses a subset of this)
- `192.168.0.0/16` (Common for home routers)

Everything else (excluding a few specialized ranges) is a **Public IP** routed on the public internet.

---

## 3. The Default VPC

Every new AWS account comes with a **Default VPC** in every region. This exists so beginners can launch EC2 instances instantly without having to understand complex networking.

**Characteristics of the Default VPC:**

- **Size:** It uses the `172.31.0.0/16` CIDR block.
- **Subnets:** It automatically provisions a `/20` subnet (4,096 IPs) in every single Availability Zone in that region.
- **Connectivity:** It comes pre-configured with an Internet Gateway, meaning any EC2 instance launched inside it automatically receives a Public IP and can connect to the internet.

---

## 4. Custom VPC Limits & The "5 Reserved IPs" Rule

When you graduate to building your own Custom VPCs, you must abide by strict AWS boundaries:

- **VPC Size Limits:** The largest VPC you can create is a `/16` (65,536 IPs). The smallest VPC you can create is a `/28` (16 IPs).
- **The 5 Reserved IPs:** If you create a `/24` subnet, the math dictates you have 256 IPs. However, AWS only gives you **251 usable IPs**. AWS reserves the first four and the last IP in every subnet for networking purposes:

1. `.0`: Network Address
2. `.1`: VPC Router
3. `.2`: AWS DNS Server
4. `.3`: Reserved by AWS for future use
5. `.255`: Network Broadcast Address (AWS does not support broadcast, but reserves it anyway)

---

## Interview Preparation: VPC & CIDR

### Summary

Interviewers will test your understanding of AWS architectural limits and your ability to size a network properly. If a scenario asks why an instance cannot get an IP address, or why two networks cannot peer, look out for overlapping CIDR blocks or exhausted subnet capacity.

### Q&A Details

**Q1: You are designing the network architecture for a new multi-region enterprise application. You plan to connect multiple Custom VPCs together using VPC Peering. What is the most critical rule you must follow when assigning CIDR blocks to these VPCs?**
**Answer:** The CIDR blocks across the different VPCs must **never overlap**. If VPC A uses `10.0.0.0/16` and VPC B uses `10.0.0.0/16`, the VPC routers will not know where to send traffic, and VPC Peering will completely fail. You must allocate unique, non-overlapping private IP ranges (e.g., `10.1.0.0/16` and `10.2.0.0/16`).

**Q2: We need to provision a tiny, highly restricted subnet in AWS just to host 14 backend database instances. A junior developer attempts to create a `/28` subnet to perfectly fit the 14 instances, but AWS throws an error when launching the final 3 databases. Why?**
**Answer:** While a `/28` CIDR block mathematically contains 16 IP addresses, AWS automatically reserves 5 IP addresses in every subnet (Network, VPC Router, DNS, Future Use, Broadcast). This means a `/28` subnet only provides 11 usable IP addresses. To host 14 instances, the developer must provision a slightly larger subnet, such as a `/27`.

**Q3: Is it possible to create a custom AWS VPC with a massive `/8` CIDR block to ensure we never run out of IP addresses?**
**Answer:** No. AWS imposes a hard limit on VPC sizes. The largest IPv4 CIDR block you can assign to a VPC or a subnet is a `/16` (which provides 65,536 IP addresses), and the smallest is a `/28`. If more IPs are needed, you can associate up to 5 secondary CIDR blocks to the VPC later, but none can exceed the `/16` limit.
