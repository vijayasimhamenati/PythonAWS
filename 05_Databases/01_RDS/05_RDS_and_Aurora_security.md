# AWS RDS & Aurora: Security Summary

This lecture covers the fundamental security features available for Amazon RDS and Amazon Aurora, ensuring data protection, access control, and network security.

## 1. Data Encryption

### Encryption At-Rest (Storage)

At-rest encryption protects the underlying data stored on your database volumes.

* **AWS KMS Integration:** Master databases and all read replicas are encrypted using keys managed by the AWS Key Management Service (KMS).
* **Launch-Time Requirement:** Encryption must be enabled during the *initial launch* of the database.
* **The Read Replica Rule:** If the main (master) database is unencrypted, you **cannot** encrypt its read replicas.
* **Migrating Unencrypted to Encrypted:** You cannot simply toggle encryption "on" for an existing unencrypted database. You must:
1. Take a snapshot of the unencrypted database.
2. Restore that snapshot as a *new*, encrypted database.



### Encryption In-Flight (Network)

In-flight encryption secures data as it travels between your application clients and the database.

* **Enabled by Default:** Every RDS and Aurora database is ready to handle in-flight encryption out of the box.
* **SSL/TLS Certificates:** To use this, your clients must download and use the official TLS root certificates provided by AWS.

---

## 2. Authentication & Access Control

### Database Authentication

How users and applications prove who they are when connecting to the database:

* **Traditional:** Classic username and password combinations.
* **IAM Database Authentication:** Because RDS is tightly integrated with AWS, you can use IAM roles to connect.
* *Example:* An EC2 instance can use its attached IAM Role to authenticate to the database securely, completely eliminating the need to hardcode usernames and passwords in your application.



### Network Access Control

How you control which traffic is physically allowed to reach the database:

* **Security Groups:** Use AWS Security Groups to allow or block traffic based on specific IP ranges, ports, or even other Security Groups.

---

## 3. Server Access & Auditing

* **No SSH Access:** Because RDS and Aurora are fully managed services, AWS controls the underlying operating system. You cannot SSH into the servers.
* *Exception:* **Amazon RDS Custom** allows OS and database customization for specific legacy requirements.


* **Audit Logs:** To track what queries are being executed over time and monitor database activity, you can enable Audit Logs.
* **Retention:** Because logs consume storage and are eventually rotated out, you must configure RDS to send them to **Amazon CloudWatch Logs** for long-term retention and analysis.



---

> 💡 **Exam & Interview Tip:**
> If a scenario asks how to grant an EC2 instance access to an RDS database without storing passwords in the application code, the answer is always **IAM Database Authentication**. If a question asks how to encrypt an existing unencrypted database, remember the **Snapshot ➡️ Restore** workflow!