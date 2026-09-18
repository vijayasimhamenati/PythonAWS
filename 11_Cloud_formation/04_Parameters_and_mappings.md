# CloudFormation Template Inputs: Parameters vs. Mappings

To make your CloudFormation templates reusable across different environments, accounts, and regions, you must decouple the hardcoded configuration values from the resource definitions. AWS provides two primary mechanisms to achieve this: **Parameters** and **Mappings**.

Understanding when to use which is a frequent topic on the AWS Solutions Architect exams.

---

## 1. Parameters (Dynamic User Input)

Parameters allow the user (or the CI/CD pipeline) to pass dynamic inputs into the template exactly at the moment the stack is launched or updated.

**When to use Parameters:**

* When the value cannot be known ahead of time (e.g., passing in a specific database password, or an SSH KeyPair name that exists in the user's account).
* When you want to give the user a choice from a predefined list (e.g., choosing `t2.micro` for Dev or `m5.large` for Prod).

### Advanced Parameter Constraints

Parameters are not just dumb string inputs; CloudFormation allows you to enforce strict validation rules to prevent deployment errors.

* `AllowedValues`: Restricts the user to a specific dropdown list.
* `AllowedPattern`: Uses Regex to enforce formatting (e.g., ensuring an input matches a valid IPv4 CIDR block format).
* `NoEcho`: A critical security feature. Setting `NoEcho: true` ensures that the input value (like a database password) is masked with asterisks in the AWS Console and is never printed in plain text in the CloudFormation deployment logs.

---

## 2. Mappings (Static Lookup Tables)

Mappings are static lookup tables hardcoded directly into the template. They are not inputted by the user at runtime. Instead, they are evaluated by the CloudFormation engine during deployment based on internal logic.

**When to use Mappings:**

* When the values are known in advance and are tightly coupled to a specific environment variable, most commonly the **AWS Region**.

### The Classic Use Case: Regional AMI Mapping

An Amazon Machine Image (AMI) ID for Amazon Linux 2023 is different in every single AWS Region. If you hardcode `ami-0c55b159cbfafe1f0` into your template, the template will only work in `us-east-1`. If you try to deploy that exact template in `eu-west-1`, it will fail because that AMI ID does not exist there.

Instead of forcing the user to look up the correct AMI ID and pass it in as a Parameter, you use a Mapping block combined with a **Pseudo Parameter** to make the template instantly deployable globally.

---

## 3. Pseudo Parameters (The System Variables)

Pseudo Parameters are special variables provided by AWS that are always available inside every CloudFormation template. You do not define them; you simply reference them.

They allow your template to dynamically understand the context of where it is being deployed.

**Common Pseudo Parameters:**

* `AWS::Region`: Returns the region the stack is deploying in (e.g., `us-east-1`).
* `AWS::AccountId`: Returns the 12-digit AWS account ID of the user deploying the stack.
* `AWS::StackName`: Returns the name the user gave the stack during launch.

---

## 4. Bringing It Together (The `!Ref` and `!FindInMap` Functions)

Here is how you use these three concepts together in a production-grade template to achieve regional independence.

```yaml
Parameters:
  # 1. A dynamic user input constrained by AllowedValues
  EnvironmentType:
    Type: String
    AllowedValues:
      - dev
      - prod
    Default: dev

Mappings:
  # 2. A static lookup table hardcoded into the template
  RegionMap:
    us-east-1:
      AMI: ami-0c55b159cbfafe1f0
    eu-west-1:
      AMI: ami-01dd271720c1ba44f
    ap-south-1:
      AMI: ami-0a23ccb2cdd9286bb

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      # 3. Using !FindInMap with the AWS::Region Pseudo Parameter
      ImageId: !FindInMap [RegionMap, !Ref "AWS::Region", AMI]
      # 4. Using Conditionals based on the Parameter (Conceptual)
      InstanceType: !If [IsProduction, m5.large, t2.micro] 

```

### How the Logic Flows:

1. The user uploads the template in `eu-west-1`.
2. The CloudFormation engine evaluates the `AWS::Region` Pseudo Parameter as `eu-west-1`.
3. The engine uses the Intrinsic Function `!FindInMap` to look at the `RegionMap` block, find the `eu-west-1` row, and extract the `AMI` value.
4. The EC2 instance is successfully provisioned using `ami-01dd271720c1ba44f`, without the user having to input anything!