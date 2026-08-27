# 🌐 Computer Networks: Subnets, Subnet Mask, and Routing

**Video Title:** CN | IP address Subnetting Supernetting | Subnets, Subnet Mask, Routing
**Instructor:** Prof. Ravindrababu Ravula
**Video Link:** [YouTube URL](https://www.youtube.com/watch?v=3QWrq5gN8VY)

---

## 1. The Need for Subnetting [[00:02](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D2)]

In Classful addressing, networks are very large. For example, a single Class A network has roughly 16 million hosts. In a practical industry environment, maintaining such a massive, flat network is highly problematic.

**Why Subnet?**

1. **Maintenance:** Managing 16 million hosts in one single network is an administrative nightmare. Smaller networks are much easier to maintain.
2. **Security:** If you have different departments (e.g., Developers, Testing, Maintenance), you don't want them all in the same loose network. If a developer team has a core code server, you want to isolate and protect it from other departments. Subnetting allows you to divide the big network into secure, manageable chunks.

**The Disadvantage of Subnetting:**

- **Routing Complexity [[02:09](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D129)]:** Without subnetting, routing involves 3 steps (Network $\rightarrow$ Host $\rightarrow$ Process). With subnetting, it becomes a 4-step process (Network $\rightarrow$ **Subnet** $\rightarrow$ Host $\rightarrow$ Process). However, the advantages far outweigh this complexity.

---

## 2. Subnetting a Class C Network: Example 1 (2 Subnets) [[03:04](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D184)]

Let's assume an organization buys a **Class C** Network: `200.1.2.0`

- **Network ID Part:** 24 bits (`200.1.2`)
- **Host ID Part:** 8 bits (giving 256 total IP addresses, or 254 configurable hosts).

### How to split this into 2 Subnets:

To divide the network into 2 parts, we must **borrow 1 bit** from the Host ID part [[04:19](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D259)].

We take the 8 bits of the Host ID and split it based on the first bit:

- **Subnet 1:** Starts with `0` (Range: `00000000` to `01111111`) $\rightarrow$ Decimal `0` to `127`.
- **Subnet 2:** Starts with `1` (Range: `10000000` to `11111111`) $\rightarrow$ Decimal `128` to `255`.

### Details of the 2 Subnets [[07:07](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D427)]:

|                                          | Subnet 1       | Subnet 2         |
| ---------------------------------------- | -------------- | ---------------- |
| **Network ID (First IP)**                | `200.1.2.0`    | `200.1.2.128`    |
| **Usable IP Range**                      | `.1` to `.126` | `.129` to `.254` |
| **Directed Broadcast Address (Last IP)** | `200.1.2.127`  | `200.1.2.255`    |

> **Loss of IPs due to Subnetting [[11:42](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D702)]:**
> Originally, the Class C network had 254 usable hosts. By splitting it into 2 subnets, each subnet loses 2 addresses (Network ID and Directed Broadcast).
> Subnet 1 has 126 hosts. Subnet 2 has 126 hosts. Total usable hosts = **252**. Subnetting always results in a loss of available IP addresses.

### The Perspective Problem (Internal vs External) [[09:31](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D571)]

Look at the addresses. The Network ID of Subnet 1 (`200.1.2.0`) is the exact same as the Network ID of the _entire_ Class C block. The DBA of Subnet 2 (`200.1.2.255`) is the exact same as the DBA of the _entire_ Class C block.

- **If you are OUTSIDE the organization:** You don't know subnets exist. Sending a packet to `.255` broadcasts it to the _entire_ Class C block.
- **If you are INSIDE the organization:** The internal router knows about subnets. If it receives a packet for `.255` from outside, it broadcasts it to _everyone_. If a host inside Subnet 1 sends a packet to `.255`, the internal router knows it is only meant for Subnet 2.

---

## 3. Subnetting a Class C Network: Example 2 (4 Subnets) [[13:04](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D784)]

Now, let's divide the same `200.1.2.0` Class C network into **4 Subnets**.
To divide into 4 parts, we must **borrow 2 bits** from the 8-bit Host ID part.

The 4 subnets are defined by the first two bits: `00`, `01`, `10`, and `11`.

### Details of the 4 Subnets [[14:01](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D841)]:

| Subnet | Binary Prefix | IP Range         | Network ID (First IP) | Directed Broadcast (Last IP) |
| ------ | ------------- | ---------------- | --------------------- | ---------------------------- |
| **S1** | `00`          | `.0` to `.63`    | `200.1.2.0`           | `200.1.2.63`                 |
| **S2** | `01`          | `.64` to `.127`  | `200.1.2.64`          | `200.1.2.127`                |
| **S3** | `10`          | `.128` to `.191` | `200.1.2.128`         | `200.1.2.191`                |
| **S4** | `11`          | `.192` to `.255` | `200.1.2.192`         | `200.1.2.255`                |

_(Note: We have now wasted 8 total IP addresses across the 4 subnets.)_

---

## 4. The Subnet Mask [[18:44](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D1124)]

When an internal router receives a packet, say for destination `200.1.2.130`, how does it quickly know mathematically which of the 4 subnets that IP belongs to? It uses a **Subnet Mask**.

**Definition:** A Subnet Mask is a 32-bit number where:

- `1`s represent the **Network ID part + Subnet ID part**.
- `0`s represent the **Host ID part**.

### Calculating the Subnet Mask for the 4-Subnet Example [[19:39](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D1179)]:

1. It is a Class C address, so the first 24 bits are Network ID (All `1`s).
2. We borrowed 2 bits for the Subnet ID (These become `1`s).
3. We are left with 6 bits for the Host ID (These become `0`s).

Binary Mask: `11111111 . 11111111 . 11111111 . 11000000`
Dotted Decimal Mask: **`255.255.255.192`**

### Bitwise AND Operation [[21:32](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D1292)]

To find the network an IP belongs to, the router performs a **Bitwise AND** between the Destination IP and the Subnet Mask.

**Example:** Destination IP is `200.1.2.130`.

- `200 AND 255 = 200` _(Any number AND 255 is the number itself)_
- `1 AND 255 = 1`
- `2 AND 255 = 2`
- `130 AND 192` $\rightarrow$ Let's look at binary:
- `130` = `10000010`
- `192` = `11000000`
- **AND** = `10000000` (which is decimal **128**)

**Result:** `200.1.2.128`. The router instantly knows this packet belongs to Subnet 3 (S3).

---

## 5. The Routing Table [[26:06](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D1566)]

The router uses the Subnet Mask to build a **Routing Table** to decide which physical interface (cable) to send a packet down.

Let's say the router has 5 interfaces: `A`, `B`, `C`, `D` (for the 4 subnets) and `E` (external internet).

### Routing Table Example [[27:04](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D1624)]:

| Network ID          | Subnet Mask       | Interface |
| ------------------- | ----------------- | --------- |
| `200.1.2.0`         | `255.255.255.192` | **A**     |
| `200.1.2.64`        | `255.255.255.192` | **B**     |
| `200.1.2.128`       | `255.255.255.192` | **C**     |
| `200.1.2.192`       | `255.255.255.192` | **D**     |
| `0.0.0.0` (Default) | `0.0.0.0`         | **E**     |

_(This is called **Fixed-Length Subnet Masking** because all subnets have the exact same mask size)._

### The 3 Rules of Routing Processing [[29:56](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3QWrq5gN8VY%26t%3D1796)]:

When a packet arrives, the router bitwise ANDs the destination IP with every Subnet Mask in the table:

1. **Exactly One Match:** If the result matches exactly one Network ID in the table, forward the packet out that specific interface.
2. **More Than One Match:** If the packet matches multiple entries (possible in variable-length subnetting), the router must choose the entry with the **Longest Subnet Mask** (the mask with the most `1`s).
3. **No Match (Default Route):** If it matches nothing in the internal network, it falls to the `0.0.0.0` default entry. ANDing any IP with `0.0.0.0` results in `0.0.0.0`, so the packet is forwarded out Interface `E` to the external network.

---

# 🌐 Computer Networks: Variable Length Subnet Masking (VLSM)

**Video Link:** [YouTube URL](https://www.youtube.com/watch?v=GJrS5ckgjAs)

---

## 1. Introduction to VLSM [[00:01](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DGJrS5ckgjAs%26t%3D1)]

In Fixed-Length Subnet Masking (the previous examples), we divided a network into subnets of _equal sizes_ (e.g., all subnets got 64 IP addresses).
However, in practical networking, requirements are rarely equal.

**Scenario:** We want to divide a Class C network (`200.1.2.0`) into **3 parts**:

- Subnet 1: Needs 128 IP addresses.
- Subnet 2: Needs 64 IP addresses.
- Subnet 3: Needs 64 IP addresses.

_(Total addresses needed = $128 + 64 + 64 = 256$. This perfectly fits a Class C network)._

If we borrow 2 bits standardly, we get 4 subnets of 64 IPs each. This does not meet the requirement.
To achieve different sizes, we use **Variable Length Subnet Masking (VLSM)**.

---

## 2. How VLSM Works: Step-by-Step [[03:00](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DGJrS5ckgjAs%26t%3D180)]

Instead of splitting all subnets at once, VLSM splits the network hierarchically.

### Step 1: Split the Network in Half

Take the 8 bits of the Host ID part. Choose the **first bit** to divide the network into two equal halves (128 addresses each).

- **First Half (Starts with `0`):** Addresses `.0` to `.127` (Size: 128 IPs).
- **Second Half (Starts with `1`):** Addresses `.128` to `.255` (Size: 128 IPs).

_At this point, we have one subnet of 128. We keep the First Half as Subnet 1._

### Step 2: Split the Remaining Half

Take the Second Half (which starts with `1`) and choose the **second bit** to split it again.

- **Starts with `10`:** Addresses `.128` to `.191` (Size: 64 IPs). $\rightarrow$ _This is Subnet 2._
- **Starts with `11`:** Addresses `.192` to `.255` (Size: 64 IPs). $\rightarrow$ _This is Subnet 3._

---

## 3. Subnet IDs and Directed Broadcast Addresses (VLSM) [[04:12](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DGJrS5ckgjAs%26t%3D252)]

Let's look at the exact IPs for our 3 newly created unequal subnets.

### Subnet 1 (128 Addresses)

- **Binary Prefix:** `0` (1 bit borrowed)
- **Subnet ID:** `200.1.2.0` _(Host part = `00000000`)_
- **Directed Broadcast Address:** `200.1.2.127` _(Host part = `01111111`)_

### Subnet 2 (64 Addresses)

- **Binary Prefix:** `10` (2 bits borrowed)
- **Subnet ID:** `200.1.2.128` _(Host part = `10000000`)_
- **Directed Broadcast Address:** `200.1.2.191` _(Host part = `10111111`)_

### Subnet 3 (64 Addresses)

- **Binary Prefix:** `11` (2 bits borrowed)
- **Subnet ID:** `200.1.2.192` _(Host part = `11000000`)_
- **Directed Broadcast Address:** `200.1.2.255` _(Host part = `11111111`)_

---

## 4. Calculating the Variable Subnet Masks [[06:55](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DGJrS5ckgjAs%26t%3D415)]

In VLSM, because the subnet sizes are different, **the Subnet Masks will be different** for each subnet.

- _Rule:_ The number of `1`s in the Subnet Mask = Network ID bits + Subnet ID bits (bits borrowed).

**For Subnet 1 (128 addresses):**

- Network ID (24 bits) + Subnet ID (1 bit borrowed) = **25 `1`s**.
- Binary: `11111111.11111111.11111111.10000000`
- **Subnet Mask:** `255.255.255.128`

**For Subnet 2 and Subnet 3 (64 addresses each):**

- Network ID (24 bits) + Subnet ID (2 bits borrowed) = **26 `1`s**.
- Binary: `11111111.11111111.11111111.11000000`
- **Subnet Mask:** `255.255.255.192`

> **Key Observation [[09:26](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DGJrS5ckgjAs%26t%3D566)]:**
> The larger the network size, the _smaller_ the subnet mask.
> The smaller the network size, the _larger_ the subnet mask.

### Alternative Valid VLSM Split [[10:15](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DGJrS5ckgjAs%26t%3D615)]

You don't _have_ to split the second half. You could keep the second half (starting with `1`) as the 128-IP subnet, and split the first half (starting with `0`) into two 64-IP subnets (`00` and `01`). Both are perfectly valid engineering solutions.

---

## 5. The Routing Table with VLSM [[12:42](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DGJrS5ckgjAs%26t%3D762)]

Let's assume our router is connected to these 3 subnets via interfaces A, B, and C.

| Network ID          | Subnet Mask       | Interface |
| ------------------- | ----------------- | --------- |
| `200.1.2.0`         | `255.255.255.128` | **A**     |
| `200.1.2.128`       | `255.255.255.192` | **B**     |
| `200.1.2.192`       | `255.255.255.192` | **C**     |
| `0.0.0.0` (Default) | `0.0.0.0`         | **D**     |

### The "Longest Subnet Mask" Rule [[14:28](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DGJrS5ckgjAs%26t%3D868)]

Because masks vary in length, it is possible for a single IP address to match _multiple_ entries when bitwise ANDing.

- **Rule:** If there are multiple matches, the router will always choose the entry with the **longest Subnet Mask** (the one with the most `1`s).

---

## 6. Deriving Information directly from a Subnet Mask [[15:19](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DGJrS5ckgjAs%26t%3D919)]

If you are only given a Subnet Mask: `255.255.255.192`. What can you determine?

1. **Convert to binary:**
   `11111111.11111111.11111111.11000000`
2. **Count the bits:**

- Total `1`s = **26** (Network ID + Subnet ID)
- Total `0`s = **6** (Host ID)

### What can we know?

- **Size of Subnet:** Because there are 6 zeros, the number of IPs per subnet is always $2^6 = 64$.
- **Number of Subnets:** We _cannot_ know this unless we are told the original Class.
- **If it was Class A:** Network ID = 8 bits. Subnet ID = $26 - 8 = 18$ bits. ($2^{18}$ subnets possible). [[18:11](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DGJrS5ckgjAs%26t%3D1091)]
- **If it was Class B:** Network ID = 16 bits. Subnet ID = $26 - 16 = 10$ bits. ($2^{10}$ subnets possible).
- **If it was Class C:** Network ID = 24 bits. Subnet ID = $26 - 24 = 2$ bits. ($2^2 = 4$ subnets possible). [[19:09](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DGJrS5ckgjAs%26t%3D1149)]

---

## 7. Practical vs. Theoretical Subnet Masks [[21:15](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DGJrS5ckgjAs%26t%3D1275)]

- **Practical Rule:** A valid Subnet Mask MUST contain a continuous run of `1`s followed by a continuous run of `0`s (e.g., `11111111.11111111.11111111.11000000`).
- **Theoretical Anomaly [[21:43](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DGJrS5ckgjAs%26t%3D1303)]:** Sometimes theoretical questions use a non-contiguous mask like `255.255.255.15`.
- `15` in binary is `00001111`.
- Why don't we use this in practice? [[22:45](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DGJrS5ckgjAs%26t%3D1365)] Because if you use least significant bits for subnetting, the IP addresses wouldn't form clean ranges. Instead of `0 to 127`, Subnet 1 would get all the _even_ IPs (`0, 2, 4, 6...`) and Subnet 2 would get all the _odd_ IPs (`1, 3, 5, 7...`). This is impossible to route efficiently.
