# Amazon S3: Infinite Scaling Storage

Amazon Simple Storage Service (S3) is one of the foundational building blocks of AWS. It provides infinitely scalable, highly durable object storage that powers a significant portion of the web today.

## 1. What is Amazon S3 Used For?

At its core, S3 is storage, which means its use cases are virtually limitless. Some of the most common applications include:

- **Backup & Disaster Recovery:** Safely storing database snapshots or moving data across AWS regions to protect against localized failures.
- **Archiving:** Utilizing storage tiers like S3 Glacier to store historical data (e.g., NASDAQ storing 7 years of financial records) for extremely low costs.
- **Data Lakes & Analytics:** Storing massive datasets for services like Cisco to perform big data analytics and gain business insights.
- **Hybrid Cloud Storage:** Extending on-premises data centers seamlessly into the cloud.
- **Hosting:** Serving static websites, software updates, or massive media libraries (images, videos).

---

## 2. Understanding S3 Buckets

In Amazon S3, you store files (Objects) inside directories called **Buckets**.

### Regionality

- Buckets are defined at the **Region level** (e.g., `eu-west-1` Ireland).
- Even though the AWS S3 Console provides a global interface displaying all buckets across all regions, the data itself physically resides in the specific region you selected during creation.

### Bucket Naming Constraints

Naming your bucket correctly is crucial, as DNS relies on these names.

- **Formatting Rules:** No uppercase letters, no underscores, cannot be formatted as an IP address, must start with a lowercase letter or number, and cannot start with `xn--` or end with `-s3alias`. Keep it simple: use only lowercase letters, numbers, and hyphens.
- **Global vs. Regional Namespace (New Feature!):**
- _The Old Way (Global Namespace):_ Bucket names had to be globally unique across all AWS accounts worldwide. If someone on the other side of the planet named their bucket `test`, you could not use that name.
- _The New Way (Account Regional Namespace):_ AWS now allows you to reuse simple bucket names (like `demo` or `test`) across your own regions. AWS achieves this by automatically appending an Account Regional suffix (containing your account number and region) under the hood to ensure the underlying identifier remains globally unique.

---

## 3. Understanding S3 Objects (Files)

Objects are the actual files you upload to S3 (e.g., images, text documents, videos).

### The Concept of a "Key"

Unlike a traditional computer hard drive, S3 does not actually have physical directories or folders. It has a flat structure. Everything is defined by an **Object Key**, which represents the _entire path_ of the file.

If you upload a file to what looks like a folder in the console, the Key works like this:

- **Full Key:** `images/summer/beach.jpg`
- **Prefix:** `images/summer/` (This acts as the "folder" structure)
- **Object Name:** `beach.jpg`

_Note: The AWS Console UI fakes the folder experience to make it user-friendly, but internally, S3 simply maps the data to that long string Key._

### Object Characteristics

- **Size Limits:** The maximum size of a single object is **50 TB**.
- **Multi-Part Upload:** If you are uploading a file larger than 5 GB, you _must_ use the Multi-Part Upload API to break the file into smaller chunks (e.g., a 5 TB file requires at least 1,000 parts of 5 GB each).
- **Metadata & Tags:** Objects can store metadata (system or user-defined key-value pairs) and up to 10 Tags (Unicode key-value pairs) which are incredibly useful for tracking billing and configuring lifecycle security rules.
- **Versioning:** If enabled on the bucket, S3 assigns a unique Version ID to objects, allowing you to keep multiple variants of an object in the same bucket.

---

## 4. Hands-On: Creating a Bucket and Uploading Objects

Let's walk through a standard S3 deployment.

### Step 1: Create the Bucket

1. Navigate to the **S3 Console** and click **Create bucket**.
2. **Region:** Select your desired region.
3. **Bucket Type:** Select **General purpose** (Directory buckets are for highly specialized, ultra-low latency workloads).
4. **Namespace & Naming:** Either use the new Account Regional namespace to use a simple name, or use the Global namespace and provide a highly unique name (e.g., `stephane-demo-s3-v12`).
5. **Security & Defaults:**

- Leave **ACLs disabled** (Recommended).
- Leave **Block all public access** checked to ensure maximum security.
- Keep Bucket Versioning disabled for now.
- Leave **Default Encryption** enabled (Server-side encryption with Amazon S3 managed keys).

6. Click **Create bucket**.

### Step 2: Upload an Object

1. Click into your newly created bucket.
2. Click **Upload** > **Add files** and select a file from your computer (e.g., `coffee.jpg`).
3. Notice the destination is `s3://[your-bucket-name]`.
4. Click **Upload**.

### Step 3: Accessing the Object (Public vs. Pre-Signed URLs)

Once uploaded, click on the object (`coffee.jpg`) to view its properties. You will see an **Object URL** (the public link) and an **Open** button in the console.

- **The Pre-Signed URL (Success):** If you click the **Open** button, a new browser tab opens and displays the image. Look at the URL in the address bar—it is extremely long and complex. This is an **S3 Pre-Signed URL**. AWS temporarily encoded your current, authenticated AWS credentials directly into the URL, proving you have the right to view it.
- **The Public URL (Failure):** If you copy the standard **Object URL** and paste it into an incognito window, you will receive an `AccessDenied` XML error. Because we checked "Block all public access" during bucket creation, S3 correctly blocks unauthenticated requests from the public internet.
