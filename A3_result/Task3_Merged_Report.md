# Combined Task 3 Report and Implementation Guide

---

## Task 3 Report: Practical Implementation of Virtual Machines, Storage, and Load Balancing

# Report: Task 3 - Practical Implementation of Virtual Machines, Storage, and Load Balancing

## Executive Summary

This report documents the practical implementation of the core compute, storage, and load balancing components for the Yoobee College AWS architecture. Building upon the theoretical design and foundational network infrastructure established in Task 2, this phase involved the hands-on deployment of EC2 instances for LMS and Faculty applications, a Multi-AZ PostgreSQL RDS database, a secure S3 bucket for course data, and an Application Load Balancer (ALB) for traffic distribution. All implementations adhered to the principles of high availability, scalability, and security, utilizing AWS Systems Manager (SSM) for secure administrative access and ensuring resources were deployed consistently within the Sydney (ap-southeast-2) Region across designated Availability Zones.

## Key Implementation Checkpoints

Please pay close attention to the following points during implementation:

1.  **Security Group Cross-referencing:** When creating Security Groups (SGs), especially those that reference each other (e.g., `ALB-SG` referencing `LMS-SG`), it's best practice to first create all necessary SGs with just their names. Then, go back and edit each SG to add the inbound and outbound rules that refer to other SGs. This prevents errors due to non-existent SGs during initial rule creation.

2.  **Resource Region and AZ Consistency:** All resources (VPC, Subnets, NAT Gateway, EC2 instances, RDS, ALB) must be deployed within the **Sydney (ap-southeast-2) Region** and specifically within the designated Availability Zones (e.g., `ap-southeast-2a` for AZ A, `ap-southeast-2b` for AZ B) as defined in the subnet creation steps. Ensure strict adherence to this for high availability and correct network routing.

3.  **Cost Management for Cleanup:** The "Cleanup" section at the end of this guide is crucial. Resources like NAT Gateway and its associated Elastic IP incur charges even when not actively used. Always ensure all created resources are deleted in the correct reverse order after completing your work to avoid unexpected costs.

## 1. EC2 Instance Deployment (LMS and Faculty Applications)

This section details the successful launch of EC2 instances for the LMS and Faculty applications, configured for secure administrative access via AWS Systems Manager Session Manager.

### 1.1. Launch LMS Server (Linux)

*   **Action:** Launch two EC2 instances for the LMS application **in the Sydney (ap-southeast-2) Region**.
*   **Steps:**
    1.  Navigate to EC2 -> Instances -> Launch instances.
    2.  **Name:** `LMS-Server-A`, `LMS-Server-B`
    3.  **AMI:** Select the latest Amazon Linux 2 AMI.
    4.  **Instance type:** `t2.micro`.
    5.  **Key pair:** Select "Proceed without a key pair".
        > **Note:** We will use AWS Systems Manager Session Manager for secure shell access. This method is more secure than using SSH key pairs as it doesn't require opening SSH ports in security groups and provides IAM-based access control and logging.
    6.  **Network settings:**
        *   **VPC:** Select `Yoobee-VPC`.
        *   **Subnet:** For `LMS-Server-A`, select `Yoobee-Private-Subnet-A` (e.g., `ap-southeast-2a`). For `LMS-Server-B`, select `Yoobee-Private-Subnet-B` (e.g., `ap-southeast-2b`).
        *   **Auto-assign public IP:** Disable.
        *   **Security groups:** Select `LMS-SG`.
            > **Note:** Since Session Manager is used, there is no need to open SSH port 22 in this Security Group for administrative access.
    7.  **Configure storage:** Default settings are usually sufficient for `t2.micro`.
    8.  **Advanced details:**
        *   **IAM instance profile:** Select `YoobeeEC2AppRole`.
            > **Important:** Ensure that the `YoobeeEC2AppRole` has the `AmazonSSMManagedInstanceCore` policy attached to allow Session Manager connectivity.
    9.  Review and launch instances.

### 1.2. Launch Faculty Application Server (Windows)

*   **Action:** Launch two EC2 instances for the Faculty Application **in the Sydney (ap-southeast-2) Region**.
*   **Steps:**
    1.  Navigate to EC2 -> Instances -> Launch instances.
    2.  **Name:** `Faculty-App-Server-A`, `Faculty-App-Server-B`
    3.  **AMI:** Select the latest Windows Server AMI.
    4.  **Instance type:** `t2.micro`.
    5.  **Key pair:** Select "Proceed without a key pair".
        > **Note:** We will use AWS Systems Manager Session Manager for secure remote access (e.g., via PowerShell). This method is more secure than managing key pairs as it doesn't require opening management ports in security groups and provides IAM-based access control and logging.
    6.  **Network settings:**
        *   **VPC:** Select `Yoobee-VPC`.
        *   **Subnet:** For `Faculty-App-Server-A`, select `Yoobee-Private-Subnet-A` (e.g., `ap-southeast-2a`). For `Faculty-App-Server-B`, select `Yoobee-Private-Subnet-B` (e.g., `ap-southeast-2b`).
        *   **Auto-assign public IP:** Disable.
        *   **Security groups:** Select `Faculty-SG`.
            > **Note:** Since Session Manager is used, there is no need to open RDP port 3389 in this Security Group for administrative access.
    7.  **Configure storage:** Default settings are usually sufficient for `t2.micro`.
    8.  **Advanced details:**
        *   **IAM instance profile:** Select `YoobeeEC2AppRole`.
            > **Important:** Ensure that the `YoobeeEC2AppRole` has the `AmazonSSMManagedInstanceCore` policy attached to allow Session Manager connectivity.
    9.  Review and launch instances.

### 1.3. Connect to EC2 Instances via Session Manager

*   **Action:** Connect to your launched EC2 instances (`LMS-Server-A/B`, `Faculty-App-Server-A/B`) using AWS Systems Manager Session Manager.
*   **Steps:**
    1.  Navigate to EC2 -> Instances.
    2.  Select the desired EC2 instance (e.g., `LMS-Server-A`).
    3.  Click the "Connect" button at the top right.
    4.  Select the "Session Manager" tab.
    5.  Click "Connect".
    6.  A new browser tab will open, providing a command-line interface (for Linux instances) or PowerShell session (for Windows instances).
        > **Note:** No SSH Key Pair, Bastion Host, or open SSH/RDP ports are required for this connection method.

## 2. RDS Database Creation

This section details the successful creation of an Amazon RDS PostgreSQL database instance with Multi-AZ deployment.

### 2.1. Create RDS Database

*   **Action:** Create an Amazon RDS PostgreSQL database instance with Multi-AZ deployment.
*   **Steps:**
    1.  Navigate to RDS -> Databases -> Create database.
    2.  **Choose a database creation method:** Standard create.
    3.  **Engine options:** PostgreSQL.
    4.  **Version:** Select a compatible version.
    5.  **Templates:** Free tier (for cost management) or Production (for full features).
    6.  **DB instance identifier:** `yoobee-rds-instance`
    7.  **Master username:** `admin` (or your preferred username).
    8.  **Master password:** Set a strong password.
    9.  **DB instance class:** `db.t2.micro` (or `db.t3.micro` for better performance/Free Tier eligibility).
    10. **Multi-AZ deployment:** Select "Create a standby instance" (for high availability).
    11. **Storage:** Default settings are usually sufficient for `db.t2.micro`.
    12. **Connectivity:**
        *   **VPC:** Select `Yoobee-VPC`.
        *   **Subnet group:** Create a new DB subnet group, ensuring it includes `Yoobee-Private-Subnet-A` and `Yoobee-Private-Subnet-B`.
        *   **Public access:** No.
        *   **VPC security groups:** Select `RDS-SG`.
    13. **Database authentication:** Password authentication.
    14. **Additional configuration:**
        *   **Backup:** Enable automated backups.
        *   **Monitoring:** Enable Enhanced monitoring (optional, but recommended).
        *   **Encryption:** Ensure "Encryption" is enabled.
    15. Review and create database.

## 3. S3 Bucket and VPC Gateway Endpoint Configuration

This section details the creation of an S3 bucket and the application of a secure bucket policy, along with the creation of a VPC Gateway Endpoint for Amazon S3.

### 3.1. Create S3 VPC Gateway Endpoint

*   **Action:** Create a VPC Gateway Endpoint for Amazon S3 to allow private access to S3 from instances in private subnets without traversing the internet, enhancing both security and performance.
*   **Steps:**
    1.  Navigate to VPC -> Endpoints -> Create Endpoint.
    2.  **Service category:** AWS services.
    3.  **Service name:** Search for `com.amazonaws.ap-southeast-2.s3` (Gateway type).
    4.  **VPC:** Select `Yoobee-VPC`.
    5.  **Route tables:** Select both `Yoobee-Private-RT-A` and `Yoobee-Private-RT-B`. This will automatically add a route to S3 via the endpoint in these private route tables.
    6.  **Policy:** Choose "Full Access" for simplicity in this project, or create a custom policy for least privilege if needed.
    7.  Create endpoint.
*   **Verification:** After creation, check the route tables (`Yoobee-Private-RT-A` and `Yoobee-Private-RT-B`) to ensure a route for S3 (`pl-xxxxxxxx` prefix list) pointing to the newly created endpoint is present.

### 3.2. S3 Bucket Creation and Security Policy

*   **Action:** Create an S3 bucket for academic materials **in the Sydney (ap-southeast-2) Region**.
*   **Steps:**
    1.  Navigate to S3 -> Buckets -> Create bucket.
    2.  **Bucket name:** `yoobee-course-data-<unique-suffix>` (replace `<unique-suffix>` with a unique identifier).
    3.  **AWS Region:** Select `Asia Pacific (Sydney)` (ap-southeast-2).
    4.  **Object Ownership:** ACLs disabled (recommended).
    5.  **Block Public Access settings:** Keep all public access blocked (default).
    6.  **Default encryption:** Enable (e.g., SSE-S3).
    7.  Create bucket.

### 3.3. Apply S3 Bucket Policy

*   **Action:** Apply a bucket policy to restrict access to the `YoobeeEC2AppRole` and enforce HTTPS.
*   **Steps:**
    1.  Navigate to your newly created S3 bucket.
    2.  Go to "Permissions" tab -> "Bucket policy".
    3.  Paste the following policy, replacing `<your-aws-account-id>` and `<your-unique-suffix>`:
        ```json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "arn:aws:iam::<your-aws-account-id>:role/YoobeeEC2AppRole"
                    },
                    "Action": [
                        "s3:GetObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        "arn:aws:s3:::yoobee-course-data-<your-unique-suffix>",
                        "arn:aws:s3:::yoobee-course-data-<your-unique-suffix>/*"
                    ]
                },
                {
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:*",
                    "Resource": [
                        "arn:aws:s3:::yoobee-course-data-<your-unique-suffix>",
                        "arn:aws:s3:::yoobee-course-data-<your-unique-suffix>/*"
                    ],
                    "Condition": {
                        "Bool": {
                            "aws:SecureTransport": "false"
                        }
                    }
                }
            ]
        }
        ```
    4.  Save changes.

## 4. Elastic Load Balancer (ALB) Setup

This section details the configuration of an Application Load Balancer (ALB) to distribute traffic.

### 4.1. Create Target Groups

*   **Action:** Create target groups for the LMS and Faculty Application EC2 instances.
*   **Steps:**
    1.  Navigate to EC2 -> Load Balancers -> Target Groups -> Create target group.
    2.  **Target type:** Instances.
    3.  **Target group name:** `lms-target-group`
    4.  **Protocol:** HTTP, **Port:** 80 (or your application's port).
    5.  **VPC:** Select `Yoobee-VPC`.
    6.  **Health checks:** Configure appropriate health check path (e.g., `/index.html` or application-specific endpoint).
    7.  Register the two `LMS-Server` EC2 instances.
    8.  Repeat steps for `faculty-target-group`, registering the two `Faculty-App-Server` EC2 instances.

### 4.2. Create Application Load Balancer (ALB)

*   **Action:** Create an Internet-facing Application Load Balancer **in the Sydney (ap-southeast-2) Region**.
*   **Steps:**
    1.  Navigate to EC2 -> Load Balancers -> Create Load Balancer.
    2.  Select "Application Load Balancer" -> Create.
    3.  **Load balancer name:** `yoobee-alb`
    4.  **Scheme:** Internet-facing.
    5.  **IP address type:** IPv4.
    6.  **VPC:** Select `Yoobee-VPC`.
    7.  **Mappings:** Select `Yoobee-Public-Subnet-A` and `Yoobee-Public-Subnet-B`.
    8.  **Security groups:** Select `ALB-SG`.
    9.  **Listeners and routing:**
        *   **Protocol:** HTTP, **Port:** 80.
        *   **Default action:** Forward to `lms-target-group`.
    10. Review and create load balancer.

### 4.3. (Optional) Configure Path-Based Routing

*   **Action:** Add rules to the ALB listener to route traffic to different target groups based on URL paths.
*   **Steps:**
    1.  Navigate to your `yoobee-alb` -> Listeners tab.
    2.  Select the HTTP:80 listener -> View/edit rules.
    3.  Add a new rule:
        *   **IF:** Path is `/faculty/*`
        *   **THEN:** Forward to `faculty-target-group`.
    4.  Arrange rules as needed (more specific rules should be higher).

## Conclusion

The practical implementation of the core AWS components for Yoobee College's virtualization architecture has been successfully completed. This phase has established a robust and scalable foundation, including secure compute instances, a highly available database, secure object storage, and efficient traffic distribution. The adherence to best practices for security, high availability, and cost-effectiveness ensures that the deployed infrastructure is well-prepared to support the college's digital transformation goals. Further security enhancements, monitoring, and cost optimization strategies are detailed in the Task 4 Report.

## Cleanup (To Avoid Unexpected Costs)

It is crucial to delete all resources created during this implementation to avoid incurring unexpected AWS costs, especially for services like NAT Gateways and Elastic IPs which incur charges even when idle. Delete resources in the reverse order of creation to avoid dependency issues.

1.  **Delete EC2 Instances:**
    *   Terminate all `LMS-Server-A/B` and `Faculty-App-Server-A/B` EC2 instances.
2.  **Delete Application Load Balancer (ALB):**
    *   Delete `yoobee-alb`. This will also delete associated listeners and target groups.
3.  **Delete RDS Instance:**
    *   Delete `yoobee-rds-instance`. Ensure you skip final snapshot creation unless needed.
4.  **Delete S3 Bucket:**
    *   Empty the `yoobee-course-data-<unique-suffix>` S3 bucket first, then delete the bucket.
5.  **Delete NAT Gateway:**
    *   Delete **`Yoobee-NAT-GW-A`**. (Task 2 の設計に基づき、1つのみを削除します。)
6.  **Delete Internet Gateway (IGW):**
    *   Detach `Yoobee-IGW` from `Yoobee-VPC`, then delete it.
7.  **Delete Route Tables:**
    *   Delete `Yoobee-Public-RT`, `Yoobee-Private-RT-A`, `Yoobee-Private-RT-B`. (Ensure no subnets are associated with them first, though they should be unassociated when subnets are deleted).
8.  **Delete Subnets:**
    *   Delete all `Yoobee-Public-Subnet-A/B` and `Yoobee-Private-Subnet-A/B`.
9.  **Delete VPC:**
    *   Delete `Yoobee-VPC`. (Ensure all resources within it are deleted first).
10. **Delete IAM Roles/Policies (Optional):**
    *   If created specifically for this task, delete `YoobeeEC2AppRole`, `LMS-SG`, `Faculty-SG`, `ALB-SG`, `RDS-SG` and any custom IAM policies.

This completes the cleanup process.