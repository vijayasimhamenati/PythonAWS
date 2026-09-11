# Amazon S3 Security: Access Control Mechanisms

Securing data in Amazon S3 is one of the most heavily tested domains in AWS certifications. Because S3 is publicly routable over the internet, a single misconfiguration can lead to a devastating data breach.

AWS provides multiple layers of defense to control exactly who can read, write, or delete your objects.

---

## 1. The Core Security Mechanisms

There are three primary ways to control access to S3. They are evaluated together to determine if an action is allowed.

### A. User-Based Security (IAM Policies)

This is security attached to the *identity* making the request.

* **How it works:** You attach an IAM Policy to an IAM User, Group, or Role.
* **Example:** An EC2 instance has an IAM Role attached that explicitly allows `s3:GetObject` on a specific bucket. When the instance requests a file, AWS checks the role, sees the permission, and grants access.

### B. Resource-Based Security (S3 Bucket Policies)

This is security attached directly to the *bucket* itself.

* **How it works:** A Bucket Policy is a JSON document attached to the S3 bucket that defines rules for who can interact with it.
* **Common Use Cases:**
* Granting cross-account access (allowing a user in Account B to access a bucket in Account A).
* Making a bucket entirely public (e.g., for hosting a static website).
* Forcing specific security conditions (e.g., denying any uploads that aren't encrypted).



### C. Access Control Lists (ACLs) - Legacy

ACLs are an older, finer-grained security mechanism that can be applied at the object level or the bucket level.

* **Current Best Practice:** AWS strongly recommends **disabling** ACLs entirely and managing all permissions via IAM Policies and Bucket Policies. (We saw this in the previous lecture where "ACLs disabled" was the default setting during bucket creation).

---

## 2. Policy Evaluation Logic (The Rules of Access)

When a user tries to download an object from S3, AWS evaluates the IAM Policies and the Bucket Policies together. How does it decide what to do?

**The Golden Rules of Evaluation:**

1. **Default Deny:** By default, all requests are denied.
2. **Explicit Allow:** An explicit `Allow` in *either* an IAM Policy OR a Bucket Policy will grant access (assuming they are in the same account).
3. **Explicit Deny:** An explicit `Deny` in *any* policy always trumps an `Allow`. If a Bucket Policy allows access, but an IAM Policy denies it, the request is denied.

---

## 3. Dissecting a Bucket Policy

Bucket Policies are written in JSON. You must be able to read and understand basic JSON policy structures for the exam.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::example-bucket/*"
    }
  ]
}

```

* **Effect:** Is this rule going to `Allow` or `Deny` the action?
* **Principal:** Who is this rule for? `"*"` means "Anyone in the world" (anonymous internet users). If you wanted to restrict it, you would put a specific AWS Account ID or IAM User ARN here.
* **Action:** What API call is being controlled? `s3:GetObject` means downloading/reading a file.
* **Resource:** What AWS asset does this apply to? The `/*` at the end means "every object inside the bucket named example-bucket."

*Conclusion:* The policy above makes every file in the bucket publicly downloadable on the internet.

---

## 4. The Safety Net: Block Public Access

Because it is so easy to accidentally write a Bucket Policy with `Principal: "*"` and expose sensitive corporate data to the internet, AWS introduced the **Block Public Access (BPA)** settings.

BPA acts as a master override switch. If BPA is turned ON at the bucket level (or the account level), AWS will completely ignore any Bucket Policy or ACL that attempts to grant public access.

* **Exam Tip:** If an exam question states that a Bucket Policy is correctly configured to allow public read access, but internet users are getting an `AccessDenied` error, the answer is always that **Block Public Access** is enabled on the bucket.

---

## Interview Preparation: S3 Security

### Summary

Interviews test your ability to troubleshoot `AccessDenied` errors by understanding the interplay between IAM, Bucket Policies, and BPA.

### Q&A Details

**Q1: We have an S3 bucket used to host a static website. We attached a Bucket Policy granting `s3:GetObject` to `Principal: "*"`. However, when users browse to the website URL, they receive a 403 Forbidden error. We checked the policy JSON and there are no syntax errors. What is preventing the public from accessing the site?**
**Answer:** The bucket likely has the **Block Public Access (BPA)** settings enabled. BPA acts as an overarching security shield that overrides any Bucket Policy attempting to grant public access. To fix this and make the static website functional, you must go to the bucket's permissions tab and turn off the 'Block all public access' setting.

**Q2: A data science team in `Account A` needs to read datasets stored in an S3 bucket located in `Account B`. How can we architect this cross-account access securely without duplicating data?**
**Answer:** You must use a combination of IAM Policies and **S3 Bucket Policies**. The administrator of `Account B` must attach a Bucket Policy to the S3 bucket that explicitly grants `s3:GetObject` permissions, specifying the AWS Account ID or IAM Role ARN of the data science team in `Account A` as the `Principal`. Concurrently, the administrator of `Account A` must ensure the data scientists' IAM Role has an IAM Policy attached allowing them to perform the `s3:GetObject` action on the target bucket's ARN.

**Q3: We have an IAM User named 'Alice'. Alice's IAM Policy explicitly grants her full administrator access (`s3:*`) to a bucket named `finance-reports`. However, the Bucket Policy attached to `finance-reports` has a statement that explicitly `Denies` the `s3:DeleteObject` action for all users. Can Alice delete a report from the bucket?**
**Answer:** No. In AWS policy evaluation, an **Explicit Deny** always overrides an Explicit Allow. Even though Alice's IAM Policy grants her full access, the explicit deny in the Bucket Policy takes precedence, and her attempt to delete the object will result in an `AccessDenied` error.

---
# Practical Guide: Making an S3 Bucket Public (The Right Way)

In this hands-on lab, we will intentionally expose the `coffee.jpg` file we uploaded earlier to the public internet so that its standard Object URL works for anyone, without requiring a pre-signed URL.

> ⚠️ **SECURITY WARNING:** This process should *only* be used for buckets hosting public assets (like website images or CSS files). Never apply these steps to a bucket containing sensitive corporate or user data.

---

## 1. Disabling the "Block Public Access" Shield

As discussed in the security lecture, AWS places a protective shield over all new buckets by default. If we write a policy granting public access right now, AWS will completely ignore it because of this shield. We must lower the shield first.

1. Navigate to your S3 Bucket in the AWS Console.
2. Click on the **Permissions** tab.
3. Scroll down to the **Block public access (bucket settings)** section.
4. Click the **Edit** button.
5. **Uncheck** the box that says *Block all public access*.
6. Click **Save changes**.
7. AWS will force you to type the word `confirm` in a popup box. This friction is intentional to prevent accidental data exposure.

Your bucket is now *capable* of being public, but it is not public *yet*. The default state is still "Deny". We must now explicitly write a rule allowing access.

---

## 2. Writing the Public Bucket Policy

We need to attach a JSON policy to the bucket telling AWS to allow anonymous internet users to read the files.

While you can write the JSON manually, using the AWS Policy Generator ensures you don't make syntax errors.

### A. Get the Bucket ARN

1. Still on the **Permissions** tab, scroll down to the **Bucket policy** section.
2. Copy the **Bucket ARN** (it will look something like `arn:aws:s3:::stephane-demo-s3-v12`). Keep this on your clipboard.

### B. Generate the Policy JSON

1. Click the **Policy generator** button (this usually opens in a new tab).
2. **Select Type of Policy:** Choose `S3 Bucket Policy`.
3. **Effect:** `Allow` (We want to grant access).
4. **Principal:** Type `*` (This is the wildcard for "Anyone in the world").
5. **AWS Service:** `Amazon S3`
6. **Actions:** Scroll down the list and check `GetObject` (This is the specific API call that allows someone to download/view a file).
7. **Amazon Resource Name (ARN):** Paste your Bucket ARN here.
* **CRITICAL STEP:** You must append `/*` to the end of the ARN.
* *Example:* `arn:aws:s3:::stephane-demo-s3-v12/*`
* *Why?* The policy needs to apply to the *objects* inside the bucket, not the bucket itself. The `/*` means "every object inside this bucket."


8. Click **Add Statement**, then click **Generate Policy**.
9. Copy the resulting JSON block.

### C. Apply the Policy

1. Return to your S3 Bucket **Permissions** tab.
2. In the **Bucket policy** section, click **Edit**.
3. Paste the generated JSON into the text editor. (Ensure there are no extra spaces or blank lines at the very beginning of the text box, or AWS will throw a syntax error).
4. Click **Save changes**.

You will now see a red badge on your bucket overview that says **Publicly accessible**. AWS does this so you are always aware when a bucket is exposed to the internet.

---

## 3. Testing the Public URL

Let's prove the policy works.

1. Navigate back to the **Objects** tab in your bucket.
2. Click on the `coffee.jpg` file to view its properties.
3. Find the **Object URL** on the right side of the screen (e.g., `[https://stephane-demo-s3-v12.s3.eu-west-1.amazonaws.com/coffee.jpg](https://stephane-demo-s3-v12.s3.eu-west-1.amazonaws.com/coffee.jpg)`).
4. Click that URL or copy/paste it into a new, incognito browser tab.

**Success!** The image will load instantly. You did not need a complex Pre-Signed URL with IAM credentials; the standard web URL now works for anyone on the internet thanks to the Bucket Policy you created.