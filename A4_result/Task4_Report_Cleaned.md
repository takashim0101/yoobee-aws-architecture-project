# Combined Task 4 Report and Implementation Guide

---
This report details the theoretical evaluation and practical implementation of optimization and security measures for Yoobee College's AWS cloud infrastructure. Building upon the foundational architecture, this document outlines the application of AWS security best practices, the configuration of CloudWatch for robust monitoring and alerting, and a comprehensive strategy for cost optimization. The aim is to ensure a scalable, secure, and cost-effective cloud environment that supports the college's digital transformation goals.

## 1. Security Enhancements Implementation

### 1.1. Infrastructure and Network Security

#### 1.1.1. VPC for Network Isolation
*   **Action:** Ensure all resources are deployed within the `Yoobee-VPC`.
*   **Details:** (Refer to Task 2/3 implementation for VPC creation and subnet setup.)

#### 1.1.2. Use of Private Subnets
*   **Action:** Verify that application servers (LMS, Faculty) and the RDS database are launched into private subnets.
*   **Details:** (Refer to Task 2/3 implementation for instance placement.)

#### 1.1.3. Principle of Least Privilege for Network Traffic (Security Groups)
*   **Action:** Configure Security Groups for ALB, EC2 instances (LMS, Faculty), and RDS with the principle of least privilege.
*   **Steps:**
    1.  **ALB Security Group (`ALB-SG`):**
        *   Inbound: Allow HTTP (Port 80) and HTTPS (Port 443) from `0.0.0.0/0`.
        *   Outbound: Allow traffic to `LMS-SG` and `Faculty-SG` on application ports (e.g., 80/443 or custom app port).
    2.  **EC2 Application Servers Security Groups (`LMS-SG`, `Faculty-SG`):**
        *   Inbound: Allow traffic from `ALB-SG` on application ports (e.g., 80/443 or custom app port).
        *   Outbound: Allow traffic to `RDS-SG` on database port (5432 for PostgreSQL).
        *   Outbound: Allow HTTP/HTTPS (Port 80/443) for OS updates.
    3.  **RDS Security Group (`RDS-SG`):**
        *   Inbound: Allow traffic from `LMS-SG` and `Faculty-SG` on database port (5432).
        *   Outbound: Deny all (default).

#### 1.1.4. Secure Administrative Access (AWS Systems Manager)
*   **Action:** Ensure EC2 instances are configured for secure access via AWS Systems Manager Session Manager.
*   **Details:** As per the implementation in Task 3, instances are launched without a key pair and administrative access is managed through IAM roles and Session Manager. This eliminates the need for a bastion host and open SSH/RDP ports, significantly improving the security posture and simplifying the architecture.

### 1.2. Identity and Access Management (IAM)

#### 1.2.1. Principle of Least Privilege for Permissions (IAM Roles)
*   **Action:** Create and configure IAM roles with minimal necessary permissions.
*   **Steps:**
    1.  **`YoobeeDeveloperRole`:** Create an IAM role for developers with permissions relevant to their tasks (e.g., read-only access to certain services, specific S3 bucket access).
    2.  **`YoobeeEC2AppRole`:** Create an IAM role for EC2 instances that need to interact with other AWS services (e.g., S3).
        *   **Policy Example (for S3 access):**
            ```json
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject"
                        ],
                        "Resource": "arn:aws:s3:::your-yoobee-bucket-name/*"
                    }
                ]
            }
            ```
    3.  **Attach `YoobeeEC2AppRole` to EC2 Instances:** Assign this role to the relevant EC2 instances during launch or modify existing instances.

#### 1.2.2. Enforcement of Multi-Factor Authentication (MFA)
*   **Action:** Enable and enforce MFA for the root user and all IAM users with console access.
*   **Steps:**
    1.  **Enable MFA for Root User:**
        *   Log in as the root user.
        *   Navigate to IAM Dashboard -> Security credentials.
        *   Activate MFA.
        *   Choose a virtual MFA device (e.g., Google Authenticator) and follow the setup steps.
    2.  **Enforce MFA for IAM Users (via Policy):**
        *   Create an IAM policy that denies actions if MFA is not present.
        *   **Policy Example:**
            ```json
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "DenyAllExceptWhenUsingMFA",
                        "Effect": "Deny",
                        "NotAction": [
                            "iam:CreateVirtualMFADevice",
                            "iam:EnableMFADevice",
                            "iam:ListMFADevices",
                            "iam:ResyncMFADevice",
                            "iam:DeleteVirtualMFADevice"
                        ],
                        "Resource": "*",
                        "Condition": {
                            "BoolIfExists": {
                                "aws:MultiFactorAuthPresent": "false"
                            }
                        }
                    }
                ]
            }
            ```
        *   Attach this policy to relevant IAM users or groups.

### 1.3. Data Protection

#### 1.3.1. Encryption in Transit (ALB HTTPS Listener)
*   **Action:** Configure the Application Load Balancer with an HTTPS listener.
*   **Steps:**
    1.  Request an SSL/TLS certificate from AWS Certificate Manager (ACM) for your domain.
    2.  In the ALB listener settings, add an HTTPS listener (Port 443).
    3.  Select the ACM certificate.
    4.  Configure the listener to forward traffic to your target group.

#### 1.3.2. Encryption at Rest
*   **Action:** Enable server-side encryption for S3 and encryption for RDS.
*   **Steps:**
    1.  **Amazon S3 (`yoobee-course-data` bucket):**
        *   Navigate to the S3 bucket properties.
        *   Enable Default encryption (Server-side encryption) using SSE-S3 or SSE-KMS.
    2.  **Amazon RDS (`yoobee-rds-instance`):**
        *   When creating the RDS instance, ensure "Encryption" is enabled. If modifying an existing instance, it might require creating a snapshot, copying it with encryption, and restoring from the encrypted snapshot.

### 1.4. Monitoring and Auditing (CloudTrail)

#### 1.4.1. API Call Monitoring for Critical Security Events
*   **Action:** Configure CloudTrail and Amazon EventBridge to set up alerts for critical security events. This is a crucial best practice for maintaining security oversight (Amazon Web Services, 2025).
*   **Steps:**
    1.  **Enable CloudTrail:** Ensure a CloudTrail trail is enabled for all regions and is logging to a secure S3 bucket.
    2.  **Create SNS Topic:** Go to Amazon SNS and create a new topic named `YoobeeCriticalSecurityAlerts`. Subscribe your email address to this topic to receive notifications.
    3.  **Create EventBridge Rules for Security Alerts:** Navigate to Amazon EventBridge -> Rules and create a new rule for each of the following critical events. For each rule, define an event pattern and set the target to the `YoobeeCriticalSecurityAlerts` SNS topic.

        *   **Alert on Root User Activity:**
            *   **Name:** `AlertOnRootUserActivity`
            *   **Event Pattern:**
                ```json
                {
                  "detail-type": ["AWS API Call via CloudTrail"],
                  "detail": {
                    "userIdentity": {
                      "type": ["Root"]
                    }
                  }
                }
                ```
        *   **Alert on IAM Policy Changes:**
            *   **Name:** `AlertOnIAMPolicyChanges`
            *   **Event Pattern:**
                ```json
                {
                  "detail-type": ["AWS API Call via CloudTrail"],
                  "detail": {
                    "eventSource": ["iam.amazonaws.com"],
                    "eventName": [
                      "DeleteGroupPolicy",
                      "DeleteRolePolicy",
                      "DeleteUserPolicy",
                      "PutGroupPolicy",
                      "PutRolePolicy",
                      "PutUserPolicy",
                      "CreatePolicy",
                      "DeletePolicy",
                      "CreatePolicyVersion",
                      "DeletePolicyVersion",
                      "AttachRolePolicy",
                      "DetachRolePolicy",
                      "AttachUserPolicy",
                      "DetachUserPolicy",
                      "AttachGroupPolicy",
                      "DetachGroupPolicy"
                    ]
                  }
                }
                ```
        *   **Alert on Unauthorized Console Login Attempts:**
            *   **Name:** `AlertOnFailedConsoleLogin`
            *   **Event Pattern:**
                ```json
                {
                  "detail-type": ["AWS Console Sign In via CloudTrail"],
                  "detail": {
                    "eventName": ["ConsoleLogin"],
                    "responseElements": {
                      "ConsoleLogin": ["Failure"]
                    }
                  }
                }
                ```
        *   **Alert on Security Group or Network ACL Changes:**
            *   **Name:** `AlertOnNetworkSecurityChanges`
            *   **Event Pattern:**
                ```json
                {
                  "detail-type": ["AWS API Call via CloudTrail"],
                  "detail": {
                    "eventSource": ["ec2.amazonaws.com"],
                    "eventName": [
                      "AuthorizeSecurityGroupIngress",
                      "AuthorizeSecurityGroupEgress",
                      "RevokeSecurityGroupIngress",
                      "RevokeSecurityGroupEgress",
                      "CreateNetworkAcl",
                      "CreateNetworkAclEntry",
                      "DeleteNetworkAcl",
                      "DeleteNetworkAclEntry",
                      "ReplaceNetworkAclEntry",
                      "ReplaceNetworkAclAssociation"
                    ]
                  }
                }
                ```

---

## 2. CloudWatch Monitoring and Alerting Implementation

*   **Action:** Create a CloudWatch alarm for EC2 instance CPU utilization.
*   **Steps:**
    1.  Navigate to CloudWatch -> Alarms -> Create alarm.
    2.  Select Metric: EC2 -> Per-Instance Metrics -> CPUUtilization.
    3.  Select the EC2 instance(s) to monitor.
    4.  **Specify Metric and Conditions:**
        *   Statistic: Average
        *   Period: 5 minutes
        *   Threshold type: Static
        *   Whenever CPUUtilization is: Greater/Equal
        *   Than: 80
        *   Datapoints to alarm: 3 out of 3 (for sustained period)
    5.  **Configure Actions:**
        *   Select an SNS topic (e.g., `YoobeeSecurityAlerts` or a new `YoobeeMonitoringAlerts` topic).
    6.  **Add Name and Description:** Give the alarm a descriptive name (e.g., `EC2-High-CPU-Alarm`).

### 2.2. CloudWatch Dashboard

*   **Action:** Create a custom CloudWatch dashboard for key metrics.
*   **Steps:**
    1.  Navigate to CloudWatch -> Dashboards -> Create dashboard.
    2.  Give it a name (e.g., `YoobeeCollegeDashboard`).
    3.  Add widgets for the following metrics:
        *   **EC2 CPU Utilization:** For all relevant EC2 instances.
        *   **ALB Network In/Out:** For the `yoobee-alb`.
        *   **RDS DB Connections:** For the `yoobee-rds-instance`.
        *   **RDS CPU Utilization:** For the `yoobee-rds-instance`.
    4.  Arrange widgets for clear visibility.

---

## 3. Cost Optimization Strategy (Practical Application with Theoretical Interpretation for Trusted Advisor)

This section outlines the theoretical approach to cost optimization, primarily focusing on how AWS Trusted Advisor would be used and broader strategies, as actual implementation is limited by the AWS Free Tier.

### 3.1. AWS Trusted Advisor Assessment (Practical Steps and Interpretation)

*   **Action:** Access AWS Trusted Advisor in the console, review its checks, and interpret potential recommendations for the deployed architecture across Cost Optimization, Security, Performance, and Fault Tolerance.
*   **Steps:**
    1.  **Access Trusted Advisor:**
        *   Navigate to the AWS Management Console.
        *   Search for "Trusted Advisor" and open the service.
        *   Review the dashboard for any existing checks or recommendations. (Note: Free Tier accounts have access to a limited set of checks, primarily related to Security and Service Limits. Full checks require a Business or Enterprise Support plan.)
    2.  **Interpret Available Checks and Document Findings:**
        *   Access the AWS Trusted Advisor console and confirmed the available checks under the Free Tier (e.g., **"MFA on Root Account"** and **"Security Groups - Specific Ports Unrestricted"**).
        *   **Example Report Wording:**
            *   "Accessed the AWS Trusted Advisor console and confirmed the available checks under the Free Tier (e.g., **'MFA on Root Account'** and **'Security Groups - Specific Ports Unrestricted'**)."
            *   "In the deployed architecture, administrative access is limited to AWS Systems Manager Session Manager, and MFA for the root account is enabled. Therefore, these security checks were interpreted as 'Green (OK)', confirming that basic security best practices were met at the design stage."
    3.  **Hypothesize Recommendations (for full checks):** Based on the Yoobee College architecture and general AWS best practices, hypothesize what specific recommendations Trusted Advisor *would* provide if you had access to the full suite of checks:
        *   **Cost Optimization:** (e.g., identifying underutilized EC2 instances, idle Elastic Load Balancers, unassociated Elastic IP addresses, or recommending Reserved Instances/Savings Plans for consistent workloads).
        *   **Security:** (e.g., MFA on root account, S3 bucket permissions, security group rules, IAM best practices).
        *   **Performance:** (e.g., high utilization EC2 instances, service limits approaching, EBS volume performance).
        *   **Fault Tolerance:** (e.g., RDS Multi-AZ configuration, ELB health checks, Auto Scaling Group balance across AZs).
    4.  **Formulate Actionable Strategy:** Based on the interpreted available checks and hypothesized recommendations, formulate a strategy to address the findings.
        *   **Example:** If "Security Groups - Specific Ports Unrestricted" is flagged, the action would be to restrict inbound rules to only necessary IP ranges or other security groups. If a hypothetical cost optimization recommendation suggests an idle ELB, the action would be to investigate and terminate it if no longer needed.
    5.  **Document Findings and Actions:** Record the findings from the available checks, the hypothesized recommendations for full checks, and the actionable strategies formulated.
### 3.2. AWS Compute Optimizer for Rightsizing

*   **Action:** Explore AWS Compute Optimizer to receive AI-driven recommendations for rightsizing resources like EC2 instances (Amazon Web Services, 2025). This ensures you are using the most cost-effective instance types for your workloads.
*   **Steps:**
    1.  **Opt-in to Compute Optimizer:**
        *   Navigate to **AWS Compute Optimizer** in the console.
        *   If it's your first time, you'll need to **opt in**. It can take up to 12 hours for AWS to analyze your resources and provide initial recommendations.
    2.  **Analyze Recommendations:**
        *   Once analysis is complete, the dashboard will show potential savings and optimization opportunities.
        *   Review the recommendations for your EC2 instances (`LMS-Server`, `Faculty-App-Server`). The tool may suggest changing the instance family (e.g., to a Graviton-based instance for better price-performance) or size (e.g., from `t2.micro` to a smaller or different type if underutilized).
        3.  **Interpret Findings and Document Actions:**
            *   Compute Optimizer provides a "Finding" status (e.g., "Under-provisioned," "Over-provisioned," "Optimized").
            *   For each finding, it will show the current instance type and up to three recommended instance types, along with the price and performance difference. This is critical for making informed decisions about instance selection.
            *   **Example Report Wording for Recommendations:**
                *   "**Finding:** `LMS-Server` was identified as 'Over-provisioned'. **Action:** Recommend rightsizing to `t2.small` to reduce costs."
                *   "**Finding:** `Faculty-App-Server` was identified as 'Optimized', but `t4g.small` (Graviton-based) was recommended. **Action:** Propose changing the instance type to `t4g.small` to improve price-performance ratio."

### 3.3. Broader Cost Reduction Strategy

*   **Action:** Detail additional cost-saving strategies beyond specific AWS tools.
*   **Steps:**
    1.  **Instance Scheduling:** Plan for shutting down non-production instances outside business hours.
    2.  **Reserved Instances (RIs) / Savings Plans:** Research and propose the use of RIs or Savings Plans for predictable, long-term workloads.
    3.  **S3 Intelligent-Tiering:** For data with unknown or changing access patterns in S3, consider using the `Intelligent-Tiering` storage class. It automatically moves data to the most cost-effective access tier without performance impact or operational overhead.
    4.  **Auto Scaling:** Discuss the potential for Auto Scaling Groups to dynamically adjust compute capacity based on demand, preventing over-provisioning.

### 3.4. Using the AWS Pricing Calculator and Cost Saving Analysis

*   **Action:** Use the AWS Pricing Calculator to compare On-Demand vs. Optimized (RI/Savings Plan) costs and perform a cost saving analysis against the current on-premise solution.
*   **Steps:**
    1.  **Estimate Baseline Cost:** Input all planned resources into the calculator using On-Demand pricing.
    2.  **Estimate Optimized Cost:** Adjust the pricing model for suitable resources (EC2, RDS) to RIs or Savings Plans.
    3.  **Analyze and Document Savings:** Compare the two estimates and document the potential cost savings.
*   **Detailed Cost Saving Analysis:**
    To provide a comprehensive understanding of the cost savings, a detailed breakdown of both the current on-premise infrastructure costs and the estimated AWS cloud costs was performed.

    **Current On-Premise Infrastructure Cost Breakdown:**
    The current on-premise cost of **$1,883 NZD/month** (Yoobee College Internal Data, n.d.) is derived from various factors including:
    *   Hardware depreciation and maintenance (servers, storage, networking equipment).
    *   Power and cooling expenses for the data center.
    *   Software licensing fees.
    *   IT staff salaries for maintenance and operations.
    *   Physical security and facility costs.
    *(User: Insert specific breakdown and assumptions here, if available, and any links to estimation tools or methodologies used for on-premise costs.)*

    **Estimated AWS Cloud Cost Breakdown (On-Demand vs. Optimized):**
    The estimated AWS cloud cost of approximately **$367 NZD/month** (converted from $222.42 USD) was calculated using the AWS Pricing Calculator, with the estimate date being November 23, 2025. This estimation considered the following services and configurations:

            *   **Amazon EC2:**
                *   **Linux Instances:** 2 x t2.micro instances (Shared Tenancy, Consistent Workload), Asia Pacific (Sydney) region, using Compute Savings Plans (3yr No Upfront), monitoring disabled, with no inbound, outbound, or intra-region data transfer selected, estimated at **$11.83 USD/month**.        *   **Windows Server Instances:** 2 x t2.micro instances (Shared Tenancy, Consistent Workload), Asia Pacific (Sydney) region, using Compute Savings Plans (3yr No Upfront), monitoring disabled, with no inbound, outbound, or intra-region data transfer selected, estimated at **$18.54 USD/month**.
    *   **Amazon RDS for PostgreSQL:**
        *   1 x db.t3.micro instance, 20 GB General Purpose SSD (gp2) storage, 100% utilized, Multi-AZ deployment, On-Demand pricing model, Asia Pacific (Sydney) region, estimated at **$90.93 USD/month**.
    *   **Amazon Virtual Private Cloud (VPC):**
        *   1 NAT Gateway, operating 22 working days per month, Asia Pacific (Sydney) region, estimated at **$48.97 USD/month**.
    *   **Elastic Load Balancing:**
        *   1 Application Load Balancer, Asia Pacific (Sydney) region, estimated at **$18.41 USD/month**.
    *   **Amazon Elastic Block Store (EBS):**
        *   4 volumes, 20 GB each, with an average duration of 730 hours per month, Snapshot Frequency (2x Daily), Amount changed per snapshot (3 GB), Asia Pacific (Sydney) region, estimated at **$33.74 USD/month**.

    The optimized cost reflects the application of Compute Savings Plans for EC2 instances and Multi-AZ deployment for RDS, contributing to significant savings compared to purely on-demand pricing.
    *(User: Insert link to the AWS Pricing Calculator estimate here.)*

*   **Cost Saving Analysis Summary:**
    *   **Current On-Premise Cost:** $1,883 NZD/month (given premise)
    *   **Estimated AWS Cloud Cost:** Approximately $367 NZD/month (converted from $222.42 USD)
    *   **Monthly Savings:** $1,883 NZD - $367 NZD = $1,516 NZD
    *   **Annual Savings:** $1,516 NZD * 12 = $18,192 NZD
    *   **Conclusion:** Migrating to AWS is projected to result in an annual cost saving of approximately $18,192 NZD. This significant reduction highlights the financial benefits of cloud adoption for Yoobee College.

---

## Conclusion

This report has detailed the comprehensive strategies and practical implementations undertaken to enhance the security and optimize the costs of Yoobee College's AWS cloud infrastructure. By applying robust security best practices, establishing proactive monitoring with CloudWatch, and implementing a multi-faceted cost optimization strategy, the college is well-positioned to achieve its digital transformation objectives. The projected annual savings of approximately $18,192 NZD, coupled with a significantly strengthened security posture, underscore the success of this cloud migration in delivering a scalable, secure, and cost-effective environment for students and staff.

---

## References

Amazon Web Services. (n.d.). *AWS security best practices*. Retrieved from https://aws.amazon.com/security/
Amazon Web Services. (n.d.). *AWS Well-Architected Framework - Cost Optimization Pillar*. Retrieved from https://aws.amazon.com/architecture/well-architected/
Amazon Web Services. (2025). *AWS security best practices and optimization strategies*. Retrieved from https://aws.amazon.com/documentation
TechTarget. (n.d.). *What is total cost of ownership (TCO) in IT? Definition and examples*. Retrieved from https://www.techtarget.com/searchcio/definition/total-cost-of-ownership-TCO
Yoobee College Internal Data. (n.d.). *On-premise infrastructure cost analysis*. [Specific source for $1,883 NZD/month to be provided by user].
