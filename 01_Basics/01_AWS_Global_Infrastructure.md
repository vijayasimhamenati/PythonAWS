## 1. AWS Regions

A **Region** is a physical geographical location in the world where AWS clusters its data centers (e.g., `us-east-1` in N. Virginia, `ap-south-1` in Mumbai). Each Region operates completely independently of the others.

When you deploy an application, you must choose a Region. How do you decide?

- **Compliance / Data Sovereignty:** Laws might require user data to stay within a specific country's borders.
- **Proximity to Customers (Latency):** Choose a Region closest to your primary user base so your app responds faster.
- **Available Services:** New AWS services (especially cutting-edge GenAI features) often launch in US regions first before rolling out globally.
- **Pricing:** The cost of compute and storage varies slightly from Region to Region due to local taxes, power, and real estate costs.

## 2. Availability Zones (AZs)

Inside every Region are multiple **Availability Zones** (usually a minimum of 3). An AZ consists of _one or more discrete data centers_, each with redundant power, networking, and connectivity.

AZs in a Region are geographically separated by a meaningful distance (usually miles) to protect against local disasters like floods, fires, or power grid failures, but close enough to have ultra-low latency connections between them.

- **The Golden Rule:** Always deploy your applications across at least two Availability Zones. If one AZ goes down, your application keeps running in the other. This is called **High Availability (HA)**.

## 3. Edge Locations (Points of Presence)

AWS has hundreds of **Edge Locations** scattered globally. These are _not_ used to run your main application servers. Instead, they are smaller data centers used primarily to **cache** data closer to the end user.

- If your app is hosted in a Region in London, but a user in Australia requests an image, the request doesn't have to travel to London. It is served instantly from a local Edge Location in Sydney.
- **AWS Services:** Amazon CloudFront (Content Delivery Network / CDN) and Amazon Route 53 (DNS) heavily utilize Edge Locations.

---

## Interview Preparation: AWS Global Infrastructure

## Summary

Interviewers test this topic to ensure you know how to design highly available, fault-tolerant architectures. You must understand the distinction between Regions (for compliance/latency) and AZs (for disaster recovery/high availability), and know when to leverage Edge Locations (for caching/CDN).

## Q&A Details

**Q1: We are launching a new application that must comply with strict European data privacy laws. However, our development team is based in the US. Where should we deploy our infrastructure?**

- **Answer:** We must deploy the infrastructure in a European AWS Region (such as `eu-central-1` in Frankfurt). The physical location of the development team doesn't dictate infrastructure placement; data sovereignty and compliance laws require the data to reside physically within European borders.

**Q2: How do you design an application to survive a catastrophic failure, such as a localized power grid failure taking out an entire data center?**

- **Answer:** By deploying the application across multiple Availability Zones (Multi-AZ). Because each AZ consists of distinct, physically separated data centers with isolated power and networking, a localized disaster will only affect one AZ. Our load balancers would simply route traffic to the healthy instances running in the other AZs.

**Q3: We have an application hosted in the `us-east-1` Region, but our users in Japan are complaining about slow load times for static assets like images and videos. How do we fix this without migrating the whole application?**

- **Answer:** We should implement Amazon CloudFront. CloudFront uses AWS Edge Locations to cache static content globally. The first time a Japanese user requests an image, it is fetched from `us-east-1` and cached in a Tokyo Edge Location. Subsequent requests by users in Japan are served locally from Tokyo, drastically reducing latency.
