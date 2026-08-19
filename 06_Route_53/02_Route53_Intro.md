# Amazon Route 53: Introduction, DNS Records, and Hosted Zones

## 1. What is Amazon Route 53?

Amazon Route 53 is a highly available, scalable, fully managed, and **Authoritative DNS** web service. It also acts as a Domain Registrar, meaning you can buy domain names (like `example.com`) directly through AWS.

* **Authoritative:** This means the customer has full control over the DNS records. You dictate the final truth of where traffic should go.
* **The 100% SLA:** Route 53 is the *only* service in AWS that guarantees a **100% Availability Service Level Agreement (SLA)**. It is engineered to never go down.
* **Why "53"?** The name is a reference to TCP/UDP Port 53, which is the traditional port used by DNS services globally.

**How it works conceptually:**
When a client requests `example.com`, Route 53 acts as the Authoritative Name Server. It reads the DNS records you configured and replies, *"You are looking for the IP `54.22.33.44`,"* allowing the client to connect directly to your underlying EC2 instance.

---

## 2. DNS Records in Route 53

A Hosted Zone contains DNS Records. Each record defines how you want to route traffic for a specific domain or subdomain.

A standard Route 53 record contains the following information:

* **Domain/Subdomain Name:** (e.g., `api.example.com`)
* **Record Type:** (e.g., A, AAAA, CNAME)
* **Value:** (e.g., `12.34.56.78`)
* **Routing Policy:** How Route 53 responds to queries (e.g., Simple, Weighted, Latency).
* **TTL (Time to Live):** The amount of time the record is cached at local DNS resolvers before they must ask Route 53 for an update.

### Important Record Types (Exam Focus)

| Type | Function | Rule to Remember |
| --- | --- | --- |
| **A** | Maps a hostname to an **IPv4** address. | The most common record (e.g., `example.com` ➡️ `1.2.3.4`). |
| **AAAA** | Maps a hostname to an **IPv6** address. | The modern equivalent of an A record. |
| **CNAME** | Maps a hostname to another **Hostname**. | **CRITICAL:** You cannot create a CNAME at the "Zone Apex" or root domain (e.g., `example.com` is illegal; `[www.example.com](https://www.example.com)` is fine). |
| **NS** | **Name Server** records. | These are the specific IP addresses of the servers that control routing for your domain. |

---

## 3. Hosted Zones: Public vs. Private

A **Hosted Zone** is simply a container that holds the DNS records for a specific domain. There are two distinct types:

### Public Hosted Zones

* **Purpose:** Answers DNS queries originating from the public internet.
* **Use Case:** You buy `mypublicdomain.com` and want anyone in the world to be able to resolve `api.mypublicdomain.com` to your public-facing web servers.
* **Pricing:** You pay $0.50 per month for the zone itself, plus you are billed for the DNS queries ($0.40 per million standard queries).

### Private Hosted Zones

* **Purpose:** Answers DNS queries originating *only* from within your own Virtual Private Cloud (VPC). It is invisible to the outside world.
* **Use Case:** You want your internal application servers to communicate securely. You create a private zone for `company.internal`. Your web server can securely resolve `database.company.internal` to a private IP like `10.0.0.10` without exposing the database to the internet.
* **Pricing:** You pay $0.50 per month for the zone itself, but **queries against Private Hosted Zones are completely free**.

---

## Interview Preparation: Route 53 Basics

### Summary

Interviewers will test your understanding of exactly *when* to use a Private Hosted Zone versus a Public one, and they will test your knowledge of CNAME limitations at the root domain.

### Q&A Details

**Q1: We have an internal microservice architecture running inside a VPC. Service A needs to communicate with Service B. Currently, the developers have hardcoded Service B's private IP address into Service A's code. How can we improve this architecture?**
**Answer:** Hardcoding IP addresses is an anti-pattern. You should create a **Private Hosted Zone** in Route 53 (e.g., `internal.myapp.com`) and create an A record pointing `service-b.internal.myapp.com` to Service B's private IP. Service A can then query the DNS name instead of the IP. If Service B's IP changes, you only update the Route 53 record, requiring zero code changes.

**Q2: A developer is trying to map the root domain `mycompany.com` to an existing external SaaS application hosted at `app.external-saas-provider.com`. They attempt to create a CNAME record in Route 53 for `mycompany.com` but receive an error. Why is this happening, and how do we resolve it?**
**Answer:** This fails because the DNS protocol strictly prohibits CNAME records at the root (or Zone Apex) of a domain. You cannot CNAME `mycompany.com`. To bypass this, the developer must either map a subdomain (like `[www.mycompany.com](https://www.mycompany.com)` or `app.mycompany.com`) using a CNAME, or check if the SaaS provider offers static IP addresses to create an A record instead. *(Note: If the target was an AWS resource like an ELB, we would use an AWS Alias record, but this does not work for external third-party domains).*

**Q3: We want to route traffic to an internal EC2 instance using a friendly name, but our finance department is highly sensitive to AWS costs. If we use a Private Hosted Zone, will we be charged for the millions of internal DNS queries our microservices generate every day?**
**Answer:** No. While AWS charges $0.50 per month for the Hosted Zone itself, DNS queries made against a Private Hosted Zone within a VPC are provided at no additional cost.