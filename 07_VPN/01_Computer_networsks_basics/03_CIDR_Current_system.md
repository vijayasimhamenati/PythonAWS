# 🌐 Computer Networks: Classless Inter-Domain Routing (CIDR)

**Video Title:** CN | IP address Subnetting Supernetting | Classless Inter Domain Routing (CIDR)
**Instructor:** Prof. Ravindrababu Ravula
**Video Link:** [YouTube URL](https://www.youtube.com/watch?v=86RDE_bP1Bs)

---

## 1. The Problem with Classful Classification [[00:01](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D1)]

In the Classful system (Class A, B, C), the 32-bit IP address space was pre-cut into fixed networks.

**The "Big Cake" Analogy [[02:40](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D160)]:**
Imagine the address space as a big cake that has already been sliced into specific sizes. If you go to the Internet Assigned Numbers Authority (IANA) or your ISP to buy IP addresses, you have to take an entire pre-cut piece.

- If you only need 100 IP addresses, you must buy a **Class C** network, which gives you $2^8 = 256$ addresses.
- If you need 300 IP addresses, Class C is too small. You are forced to buy a **Class B** network, which gives you roughly 64,000 addresses, wasting thousands of them!

Because of this extreme lack of flexibility, the networking world moved to **Classless** addressing in the 1990s.

---

## 2. Introduction to CIDR (Classless) [[03:12](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D192)]

**CIDR (Classless Inter-Domain Routing)** ignores the strict Class A, B, and C boundaries.
Instead of rigid classes, if a user asks for exactly 1,000 IP addresses, IANA cuts a customized **block** of IP addresses that fits that requirement (rounding up to the nearest power of 2) and assigns it.

### The Challenge of Classless [[04:15](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D255)]

In Classful addressing, if an IP address started with `10.x.x.x`, you instantly knew it was Class A, meaning 8 bits were for the Network ID and 24 bits were for the Host ID.

Without classes, **how do you look at an IP address and know which part is the Block ID (Network ID) and which part is the Host ID?**

### The Solution: CIDR Notation (`/n`) [[05:29](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D329)]

We use slash notation to specify exactly how many bits belong to the Block ID.

**Example:** `20.10.30.50 / 20`

- `/20` means the **Block ID (Network ID) is exactly 20 bits**.
- Since an IP is 32 bits, the **Host ID is 12 bits** ($32 - 20 = 12$).
- The size of the block this IP belongs to is $2^{12}$ IP addresses.

---

## 3. The 3 Strict Rules for Forming CIDR Blocks [[08:46](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D526)]

You cannot just grab random IP addresses and call them a CIDR block. Every block must strictly obey three rules:

### Rule 1: All IP addresses must be Contiguous [[09:05](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D545)]

There can be no gaps or interleaving. If your block starts at `.10`, the next IPs must be `.11`, `.12`, `.13`, etc., in perfect sequence.

### Rule 2: The Block Size must be a Power of 2 [[09:46](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D586)]

You cannot ask for 100 IP addresses; you must ask for 128 ($2^7$).

**Why Power of 2? The Division Analogy [[11:50](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D710)]:**

- **In Decimal (Base 10):** If you divide `1234` by $10^2$ (100), the remainder is simply the least significant two digits (`34`) and the quotient is the most significant digits (`12`).
- **In Binary (Base 2):** If you have an $n$-bit binary number and divide it by $2^k$, the remainder is simply the **least significant $k$ bits**, and the quotient is the most significant remaining bits.
- Because computers operate in binary, making the block size a power of two ($2^n$) allows the router to separate the Host ID (remainder) and Block ID (quotient) instantly by just looking at the bits, without actual division operations.

### Rule 3: The First IP Address must be Evenly Divisible by the Size of the Block [[15:45](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D945)]

If your block size is $2^n$, the first IP address of that block, when divided by $2^n$, must leave a remainder of 0.

**Why? [[16:46](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D1006)]:**
As established above, the remainder of dividing by $2^n$ is the last $n$ bits. For the remainder to be 0, **the Host ID part of the first IP address must be all `0`s.**
If the first IP address starts with all `0`s in the Host ID part, it perfectly acts as the Block ID. Furthermore, you can sequentially count all the way up to all `1`s, completely filling out the $2^n$ block without any gaps.

---

## 4. Validating CIDR Blocks (Examples) [[20:10](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D1210)]

The instructor presented examples to check against the 3 rules.

### Example 1

**Given IP Range:** `100.1.2.32` through `100.1.2.47`

1. **Contiguous?** Yes (32 to 47 has no gaps).
2. **Power of 2?** The size is 16 IP addresses ($47 - 32 + 1 = 16$). 16 is $2^4$. Yes.
3. **First IP evenly divisible by Block Size ($2^4$)?**

- First IP: `100.1.2.32`. We look at the last octet: `32`.
- `32` in binary is `0010 0000`.
- Divide by $2^4 \rightarrow$ Look at the least significant 4 bits. They are `0000`.
- Remainder is 0. Yes!
  **Conclusion:** Valid CIDR Block.

### Example 2

**Given IP Range:** `150.10.20.64` through `150.10.20.127`

1. **Contiguous?** Yes.
2. **Power of 2?** Size is 64 ($2^6$). Yes.
3. **First IP evenly divisible by Block Size ($2^6$)?**

- First IP is `.64`.
- `64` in binary is `0100 0000`.
- Look at the least significant 6 bits: `000000`.
- Remainder is 0. Yes!
  **Conclusion:** Valid CIDR Block.

---

## 5. Representing CIDR Blocks and Finding Ranges [[27:36](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D1656)]

Instead of writing out a whole range, you pick **any** IP address inside the block and append the `/n` notation.

### Representing a Block [[28:13](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D1693)]:

Take Example 1 from above (Size: 16 IPs $\rightarrow 2^4 \rightarrow$ Host ID is 4 bits).

- 32 bits total - 4 bits Host ID = **28 bits Block ID**.
- CIDR Representation: **`100.1.2.32 /28`** (You could also write `100.1.2.40 /28`, it represents the same block).

### Deriving the Range from a CIDR IP [[33:22](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D2002)]:

**Given:** `20.10.30.35 /27`

- **Block ID:** 27 bits. **Host ID:** 5 bits ($32 - 27 = 5$).
- The split happens in the last octet (8 bits).
- Let's convert `35` (the last octet) to binary: `0010 0011`.
- Split it after the first 3 bits (because $24 + 3 = 27$ total Block ID bits):
- **Block part:** `001`
- **Host part:** `0 0011`

**To find the First IP Address (Block ID):** Put all `0`s in the Host part.

- `001` + `0 0000` = `0010 0000` = **Decimal 32**.
- First IP: `20.10.30.32`

**To find the Last IP Address (Directed Broadcast):** Put all `1`s in the Host part.

- `001` + `1 1111` = `0011 1111` = **Decimal 63**.
- Last IP: `20.10.30.63`

**Full Range:** `20.10.30.32` to `20.10.30.63`

---

To help visualize how the `/n` prefix dictates the number of available hosts and the division between network and host bits, you can experiment with this CIDR block explorer:

> **Note on Usable Hosts [[31:48](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D86RDE_bP1Bs%26t%3D1908)]:** Just like in classful addressing, the first IP address of a CIDR block is reserved for the **Block ID** and the last IP address is reserved for the **Directed Broadcast Address**. Therefore, a block size of 16 yields exactly **14 usable host IPs**.

---

Here are detailed GitHub-flavored Markdown notes derived directly from the video, capturing the instructor's exact explanations, derivations, and examples for Subnetting and VLSM in CIDR.

# 🌐 Computer Networks: Subnetting & VLSM in CIDR

**Video Title:** CN | IP address Subnetting Supernetting | Subnetting in CIDR, VLSM in CIDR
**Video Link:** [YouTube URL](https://www.youtube.com/watch?v=zYOgpo0SDBc)

---

## 1. Introduction: Subnetting in CIDR [[00:00](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DzYOgpo0SDBc%26t%3D0)]

Even when an organization receives a CIDR block (classless), they often need to divide that block internally into smaller subnetworks (subnets) for management and security.

### 📝 Example 1: Creating 2 Subnets [[00:14](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DzYOgpo0SDBc%26t%3D14)]

**Given Block:** `20.30.40.10 / 25`

**Step 1: Understand the Block Structure**

- `/25` means the **Block ID (Network part)** is **25 bits**.
- Since an IPv4 address is 32 bits, the **Host ID part** is $32 - 25 = \textbf{7 bits}$.
- Total IP addresses in this block = $2^7 = 128$.

**Step 2: Find the Base Block ID (Starting IP)**
To find the base Block ID, we look at the octet where the split happens.
25 bits means the split is in the **4th octet** (24 bits + 1 bit).

- Convert the 4th octet (`10`) to binary: `0000 1010`.
- The first 1 bit belongs to the Block ID. The remaining 7 bits belong to the Host ID.
- To find the starting IP, set all 7 Host ID bits to `0`.
- Base Block ID = `20.30.40.0 / 25`.

**Step 3: Subnet the Block into 2 Halves [[01:44](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DzYOgpo0SDBc%26t%3D104)]**
To create 2 subnets, we must borrow **1 bit** from the 7-bit Host ID part.

- **Subnet 1:** First bit is `0`.
- **Subnet 2:** First bit is `1`.

|                                  | Subnet 1                         | Subnet 2                |
| -------------------------------- | -------------------------------- | ----------------------- |
| **New Prefix Length**            | `/26` (25 original + 1 borrowed) | `/26`                   |
| **Host Bits Remaining**          | 6 bits ($2^6 = 64$ IPs)          | 6 bits ($2^6 = 64$ IPs) |
| **Network ID (First IP)**        | `20.30.40.0 /26`                 | `20.30.40.64 /26`       |
| **Directed Broadcast (Last IP)** | `20.30.40.63`                    | `20.30.40.127`          |

> **Key Takeaway [[06:52](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DzYOgpo0SDBc%26t%3D412)]:** The `/26` notation inherently acts as both the Subnet ID representation _and_ the Subnet Mask. A `/26` means the subnet mask is 26 `1`s followed by 6 `0`s (which is `255.255.255.192`).

---

## 2. Subnetting a CIDR Block into 4 Subnets [[07:20](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DzYOgpo0SDBc%26t%3D440)]

Using the same initial block: `20.30.40.0 / 25` (Host ID = 7 bits).
We want to divide it into **4 Subnets**.

To get 4 subnets, we must borrow **2 bits** from the 7-bit Host ID part.
The 2 borrowed bits will have the combinations: `00`, `01`, `10`, and `11`.
Because we borrowed 2 bits, the new prefix length for all subnets will be $25 + 2 = \textbf{/27}$.

### Calculating the Subnet IDs [[08:15](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DzYOgpo0SDBc%26t%3D495)]

We must look at the weights of the borrowed bits. Since they are the 7th and 6th bits (from the right) in the last octet, their decimal weights are **64** and **32**.

- **Subnet 1 (`00`):** Base + 0 = `20.30.40.0 / 27`
- **Subnet 2 (`01`):** Base + 32 = `20.30.40.32 / 27`
- **Subnet 3 (`10`):** Base + 64 = `20.30.40.64 / 27`
- **Subnet 4 (`11`):** Base + 96 = `20.30.40.96 / 27`

_(Each subnet has $32 - 27 = 5$ bits for hosts, giving $2^5 = 32$ IP addresses per subnet)._

---

## 3. Variable Length Subnet Masking (VLSM) in CIDR [[15:17](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DzYOgpo0SDBc%26t%3D917)]

ISPs constantly use VLSM to hand out unequal blocks of IP addresses to different companies.

### 📝 Example: ISP Allocation Scenario [[24:27](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DzYOgpo0SDBc%26t%3D1467)]

An ISP owns the block: **`40.30.10.0 / 20`**

- **Block ID:** 20 bits.
- **Host ID:** 12 bits ($32 - 20 = 12$).
- **Total IP Addresses:** $2^{12} = 4096$.

**The Requirement [[26:49](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DzYOgpo0SDBc%26t%3D1609)]:**
The ISP needs to divide this block into 3 unequal parts:

1. **Company A:** Needs $2^{11}$ (2048) IPs.
2. **Company B:** Needs $2^{10}$ (1024) IPs.
3. **ISP Keep:** Wants to keep $2^{10}$ (1024) IPs for itself.

### Finding the Base Range [[25:22](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DzYOgpo0SDBc%26t%3D1522)]

First, where does the 20-bit split happen? It happens in the **3rd octet** (16 bits + 4 bits).
Let's convert `10` (the 3rd octet) to binary: `0000 1010`.

- The first 4 bits (`0000`) belong to the Block ID.
- The remaining 4 bits, plus the entire 4th octet, belong to the Host ID.

To find the Base Block ID, put `0`s in all Host ID bits: `40.30.0.0 / 20`.
_(Notice how the 3rd octet changed from `10` to `0` because those 1 bits were in the Host ID part!)_

### Performing the VLSM Split [[27:33](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DzYOgpo0SDBc%26t%3D1653)]

The Host ID part is 12 bits.
We split the network hierarchically.

**Step 1: Divide the block in half.**
Borrow the **1st bit** of the Host ID (which has a place value of $2^3 = 8$ in the 3rd octet).

- **Half 1 (`0`):** `40.30.0.0 / 21` (Size = $2^{11}$). $\rightarrow$ **Give this to Company A.**
- **Half 2 (`1`):** `40.30.8.0 / 21` (Size = $2^{11}$).

**Step 2: Divide Half 2 in half again.**
Borrow the **2nd bit** of the Host ID (which has a place value of $2^2 = 4$ in the 3rd octet).

- **Quarter 1 (`10`):** `40.30.8.0 / 22` (Size = $2^{10}$). $\rightarrow$ **Give this to Company B.**
- **Quarter 2 (`11`):** `40.30.12.0 / 22` (Size = $2^{10}$). $\rightarrow$ **ISP keeps this.**

---

## 4. Final VLSM Allocation Table [[30:22](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DzYOgpo0SDBc%26t%3D1822)]

| Entity         | Subnet ID    | Prefix / Mask | Host Bits | IPs Available | Range (First to Last)          |
| -------------- | ------------ | ------------- | --------- | ------------- | ------------------------------ |
| **Company A**  | `40.30.0.0`  | `/21`         | 11 bits   | 2048          | `40.30.0.0` to `40.30.7.255`   |
| **Company B**  | `40.30.8.0`  | `/22`         | 10 bits   | 1024          | `40.30.8.0` to `40.30.11.255`  |
| **ISP (Self)** | `40.30.12.0` | `/22`         | 10 bits   | 1024          | `40.30.12.0` to `40.30.15.255` |

### Alternative Valid Split [[33:15](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DzYOgpo0SDBc%26t%3D1995)]

As with all VLSM, the hierarchical split could be done in reverse. You could give the _second_ half to Company A, and split the _first_ half for Company B and the ISP.

- **Company A (Second Half):** `40.30.8.0 / 21`
- **Company B (First Quarter):** `40.30.0.0 / 22`
- **ISP (Second Quarter):** `40.30.4.0 / 22`

Both solutions are perfectly valid depending on how the network administrator chooses to allocate the bits.

---

# 🌐 Computer Networks: Supernetting or Route Aggregation

**Video Title:** CN | IP address Subnetting Supernetting | Supernetting or Aggregation
**Instructor:** Prof. Ravindrababu Ravula
**Video Link:** [YouTube URL](https://www.youtube.com/watch?v=MnqP_TVwkbs)

---

## 1. What is Supernetting (Route Aggregation)? [[00:01](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D1)]

While **Subnetting** is the process of dividing a large network into many smaller networks (for security and easy maintenance), **Supernetting (or Aggregation)** is the exact opposite. It is the process of combining multiple small networks into one logical "Big Network."

### Why do we need Supernetting? [[00:34](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D34)]

Every network in the world requires an entry in a router's **Routing Table**.
If we keep dividing networks into smaller subnets, the number of routing table entries will increase exponentially.

- A massive routing table takes a router a long time to process, slowing down network traffic.
- **Solution:** By aggregating many small networks into one supernet, a core router only needs **one routing table entry** to represent all of them.

### The Post Office Analogy [[02:04](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D124)]

Think of how international mail works. If a post office in the US needs to send a letter to a specific street in Tirupati, Andhra Pradesh, India:

- The US Post Office does not check its database for "Tirupati" or the specific street.
- It only looks at **"India"** and forwards the letter to the Indian routing system.
- Once the letter reaches India, the local Indian post office looks at the state (Andhra Pradesh), and then the local city office sorts it to the street.
- **Supernetting works the same way:** A core router (US Post Office) just sees the single Supernet entry and forwards it to the local router. The local router (Indian Post Office) retains the specific subnet entries to deliver the packet locally.

---

## 2. The 3 Rules of Supernetting [[03:05](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D185)]

You cannot randomly pick a few networks and combine them. Just like CIDR block creation, networks must obey three strict rules to be eligible for aggregation:

1. **Contiguousness:** All the network IDs must be numerically continuous (no gaps).
2. **Equal Size & Power of 2:** All the networks you want to merge must be the exact same size, and the number of networks you are combining must be a power of 2 (e.g., combine 2, 4, 8, or 16 networks. You _cannot_ combine exactly 3 or 10 networks).
3. **Divisibility:** The First Network ID must be evenly divisible by the **total size** of the proposed supernet.

---

## 3. Example 1: Aggregating 4 Networks [[04:35](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D275)]

Let's say we have 4 small Class C networks (`/24`):

1. `200.1.0.0 /24`
2. `200.1.1.0 /24`
3. `200.1.2.0 /24`
4. `200.1.3.0 /24`

### Checking the 3 Rules [[05:20](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D320)]:

1. **Contiguous?** Yes. (`.0`, `.1`, `.2`, `.3`).
2. **Equal Size & Power of 2?** Yes. Each network has $2^8 = 256$ IPs. We are combining exactly 4 networks ($2^2$).
3. **Divisible?**

- Total Supernet Size = 4 networks $\times$ 256 IPs = $1024$ ($2^{10}$) IPs.
- First Network ID: `200.1.0.0`.
- Since we are checking divisibility by $2^{10}$, we look at the least significant **10 bits** of the first IP.
- `200.1.0.0` in binary (last two octets): `00000000 . 00000000`. The last 10 bits are all zeros.
- Remainder is 0. Yes!

### Calculating the Supernet Mask via Binary Matching [[10:48](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D648)]

Instead of writing 4 routing table entries, what is the single **Supernet Mask**?
Write out the network IDs in binary to see which bits are fixed (same across all 4) and which vary:

- `200.1.0.0` $\rightarrow$ `200 . 1 . 00000000 . 00000000`
- `200.1.1.0` $\rightarrow$ `200 . 1 . 00000001 . 00000000`
- `200.1.2.0` $\rightarrow$ `200 . 1 . 00000010 . 00000000`
- `200.1.3.0` $\rightarrow$ `200 . 1 . 00000011 . 00000000`

**Observation:**

- `200` is fixed (8 bits).
- `1` is fixed (8 bits).
- In the 3rd octet, the first 6 bits are fixed as `000000`. The last 2 bits are varying (`00`, `01`, `10`, `11`).

**The Mask Rule:** Put `1`s for fixed bits and `0`s for varying/host bits.

- `11111111 . 11111111 . 11111100 . 00000000`
- Decimal: **`255.255.252.0`**

### The Shortcut Method [[15:35](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D935)]

Instead of drawing out binary, use the math shortcut:

1. **Supernet ID:** If the rules pass, the Supernet ID is _always_ the very first network's ID. $\rightarrow$ `200.1.0.0`
2. **Supernet Mask (/n):** We found the total size is $2^{10}$.

- Host ID bits = 10.
- Network ID bits = $32 - 10 = 22$ bits.
- Prefix notation: **`/22`**.
- Therefore, the single routing entry is: **`200.1.0.0 /22`**.

---

## 4. Example 2: Aggregating 16 Networks [[18:32](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D1112)]

Let's say we are given 16 contiguous Class C networks:

- `200.1.32.0 /24`
- `200.1.33.0 /24`
- ... up to `200.1.47.0 /24`

### Checking the Rules & Calculating [[19:09](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D1149)]:

1. **Contiguous?** Yes (`32` to `47` is sequential).
2. **Size?** 16 networks $\times 2^8$ IPs = $2^4 \times 2^8 = \textbf{2^{12}}$ total IPs.
3. **Divisible?** First IP is `200.1.32.0`.

- Look at the least significant 12 bits of `32.0`
- `32` in binary is `00100000`.
- Combined last 12 bits: `0000 . 00000000`. They are all zero. Yes!

**The Shortcut Result [[22:23](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D1343)]:**

- **Supernet ID:** First IP $\rightarrow$ **`200.1.32.0`**
- **Supernet Mask:** Total size is $2^{12}$ (12 host bits). Network bits = $32 - 12 = \textbf{20}$.
- **Final Routing Entry:** **`200.1.32.0 /20`**
- _(In decimal mask, 20 ones is `255.255.240.0`)_

---

## 5. Example 3: Hierarchical Aggregation (Unequal Sizes) [[24:03](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D1443)]

What if you are given networks of _unequal_ sizes?

- N1: `100.1.2.0 /25` (Size: $2^7 = 128$ IPs)
- N2: `100.1.2.128 /26` (Size: $2^6 = 64$ IPs)
- N3: `100.1.2.192 /26` (Size: $2^6 = 64$ IPs)

**Rule Check:** You **cannot** aggregate all three simultaneously because they are not of equal size. However, you can merge them hierarchically!

### Step 1: Merge the Equal Networks [[25:02](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D1502)]

Look at N2 and N3. They are both `/26` (64 IPs each).

1. Contiguous? Yes (128 and 192 are sequential in a `/26` block).
2. Equal size? Yes ($2^6$).
3. Divisible?

- Total size of N2 + N3 = $64 + 64 = 128$ ($2^7$).
- First IP is `100.1.2.128`. In binary, `.128` is `10000000`. The least significant 7 bits are `0000000`. Divisible!

4. **Merged Result:**

- Supernet ID = First IP $\rightarrow$ `100.1.2.128`
- Mask = $32 - 7 = 25 \rightarrow \textbf{/25}$
- New Network: **`100.1.2.128 /25`**

### Step 2: Merge the Remaining Networks [[27:33](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D1653)]

Now look at N1 and our newly created supernet:

- N1: `100.1.2.0 /25`
- New: `100.1.2.128 /25`

1. Contiguous? Yes (0 to 127, then 128 to 255).
2. Equal size? Yes ($2^7$ each).
3. Divisible?

- Total size = $2^7 + 2^7 = 2^8$ (256 IPs).
- First IP is `100.1.2.0`. Least significant 8 bits are zero. Divisible!

4. **Final Merged Result [[28:42](https://www.google.com/search?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DMnqP_TVwkbs%26t%3D1722)]:**

- Supernet ID = First IP $\rightarrow$ `100.1.2.0`
- Mask = $32 - 8 = 24 \rightarrow \textbf{/24}$
- Final Supernet Entry: **`100.1.2.0 /24`**

_(Note: We successfully compressed three routing table entries into a single `/24` entry)._
