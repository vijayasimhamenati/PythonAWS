# CloudFormation Deep Dive: Outputs, Conditions, Intrinsic Functions & Rollbacks

This final section covers the advanced mechanics of CloudFormation. Understanding these concepts is critical for writing modular, production-ready templates and passing AWS certification exams.

---

## 1. Outputs (Cross-Stack Referencing)

You should rarely put your entire infrastructure into a single CloudFormation template. Best practice dictates separating your layers (e.g., a Network Stack and an Application Stack). But how does the Application Stack know where to deploy its EC2 instances if the VPC was built by the Network Stack?

**The Answer: Outputs.**

The `Outputs` section allows you to export a value from one stack so it can be imported by another.

* **Exporting:** In Stack A (Network), you use the `Export` block to expose a value globally within the AWS Region.
* **Importing:** In Stack B (Application), you use the Intrinsic Function `Fn::ImportValue` (or `!ImportValue`) to grab that exported value.

> **⚠️ The Dependency Rule:** If Stack B imports a value from Stack A, AWS creates a hard dependency link. You **cannot** delete Stack A until you first delete (or update) Stack B so that it no longer references the exported value.

---

## 2. Conditions

Conditions allow you to write logical `If/Then/Else` statements in your templates. They are most commonly used to alter the deployment based on the environment (e.g., Dev vs. Prod).

* **Definition:** You define conditions using logical operators like `Fn::Equals`, `Fn::Not`, `Fn::And`, and `Fn::Or`.
* **Application:** You apply the condition to a resource. If the condition evaluates to `True`, the resource is created. If `False`, CloudFormation ignores it.

*Example:* You can write a condition named `IsProduction` that checks if the `Environment` parameter equals `prod`. You can then attach that condition to a high-performance IOPS EBS volume. If deployed in Dev, the volume is skipped, saving money.

---

## 3. Intrinsic Functions (The Programming Logic)

Intrinsic functions are built-in tools that allow you to assign values to properties that are not available until runtime.

You must memorize the most common functions:

| Function | Shorthand | Purpose |
| --- | --- | --- |
| **`Fn::Ref`** | `!Ref` | Returns the value of a Parameter, or the Physical ID of a Resource. |
| **`Fn::GetAtt`** | `!GetAtt` | Returns a specific attribute of a resource (e.g., the public DNS name or Private IP of an EC2 instance). |
| **`Fn::FindInMap`** | `!FindInMap` | Looks up a value in the `Mappings` section (e.g., finding the correct AMI for the current region). |
| **`Fn::ImportValue`** | `!ImportValue` | Imports a value exported by another stack's `Outputs` section. |
| **`Fn::Base64`** | `!Base64` | Converts plain text into Base64 encoding. Almost exclusively used to pass scripts to EC2 `UserData`. |
| **`Fn::Sub`** | `!Sub` | Substitutes variables into a string at runtime (like Python f-strings). |

---

## 4. Rollbacks (Failure Handling)

When you deploy a CloudFormation template, AWS executes it as an **atomic operation**. It is an "All or Nothing" process.

### Creation Failures

If you attempt to create a stack with 10 resources, and the 9th resource fails (perhaps due to a typo in an AMI ID), CloudFormation automatically triggers a **Rollback**. It will methodically delete the 8 resources it just successfully built, returning your AWS account to the exact state it was in before you hit submit.

* **Troubleshooting:** If you want to stop CloudFormation from deleting the successfully provisioned resources so you can inspect them, you can choose the **Preserve successfully provisioned resources** option when launching the stack.

### Update Failures

If you update an existing, healthy stack, and the update fails mid-way, CloudFormation will automatically roll back the stack to its **last known stable state**.

---

## 5. Security: The IAM `PassRole` Mechanism

By default, when you launch a CloudFormation stack, the engine uses **your personal IAM credentials** to build the resources. If you are an Administrator, CloudFormation has Administrator access.

This is dangerous in a corporate environment. You do not want junior developers using their own credentials to deploy infrastructure.

**The Solution: Service Roles.**

1. An administrator creates an **IAM Role** specifically for CloudFormation, granting it only the permissions necessary to build the approved architecture (e.g., EC2 and S3 permissions).
2. The administrator gives the junior developer a specific IAM permission called `iam:PassRole`.
3. When the junior developer launches a stack, they use the AWS Console to "pass" the dedicated role to CloudFormation.
4. CloudFormation assumes the role and builds the infrastructure. The junior developer never had direct access to build the resources, ensuring the Principle of Least Privilege.