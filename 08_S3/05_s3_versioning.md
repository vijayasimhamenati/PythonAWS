# Amazon S3: Bucket Versioning

In a standard S3 bucket, if you upload a file named `report.pdf` and then upload a new file also named `report.pdf`, the original file is overwritten and permanently destroyed.

To protect your data from accidental overwrites, malicious modifications, or unintended deletions, AWS highly recommends enabling **Bucket Versioning**.

---

## 1. How Versioning Works

Versioning is a bucket-level setting. Once enabled, S3 begins assigning a unique, alphanumeric **Version ID** to every new object you upload.

* **Overwriting:** If you upload a file with an existing key (e.g., `index.html`), S3 does not overwrite the data. Instead, it saves the new file alongside the old file, assigning the new file a new Version ID.
* **The "Current" Version:** When a user requests a file (e.g., viewing `index.html` on your static website), S3 automatically serves the file with the most recent Version ID.
* **The "Null" Version:** Any files that existed in the bucket *before* versioning was enabled are assigned a Version ID of `null`.
* **Suspension:** You cannot completely turn off versioning once it is enabled; you can only "suspend" it. Suspending versioning prevents new versions from being created but retains all existing versions.

---

## 2. The Delete Marker Illusion

Understanding how S3 deletes versioned objects is critical for the exam.

When you select a file in the AWS Console and click "Delete," **S3 does not actually delete the file.**

Instead, S3 creates a special, zero-byte object called a **Delete Marker** and assigns it a new Version ID. S3 then places this Delete Marker on top of the file stack, making it the "Current" version.

* If a user tries to access the file via its standard URL, S3 sees the Delete Marker on top and returns a **404 Not Found** error. The file *appears* deleted.
* However, the original data is still safely stored beneath the Delete Marker.

### How to Actually Delete or Restore a File

To restore a "deleted" file, you simply toggle the **"Show versions"** switch in the AWS Console, locate the Delete Marker, and permanently delete it. The previous version of the file will automatically pop back up to the top of the stack and become active again.

To permanently destroy data, you must toggle **"Show versions"**, select the specific underlying Version ID containing the data, and explicitly delete it. (This action cannot be undone).

---

## 3. Practical Guide: Enabling & Testing Versioning

Let's test this mechanism on our static website.

### A. Enable Versioning

1. Navigate to your S3 bucket.
2. Click the **Properties** tab.
3. In the **Bucket Versioning** section, click **Edit**.
4. Select **Enable** and click **Save changes**.

### B. Upload a New Version

1. On your local machine, open your `index.html` file and change the text from "I love coffee" to "I REALLY love coffee." Save the file.
2. In the AWS Console, go to the **Objects** tab.
3. Click **Upload**, select your modified `index.html`, and upload it.
4. Refresh your static website endpoint. You will see the updated text.

### C. Observe the Versions

1. In the AWS Console, toggle the **Show versions** switch located near the search bar.
2. Expand the `index.html` row. You will see two files:
* The new file (Current version) with a long alphanumeric Version ID.
* The original file (Previous version) with a `null` Version ID (because it was uploaded before versioning was enabled).



### D. The Rollback (Soft Delete)

Let's pretend the new update broke our website and we need to roll back immediately.

1. Turn **off** the "Show versions" toggle.
2. Select `index.html` and click **Delete**.
3. Type `delete` in the confirmation box and click **Delete objects**.
4. Refresh your static website endpoint. You will get a **404 Not Found** error. The file is gone.
5. Turn **on** the "Show versions" toggle.
6. You will see a **Delete marker** sitting on top of the file stack.
7. Select **only** the Delete marker, click **Delete**, type `permanently delete`, and confirm.
8. Refresh your static website endpoint. The website is back, serving the previous version of the file!

---

## Interview Preparation: S3 Versioning

### Summary

Interviews test your understanding of how versioning protects against data loss and how Delete Markers function to simulate deletion while preserving data integrity.

### Q&A Details

**Q1: An administrator accidentally deleted a critical configuration file from an S3 bucket that has versioning enabled. When an application attempts to fetch the file, it receives a 404 Not Found error. How can the administrator quickly restore the file to its previous state?**
**Answer:** Because versioning is enabled, the S3 "delete" action simply placed a Delete Marker on top of the file stack. The administrator should navigate to the S3 console, enable the 'Show versions' toggle to expose the object stack, and permanently delete the specific Delete Marker. This action will uncover the underlying version of the configuration file, instantly restoring access.

**Q2: We enabled versioning on our S3 bucket last week. We noticed that some of our older files have a version ID of `null`. Does this mean these files are corrupted and need to be re-uploaded?**
**Answer:** No, the files are not corrupted. In Amazon S3, any object uploaded to a bucket *before* versioning is enabled is assigned a version ID of `null`. If you overwrite those files in the future, S3 will keep the `null` version as the historical record and assign a standard alphanumeric version ID to the newly uploaded object.

**Q3: Our security compliance team requires that certain sensitive documents in S3 be completely and permanently destroyed after 7 years. The bucket has versioning enabled. If a script issues a standard `s3:DeleteObject` API call against the file, is the compliance requirement met?**
**Answer:** No. A standard `s3:DeleteObject` call in a versioned bucket only creates a Delete Marker; the underlying sensitive data remains stored and recoverable. To satisfy the compliance requirement and permanently destroy the data, the script must issue an `s3:DeleteObject` call that explicitly specifies the exact **Version ID** of the data payload.