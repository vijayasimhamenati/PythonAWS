# Amazon S3: Data Replication

In enterprise environments, keeping a single copy of a file is rarely sufficient. You may need to copy data to another geographic region for disaster recovery, or copy production data into a lower-tier environment for testing.

Amazon S3 provides a native, asynchronous **Replication** engine to handle this automatically.

---

## 1. The Two Flavors of Replication

S3 Replication is categorized by *where* the destination bucket is located.

### CRR (Cross-Region Replication)

* **What it is:** Replicating data from a source bucket in one AWS Region (e.g., `us-east-1`) to a destination bucket in a *different* AWS Region (e.g., `eu-west-1`).
* **Use Cases:**
* **Disaster Recovery:** Ensuring your data survives even if an entire AWS Region goes offline.
* **Compliance:** Meeting legal mandates that dictate data must be stored across geographically separated areas.
* **Low Latency Access:** Replicating datasets closer to global end-users (e.g., copying US data to a European bucket so European users can download it faster).



### SRR (Same-Region Replication)

* **What it is:** Replicating data between two buckets located in the *same* AWS Region.
* **Use Cases:**
* **Log Aggregation:** Pulling security logs from 50 different application buckets into one centralized, heavily secured audit bucket in the same region.
* **Live Data Syncing:** Automatically copying data uploaded to a `Production` AWS account into a `Development` AWS account so testers have access to live datasets.



---

## 2. The Strict Rules of Replication

AWS enforces several strict prerequisites and behaviors for S3 Replication. These are heavily tested on certification exams:

1. **Versioning is Mandatory:** You **must** enable Bucket Versioning on both the source bucket *and* the destination bucket before you can configure replication.
2. **IAM Permissions:** The S3 service does not automatically have the right to read your source bucket or write to your destination bucket. You must create and attach an **IAM Role** granting the S3 service these explicit permissions.
3. **Asynchronous Only:** Replication happens in the background. While it is usually very fast (seconds), it is asynchronous. You cannot rely on it for synchronous, real-time consistency.
4. **No Chaining:** Replication is not transitive. If Bucket A replicates to Bucket B, and Bucket B has a rule to replicate to Bucket C, a file uploaded to Bucket A will *only* replicate to Bucket B. It will **not** chain down to Bucket C.

---

## 3. The "Existing Objects" Trap

When you configure an S3 Replication rule, it only applies to **new** objects uploaded *after* the rule was saved.

If you have a bucket with 50 TB of existing data, turning on a replication rule will **not** copy that existing 50 TB to the destination bucket.

* **The Fix (S3 Batch Replication):** If you need to backfill the destination bucket with the historical data, you must run an **S3 Batch Replication** job. This is a manual trigger that forces S3 to scan the bucket and copy the existing inventory.

---

## 4. Deleting Replicated Objects

How S3 handles deletes in a replicated environment is a frequent source of confusion.

* **Soft Deletes (Delete Markers):** If you perform a standard delete on an object in the source bucket (which places a Delete Marker on top, as learned in the previous module), S3 **will not** replicate that Delete Marker to the destination bucket by default. (You can explicitly enable Delete Marker replication in the rule settings if you want the destination to mirror the source's soft deletes).
* **Hard Deletes (Permanent Deletion):** If you specify a Version ID and permanently destroy an object in the source bucket, S3 will **never** replicate that permanent deletion to the destination bucket. This is an intentional security design to protect the destination bucket from malicious actors or catastrophic scripts wiping out your backup data.

---

## Interview Preparation: S3 Replication

### Summary

Interviews test your knowledge of replication constraints (mandatory versioning, lack of chaining, IAM requirements) and how it handles historical data and deletes.

### Q&A Details

**Q1: We enabled a Cross-Region Replication (CRR) rule from a bucket in `us-east-1` to a bucket in `ap-northeast-1`. We verified the IAM permissions are correct. However, the thousands of log files that were already sitting in the `us-east-1` bucket before we created the rule are not appearing in the destination bucket. Why?**
**Answer:** Standard S3 Replication rules only apply prospectively to new objects uploaded *after* the rule is enabled. To replicate the historical objects that existed prior to the rule creation, you must initiate an **S3 Batch Replication** job.

**Q2: We are using Same-Region Replication (SRR) to maintain a backup of our production media bucket. A junior developer ran a script that permanently deleted several critical video files by targeting their specific Version IDs. Is the backup bucket compromised?**
**Answer:** No, the backup bucket is safe. By design, Amazon S3 **never** replicates permanent delete operations (deletions that target a specific Version ID) to the destination bucket. This security feature ensures that malicious or accidental permanent deletions in the source bucket do not destroy your replicated backups.

**Q3: A company has three buckets. Bucket A replicates to Bucket B using SRR. Bucket B replicates to Bucket C using CRR. If a user uploads a new image directly into Bucket A, will that image eventually appear in Bucket C?**
**Answer:** No. Amazon S3 does not support **replication chaining**. The image will replicate from Bucket A to Bucket B, but the replication engine will not trigger the secondary rule to move the object from Bucket B to Bucket C.

---

# Practical Guide: Configuring Cross-Region Replication (CRR)

In this hands-on lab, we will configure Amazon S3 to automatically and asynchronously copy data from a bucket in Europe to a backup bucket in the United States.

---

## 1. Provisioning the Buckets & Versioning

Replication absolutely requires Bucket Versioning to be enabled on both the source and the destination.

1. **Create the Source Bucket:**
* Create a new bucket (e.g., `s3-demo-origin-bucket`) in your primary region (e.g., `eu-west-1` Ireland).
* Under Bucket Versioning, select **Enable**.


2. **Create the Destination Bucket:**
* Create a second bucket (e.g., `s3-demo-replica-bucket`) in your backup region (e.g., `us-east-1` N. Virginia).
* Under Bucket Versioning, select **Enable**.



*Note: If you upload a file to the Origin bucket right now, it will NOT replicate, because the rule is not set up yet.*

---

## 2. Configuring the Replication Rule

We must tell the Origin bucket where to send its data and give it the IAM permissions to do so.

1. Navigate to your **Origin Bucket** in the AWS Console.
2. Click on the **Management** tab.
3. Scroll down to **Replication rules** and click **Create replication rule**.
4. **Rule name:** `DemoReplicationRule`
5. **Status:** Enabled.
6. **Rule scope:** Select **Apply to all objects in the bucket**.
7. **Destination:**
* Select **Specify a bucket in this account**.
* Click Browse S3 and select your `s3-demo-replica-bucket`.
* *(Notice AWS automatically detects that the destination is in a different region, making this a Cross-Region Replication).*


8. **IAM Role:** Select **Create new role**. AWS will automatically generate an IAM role with the exact permissions needed to read from the origin and write to the replica.
9. Click **Save**.

### The "Existing Objects" Prompt

Immediately after saving, AWS will ask: *"Do you want to replicate existing objects?"*
As learned in the theory lecture, standard replication only applies to *new* uploads. To replicate historical data, you must choose **Yes**, which triggers an **S3 Batch Operations** job. For this lab, select **No, do not replicate existing objects** and click Submit.

---

## 3. Testing Replication & Version IDs

Let's verify the engine is working.

1. Go to your **Origin Bucket** and upload a new file (e.g., `coffee.jpg`).
2. Toggle **Show versions** and take note of the alphanumeric Version ID assigned to `coffee.jpg`.
3. Navigate to your **Replica Bucket** in the other region. Wait ~10 seconds and refresh.
4. You will see `coffee.jpg` appear!
5. Toggle **Show versions** in the Replica bucket. **Notice that the Version ID is exactly the same as the Origin bucket.** S3 guarantees a 1:1 version match across replicated buckets.

---

## 4. The Rules of Deletion (Exam Focus)

How do deletes replicate? It depends on your settings and *how* you delete the file.

### A. Delete Markers (Soft Deletes)

By default, if you delete a file in the Origin bucket (creating a Delete Marker), that marker does **not** replicate.

* To change this, edit your Replication Rule, scroll to the bottom, and enable **Delete marker replication**.
* Once enabled, if you soft-delete `coffee.jpg` in the Origin, S3 will copy that Delete Marker to the Replica, hiding the file in both regions.

### B. Permanent Deletes (Hard Deletes)

If you toggle "Show versions" in the Origin bucket, select a specific Version ID, and click **Permanently Delete**, the file is physically destroyed in the Origin bucket.

* **Will this replicate?** **NO.** S3 will *never* replicate a permanent deletion. The file remains safely stored in the Replica bucket. This is an intentional security design to ensure a malicious actor cannot wipe out your primary data and your backups simultaneously.

---

## 5. Boto3 Implementation

Here is the clean, simplified `boto3` script to programmatically configure Cross-Region Replication.

*Note: For replication to work via API, you must already have an IAM Role ARN created that grants S3 the permissions to replicate data.*

```python
import boto3

# Define variables
origin_region = 'eu-west-1'
replica_region = 'us-east-1'
origin_bucket = 's3-demo-origin-bucket-123'
replica_bucket = 's3-demo-replica-bucket-123'

# Provide an existing IAM Role ARN that has S3 Replication permissions
replication_role_arn = 'arn:aws:iam::123456789012:role/s3-replication-role'

# Initialize clients for both regions
s3_origin = boto3.client('s3', region_name=origin_region)
s3_replica = boto3.client('s3', region_name=replica_region)

print("1. Creating Source and Destination Buckets...")
s3_origin.create_bucket(
    Bucket=origin_bucket,
    CreateBucketConfiguration={'LocationConstraint': origin_region}
)
# us-east-1 does not require LocationConstraint
s3_replica.create_bucket(Bucket=replica_bucket) 

print("2. Enabling Versioning on both buckets (Mandatory)...")
for client, bucket in [(s3_origin, origin_bucket), (s3_replica, replica_bucket)]:
    client.put_bucket_versioning(
        Bucket=bucket,
        VersioningConfiguration={'Status': 'Enabled'}
    )

print("3. Applying Replication Rule to Origin Bucket...")
replication_config = {
    'Role': replication_role_arn,
    'Rules': [
        {
            'ID': 'DemoReplicationRule',
            'Status': 'Enabled',
            'Priority': 1,
            'DeleteMarkerReplication': {'Status': 'Enabled'}, # Optional: Replicate soft deletes
            'Filter': {'Prefix': ''}, # Replicate all objects
            'Destination': {
                'Bucket': f'arn:aws:s3:::{replica_bucket}'
            }
        }
    ]
}

s3_origin.put_bucket_replication(
    Bucket=origin_bucket,
    ReplicationConfiguration=replication_config
)

print("✅ Cross-Region Replication configured successfully!")

```

---

## Interview Preparation: S3 Replication Mechanics

### Summary

Be prepared to explain the differences between Batch vs. Live replication, and strictly articulate how S3 handles Delete Markers versus Permanent Deletions across regions.

### Q&A Details

**Q1: We set up Cross-Region Replication to backup our Ireland bucket to Tokyo. An administrator accidentally executed a script that permanently deleted 50 critical files in the Ireland bucket by explicitly specifying their Version IDs. Are the files in the Tokyo bucket destroyed as well?**
**Answer:** No. Amazon S3 intentionally does not replicate permanent delete operations (where a specific Version ID is deleted). This is a built-in safeguard to ensure that malicious actions, compromised scripts, or accidental permanent deletions in a primary bucket cannot cascade and destroy your disaster recovery backups.

**Q2: We need to enable S3 replication to sync a production bucket to a test bucket in the same region. However, the replication rule is failing to save in the AWS console. What is the most likely prerequisite we missed?**
**Answer:** You most likely forgot to enable **Bucket Versioning** on either the source bucket, the destination bucket, or both. S3 Replication strictly requires versioning to be active on both ends so it can reliably track state changes and assign matching Version IDs to the replicated objects.

**Q3: We have enabled 'Delete Marker Replication' in our rule. If a user deletes an object without specifying a version ID in the source bucket, what exactly happens in both buckets?**
**Answer:** Because a version ID was not specified, S3 performs a "soft delete" by placing a Delete Marker on top of the object stack in the source bucket, resulting in a 404 if accessed via the standard URL. Because 'Delete Marker Replication' is enabled, S3 will asynchronously copy that exact Delete Marker to the destination bucket. The object will subsequently appear "deleted" in both the source and the backup, though the underlying data remains intact in both locations.