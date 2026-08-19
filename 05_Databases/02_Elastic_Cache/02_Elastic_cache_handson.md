# Practical Guide: Creating and Deleting an Amazon ElastiCache Cluster

In this hands-on guide, we will walk through the process of provisioning a node-based Amazon ElastiCache cluster using Redis, exploring its configuration options, and securely deleting it to avoid unexpected charges.

## 1. Initial Setup and Deployment Options

1. Navigate to the **Amazon ElastiCache Console**.
2. **Engine Selection:** AWS recommends **Valkey** (a Redis-compatible replacement), but you can also choose **Redis OSS** or **Memcached**. For this walkthrough, we will use Redis.
3. **Deployment Option:** Select **Design your own cluster** (Node-based cluster) rather than the Serverless option to gain full visibility into the configuration settings.
4. **Creation Method:** Choose **Configure and create a new cluster** to manually review all available options instead of using a pre-configured template (like Production or Dev/Test).

---

## 2. Cluster Settings and Compute

* **Cluster Mode:** Set to **Disabled**. This provisions a single shard with one primary node and up to five read replicas. (Enabling Cluster Mode allows you to partition your data across multiple shards).
* **Name:** Give your cluster a name (e.g., `DemoCluster`).
* **Location:** Select **AWS Cloud**. (You also have the option to run it on-premises using AWS Outposts).
* **Multi-AZ:** Leave **Disabled** to save costs for this demo. (In production, this is crucial for high availability and failover).
* **Auto-Failover:** Keep as **Enabled**.
* **Node Type:** Select a Free Tier eligible instance, such as `cache.t2.micro` or `cache.t3.micro`.
* **Number of Replicas:** Set to **0** to minimize costs. (If Multi-AZ were enabled, you would need at least one replica).

---

## 3. Networking and Security

* **Subnet Group:** Create a new subnet group (e.g., `my-first-subnet-group`) and select your default VPC. This dictates which subnets your cache nodes can reside in.
* **AZ Placements:** Since we are not running in Multi-AZ mode, you can leave the placement settings as default.
* **Encryption at Rest:** You can enable this to encrypt data on the disk (requires an AWS KMS key). We will leave it disabled for the demo.
* **Encryption in Transit:** If enabled, data is encrypted between the client and the server. Enabling this also unlocks **Access Control** features:
* **Redis AUTH:** Require a password/token to connect.
* **User Group Access Control List (ACL):** Manage fine-grained permissions.
* *Note:* Disable encryption in transit for this basic demo.


* **Security Groups:** Assign a VPC Security Group that allows inbound traffic on the Redis port (default `6379`) from your application servers.
* **Backups, Maintenance, and Logs:** You can define backup windows, schedule minor version upgrades, and export slow logs or engine logs to Amazon CloudWatch. Keep the defaults and click **Create**.

---

## 4. Connecting to the Cache

Once the cluster status changes to **Available**, click on it to view the **Primary Endpoint** (for writes/reads) and **Reader Endpoint** (if replicas were configured).

Unlike a relational database, you cannot easily connect to ElastiCache using a standard desktop GUI client over the public internet. ElastiCache is strictly designed to be accessed from within your VPC (e.g., from an EC2 instance or Lambda function). You must write application code to interact with it.

> 💡 **Practical Developer Tip (Python / Redis)**
> To connect to your new Redis cluster from an EC2 instance within the same VPC, you would use a Redis client library like `redis-py` in Python:

```python
import redis

# Replace with your actual ElastiCache Primary Endpoint
redis_endpoint = 'democluster.xxxxxx.0001.use1.cache.amazonaws.com'
redis_port = 6379

try:
    # Establish the connection
    cache = redis.Redis(host=redis_endpoint, port=redis_port, decode_responses=True)
    
    # Test the connection (Cache Miss to Cache Hit)
    cache.set('welcome_message', 'Hello from Amazon ElastiCache!')
    cached_value = cache.get('welcome_message')
    
    print(f"✅ Successfully connected! Cached Value: {cached_value}")

except Exception as e:
    print(f"❌ Failed to connect to ElastiCache: {e}")

```

---

## 5. Cleaning Up (Deleting the Cluster)

To ensure you do not incur ongoing hourly charges, delete the cluster when you are finished.

1. Go back to the **ElastiCache Console**.
2. Select your Redis cluster (`DemoCluster`).
3. Click the **Actions** dropdown and select **Delete**.
4. When prompted to create a final backup, select **No**.
5. Type the name of the cluster to confirm the deletion and click **Delete**.