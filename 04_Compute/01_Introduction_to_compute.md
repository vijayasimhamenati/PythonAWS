# AWS Compute: The Decision Framework (EC2 vs ECS vs Lambda)

## 1. What is "Compute" in the Cloud?

Fundamentally, "compute" is the brain of your application. It represents the resources required for a program to successfully run and solve a problem.

* **Physical World:** Compute refers to the actual CPU (Central Processing Unit), RAM (Memory), and GPU (Graphics Processing Unit).
* **Cloud World:** Compute is a generic term for the virtualized power you rent to execute software. For example, a heavy Machine Learning (ML) model requires a "compute-intensive" environment (lots of RAM and GPUs).

AWS offers three primary ways to run your code, ranging from maximum control (EC2) to zero maintenance (Lambda).

---

## 2. Amazon EC2 (Elastic Compute Cloud) - The Virtual Machine

EC2 provides resizable virtual machines (VMs) in the cloud. It is **Infrastructure as a Service (IaaS)**.

**Key Characteristics:**

* **Total Control:** You have "root" or administrator access. You control the Operating System (OS), the network configuration, and the persistent storage.
* **Complete Flexibility:** Supports literally any programming language, framework, or custom software you want to install.
* **High Operational Burden:** You are entirely responsible for OS security patching, defining Auto Scaling rules, and handling instance failures.

**Best Use Cases:**

* **Legacy Applications:** Apps that require specific OS tweaks or custom kernel modifications.
* **Predictable Workloads:** Steady traffic where you need consistent performance and persistent state.
* **Specialized Hardware:** When you need direct access to massive GPUs for 3D rendering or AI model training.

---

## 3. Amazon ECS & AWS Fargate - The Containers

Modern developers package their Python apps into Docker containers so they run identically on their laptop and in the cloud. Amazon ECS (Elastic Container Service) is the orchestrator that manages these containers.

**Key Characteristics:**

* **Consistent Environments:** If the container works on your machine, it will work on ECS.
* **Two Launch Types:**
* **EC2 Launch Type:** You manage the underlying EC2 servers that the containers run on.
* **Fargate Launch Type (Recommended):** Serverless containers! AWS manages the underlying hosts; you just specify how much CPU/RAM your container needs.



**Best Use Cases:**

* **Microservices Architectures:** Running dozens of interconnected Python/Flask/FastAPI applications.
* **Long-Running Processes:** Background tasks, workers, or persistent WebSockets that run for hours or days.

---

## 4. AWS Lambda - The Serverless Function

Lambda is the ultimate developer tool. It is **Functions as a Service (FaaS)**. You do not provision servers, you do not manage containers, and you do not patch operating systems. You just upload your Python code, and AWS executes it.

**Key Characteristics:**

* **Event-Driven:** Code runs only in response to triggers (e.g., an HTTP request via API Gateway, a file uploaded to S3, or a schedule).
* **Pay-per-Request:** You pay exactly for the milliseconds your code runs. If nobody visits your API, your compute bill is `$0.00`.
* **Automatic Scaling:** Scales from 0 to thousands of concurrent executions instantly.
* **Hard Limit:** A single Lambda function cannot run for longer than 15 minutes.

**Best Use Cases:**

* **Sporadic or Spiky Traffic:** APIs that might get 10 requests today and 10,000 tomorrow.
* **Event Processing:** Running an image resizing script instantly when a user uploads a profile picture.

---

## 5. The Compute Decision Matrix (Memorize This!)

When evaluating options for a new architecture (like an Online Store API), use this matrix:

| Factor | AWS Lambda | Amazon ECS (Fargate) | Amazon EC2 |
| --- | --- | --- | --- |
| **Traffic Pattern** | Sporadic, Spiky, Unpredictable | Steady, Predictable | Steady, Predictable |
| **Scaling** | Instantly automatic | Requires scaling policies | Requires Auto Scaling Groups |
| **Duration Limit** | Maximum 15 minutes | Unlimited | Unlimited |
| **State Management** | Stateless (Saves state externally) | Can be Stateful | Full state management |
| **Cold Starts** | Yes (100ms - 10s delay on new requests) | Minimal (Container is running) | None (Server is always on) |
| **Operational Effort** | Lowest (AWS handles everything) | Medium (You configure deployments) | Highest (You patch OS/Security) |

---

> 💡 **Practical Developer Tip (Python / Boto3)**
> As a Python developer, you will often use Lambda for "Glue" logic—connecting two services together. But did you know you can trigger a Lambda function directly from another Python script using `boto3`?
> Here is how you invoke a Lambda function synchronously (waiting for the result) from your backend code:

```python
import boto3
import json

# Create the Lambda client
lambda_client = boto3.client('lambda', region_name='us-east-1')

# The payload you want to send to the function
event_payload = {
    "user_id": "12345",
    "action": "process_order"
}

try:
    # Invoke the function
    response = lambda_client.invoke(
        FunctionName='ProcessOrderFunction',
        InvocationType='RequestResponse', # Synchronous
        Payload=json.dumps(event_payload)
    )
    
    # Read the response from the function
    result = json.loads(response['Payload'].read().decode('utf-8'))
    print(f"✅ Lambda executed successfully: {result}")

except Exception as e:
    print(f"❌ Error invoking Lambda: {e}")

```

---

## Interview Preparation: Compute Decision Framework

### Summary

For the SAA and DVA exams, nearly every architectural question boils down to picking the right compute service. Look for keywords in the prompt:

* **"Legacy / Custom OS"** ➡️ EC2
* **"Docker / Microservices / Long-running"** ➡️ ECS
* **"Unpredictable traffic / Under 15 mins / Event-driven"** ➡️ Lambda

### Q&A Details

**Q1: We are building a video rendering application. When a user uploads a video, a process must extract the audio, which typically takes 45 to 60 minutes to complete. We want to minimize server management. Which compute service should we use?**
**Answer:** We should use **Amazon ECS with AWS Fargate**. While AWS Lambda is great for minimizing server management, it has a strict 15-minute execution timeout, making it impossible to use for a 60-minute task. Fargate provides serverless container management without time limits, making it perfect for long-running batch processing.

**Q2: A startup is launching a new REST API. They expect traffic to be highly erratic—zero traffic at night, but massive, unpredictable spikes during the day. They have very little funding and want to keep costs as close to $0 as possible when the API is idle. What compute service fits best?**
**Answer:** **AWS Lambda** integrated with API Gateway. Lambda automatically scales from zero to thousands of concurrent executions to handle the unpredictable spikes. Most importantly, due to its pay-per-request model, the startup pays absolutely nothing for compute when the API is idle at night.

**Q3: We are migrating a legacy on-premises database to AWS. The vendor software explicitly requires a customized Linux kernel and specific OS-level firewall configurations to run. Which compute platform must we use?**
**Answer:** We must use **Amazon EC2**. Neither Lambda nor ECS/Fargate allows access to the underlying operating system or kernel-level modifications. Only EC2 provides the total root-level control required to customize the OS for this legacy application.