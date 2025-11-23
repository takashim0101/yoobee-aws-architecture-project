# Preparation Guide for Yoobee College AWS Architecture Implementation

This guide outlines the essential preparation steps required before you begin implementing the AWS architecture for Yoobee College. Completing these steps beforehand will ensure a smoother, simpler, and more secure implementation process.

---

## 1. AWS Account Setup and IAM User Configuration

It is highly recommended to perform all implementation tasks using an IAM user with specific permissions, rather than the AWS root account.

### 1.1. Confirm AWS Account Access

*   **Action:** Ensure you have an active AWS account.
*   **Details:** If you do not have one, you will need to create an AWS account. Be aware of the AWS Free Tier limits to manage costs.

### 1.2. Create a Dedicated IAM User (Recommended for Console Access)

*   **Action:** Create a new IAM user with AWS Management Console access.
*   **Steps:**
    1.  Log in to the AWS Management Console as the root user or an administrator IAM user.
    2.  Navigate to **IAM** -> **Users** -> **Add users**.
    3.  **User name:** Enter a descriptive name (e.g., `yoobee-admin-user`).
    4.  **AWS access type:** Select "AWS Management Console access".
    5.  **Console password:** Choose "Custom password" and set a strong password. Consider enabling "Require password reset at next sign-in".
    6.  **Permissions:**
        *   Select "Attach existing policies directly".
        *   For this project, you will need permissions to create/manage VPC, EC2, RDS, S3, ELB, IAM, CloudWatch resources. You can start with `AdministratorAccess` for simplicity during learning, but in a production environment, always apply the **Principle of Least Privilege**.
        *   **Recommended for learning:** Attach `AdministratorAccess` policy.
    7.  Review and create the user.

### 1.3. Enable Multi-Factor Authentication (MFA) for Your IAM User

*   **Action:** Enhance the security of your newly created IAM user by enabling MFA.
*   **Steps:**
    1.  Log in to the AWS Management Console using your new `yoobee-admin-user`.
    2.  Navigate to **IAM** -> **Users**.
    3.  Select your `yoobee-admin-user`.
    4.  Go to the "Security credentials" tab.
    5.  Under "Assigned MFA device", click "Manage".
    6.  Select "Virtual MFA device" and follow the instructions to set it up with an authenticator app (e.g., Google Authenticator, Authy) on your smartphone.

### 1.4. Enable MFA for the AWS Root Account (Critical Security Best Practice)

*   **Action:** If not already done, enable MFA for your AWS root account. This is the single most important security measure for your entire AWS account.
*   **Steps:**
    1.  Log in to the AWS Management Console as the **root user**.
    2.  Click on your account name in the top right corner and select "Security credentials".
    3.  Under "Multi-factor authentication (MFA)", click "Activate MFA".
    4.  Follow the instructions to set up a virtual MFA device.

---

## 2. IAM Role for EC2 Application and SSM Access

This IAM Role is crucial as it grants your EC2 instances the necessary permissions to be managed by Systems Manager and to interact with other AWS services securely.

### 2.1. Create/Verify `YoobeeEC2AppRole`

*   **Action:** Navigate to IAM -> Roles and create a new role for an AWS service -> EC2.
*   **Details:** Attach the following three AWS managed policies to this role.
    1.  **`AmazonSSMManagedInstanceCore`**: Crucial for enabling secure, browser-based administrative access (Session Manager) without SSH/RDP keys.
    2.  **`AmazonS3ReadOnlyAccess`**: Required for the application servers to retrieve course data from the S3 bucket.
    3.  **`CloudWatchAgentServerPolicy`**: Required for the application servers to send metrics and logs to CloudWatch.

---

## 3. Review Implementation Guides

Before starting the hands-on implementation, thoroughly review the provided guides.

### 3.1. Review Task 3 Implementation Guide

*   **Action:** Read through `C:\Portfolio\LINZ_Cloud_CV\A2_result\diagram_script\Task3_Implementation_Guide.md`.
*   **Details:** Understand the steps for setting up the core network infrastructure, launching EC2 instances, configuring S3, and setting up the ALB. Pay close attention to the "Key Implementation Checkpoints" and "Cleanup" sections.

### 3.2. Review Task 4 Implementation Guide

*   **Action:** Read through `C:\Portfolio\LINZ_Cloud_CV\A2_result\diagram_script\Task4_Implementation_Guide.md`.
*   **Details:** Understand the steps for applying security best practices, configuring CloudWatch monitoring, and the theoretical approach to cost optimization.

---

## 4. Local Tools (Optional but Recommended)

Consider having the following tools ready on your local machine:

*   **Text Editor:** A good text editor (e.g., VS Code, Sublime Text) for viewing and editing Markdown files.
*   **(Optional) AWS CLI:** If you plan to use command-line tools for interacting with AWS, install the AWS Command Line Interface.

---

## 5. Service-Specific Pre-configuration Planning

While the actual creation of services is part of the implementation steps, it is beneficial to understand their specific configurations beforehand.

### 5.1. Application Load Balancer (ALB) Planning

*   **Action:** Understand ALB configuration requirements.
*   **Details:**
    *   **Type:** Application Load Balancer (ALB) is chosen for Layer 7 routing.
    *   **Listeners:** What ports and protocols will the ALB listen on (e.g., HTTP 80, HTTPS 443)?
    *   **Target Groups:** How will target groups be configured (e.g., `lms-target-group`, `faculty-target-group`)? What are the health check paths and protocols for your applications?
    *   **Security Group:** Ensure you understand the `ALB-SG` rules (inbound from internet, outbound to EC2 instances).

### 5.2. EC2 Instance Planning

*   **Action:** Plan EC2 instance specifications.
*   **Details:**
    *   **AMI:** Which Amazon Machine Image (AMI) will you use for Linux (e.g., Amazon Linux 2) and Windows (e.g., Windows Server 2019 Base)?
    *   **Instance Type:** Confirm `t2.micro` (or `t3.micro` for better performance/Free Tier eligibility) for cost-effectiveness.
    *   **IAM Role:** Confirm `YoobeeEC2AppRole` is created and has the necessary permissions (`AmazonSSMManagedInstanceCore`, `AmazonS3ReadOnlyAccess`, `CloudWatchAgentServerPolicy`).
    *   **User Data (Optional):** Consider if any bootstrap scripts are needed for initial setup (e.g., installing web server).

### 5.3. RDS Database Planning

*   **Action:** Plan RDS database configuration.
*   **Details:**
    *   **Engine:** PostgreSQL.
    *   **Instance Class:** Confirm `db.t2.micro` (or `db.t3.micro` for better performance/Free Tier eligibility).
    *   **Multi-AZ:** Confirm Multi-AZ deployment for high availability.
    *   **Storage:** Initial storage size and auto-scaling settings.
    *   **Credentials:** Master username and password.
    *   **Security Group:** Understand `RDS-SG` rules (inbound from EC2 application servers).
    *   **Encryption:** Ensure encryption at rest is enabled.

### 5.4. S3 Bucket Planning

*   **Action:** Plan S3 bucket configuration.
*   **Details:**
    *   **Bucket Name:** Decide on a unique bucket name (e.g., `yoobee-course-data-<unique-suffix>`).
    *   **Region:** Confirm Sydney (ap-southeast-2).
    *   **Security:** Confirm Block Public Access settings.
    *   **Encryption:** Plan for default encryption (e.g., SSE-S3 or SSE-KMS).
    *   **Bucket Policy:** Understand the bucket policy to restrict access to `YoobeeEC2AppRole` and enforce HTTPS.

---

By completing these preparation steps, you will be well-equipped to proceed with the practical implementation of the Yoobee College AWS architecture.