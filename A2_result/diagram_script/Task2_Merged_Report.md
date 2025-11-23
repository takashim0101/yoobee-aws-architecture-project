# Combined Task 2 Report and Implementation Guide

---

## Task 2 Report: Designing a Virtualization Architecture for Yoobee College

## 1. Introduction

This report details both the **theoretical design** and the **practical implementation** of the foundational cloud-based server virtualization infrastructure for Yoobee College of Creative Innovation, leveraging Amazon Web Services (AWS). This foundational setup, covered in this Task 2 report, serves as the blueprint and initial deployment for the further practical implementation detailed in Task 3 and the optimization and security enhancements covered in Task 4. The architecture aims to replace the existing on-premises systems—two Learning Management System (LMS) servers, two Faculty Application servers, and one Student Database—with a scalable, highly available, secure, and cost-effective cloud solution. This document outlines the infrastructure design, chosen AWS services, critical security considerations, including IAM policies, and the step-by-step execution of the core network components.

## 2. Theoretical Evaluation: Infrastructure Design and Chosen AWS Services

### 2.1 Infrastructure Design

The proposed architecture is built within a Virtual Private Cloud (VPC) in the **AWS Sydney (ap-southeast-2) Region**. While the newly established AWS Auckland (ap-southeast-6) Region was considered due to its location within New Zealand, the Sydney Region was ultimately selected for several strategic reasons. As a new region (Amazon Web Services, 2025b), there was uncertainty regarding the immediate availability and maturity of all required fully managed services (such as RDS Multi-AZ, NAT Gateway, ALB, and ASG) and the confirmed number of Availability Zones at the time of planning. In contrast, the Sydney Region is a long-established, mature region with a proven track record, comprehensive service support, and multiple AZs. Its proximity to New Zealand ensures low latency while providing the stability and full feature set necessary for this critical production environment. The design prioritizes high availability, scalability, and security, aligning with Yoobee College's requirements.

*   **VPC (Virtual Private Cloud):** A logically isolated section of the AWS Cloud where AWS resources are launched. Our VPC (`10.0.0.0/16`) provides a dedicated network space for Yoobee College's infrastructure, ensuring network isolation from other AWS customers.
*   **Availability Zones (AZs):** The VPC spans two distinct Availability Zones within the Sydney Region (e.g., `ap-southeast-2a` as AZ A and `ap-southeast-2b` as AZ B). Each AZ is an isolated location within a region, designed to be independent of failures in other AZs. This multi-AZ design is crucial for achieving high availability and fault tolerance, ensuring that the system remains operational even if one AZ experiences an outage (Amazon Web Services, 2025a).
*   **Subnets:** Within each AZ, both Public and Private Subnets are created.
    *   **Public Subnets (10.0.1.0/24 in AZ A, 10.0.3.0/24 in AZ B):** These subnets host resources that need direct internet access, such such as Application Load Balancers (ALBs) and NAT Gateways.
    *   **Private Subnets (10.0.2.0/24 in AZ A, 10.0.4.0/24 in AZ B):** These subnets host application servers (EC2 instances) and the RDS database. Resources in private subnets are not directly accessible from the internet, enhancing security.
    *   **Subnet Sizing Justification (/24 CIDR):** The choice of a /24 CIDR block for each subnet is a deliberate design decision based on several factors:
        *   **Sufficient IP Address Space:** A /24 subnet provides 251 usable IP addresses (after accounting for AWS reserved addresses). This is ample capacity for the current and foreseeable future needs of the resources within each subnet, including EC2 instances, load balancers, NAT gateways, and database instances.
        *   **Scalability:** This sizing provides sufficient room for horizontal scaling of application and database tiers without requiring network re-architecture or IP address exhaustion.
        *   **Standard Practice:** Utilizing /24 subnets is a common and well-understood practice in AWS network design, which contributes to the clarity, maintainability, and ease of management of the architecture.
        *   **Efficient Address Space Utilization:** It strikes an optimal balance between providing necessary IP addresses and efficiently utilizing the overall VPC CIDR block, preventing unnecessary waste of address space.
*   **Internet Gateway (IGW):** Enables communication between the VPC and the internet. All internet-bound traffic from public subnets, and outbound traffic from NAT Gateways, flows through the IGW.
*   **NAT Gateway:** Deployed in each public subnet, NAT Gateways allow instances in private subnets to initiate outbound connections to the internet (e.g., for software updates) while preventing unsolicited inbound connections from the internet. This is a key security measure.

### Figure 1: Yoobee College AWS Architecture Diagram

![Yoobee College AWS Architecture Diagram](diagram_script/yoobee_college_aws_architecture.png)

### 2.2 Chosen AWS Services and Justification

The selection of AWS services is driven by the need to meet Yoobee College's requirements for scalability, high availability, security, and cost-effectiveness.

*   **Application Load Balancer (ALB):**
    *   **Choice:** ALB is chosen for its ability to distribute incoming application traffic across multiple targets, such as EC2 instances, in multiple Availability Zones. It operates at the application layer (Layer 7), offering advanced routing features.
    *   **Justification:** Provides high availability by distributing traffic and performing health checks, ensuring requests are only sent to healthy instances. Enhances scalability by allowing the application to handle varying loads.
*   **Amazon EC2 (Elastic Compute Cloud):
    *   **Choice:** EC2 instances provide scalable compute capacity. Instances are deployed across multiple AZs to ensure high availability **within the Sydney (ap-southeast-2) Region**.
    *   **Justification:** Addresses the scalability requirement by allowing for the manual or scripted scaling of instances. Ensures high availability by distributing instances across multiple AZs, so if one AZ fails, instances in the other remain operational.
*   **Amazon RDS (Relational Database Service):**
    *   **Choice:** RDS for PostgreSQL (or a compatible engine) is selected for the student database. It is configured for Multi-AZ deployment **within the Sydney (ap-southeast-2) Region**.
    *   **Justification:** Provides high availability and data durability through automatic failover to a standby replica in a different AZ. Manages database patching, backups, and scaling, reducing operational overhead.
*   **Amazon S3 (Simple Storage Service):**
    *   **Choice:** S3 is a highly scalable, durable, and secure object storage service.
    *   **Justification:** Ideal for storing application data, user-uploaded content, and backups. Its high durability and availability ensure data integrity and accessibility. Security policies can be applied to restrict unauthorized access, meeting security requirements.
*   **AWS IAM (Identity and Access Management):**
    *   **Choice:** IAM is used to securely control access to AWS services and resources.
    *   **Justification:** Enables the definition of granular user roles and permissions, enforcing the principle of least privilege. This is fundamental for strong security compliance, ensuring only authorized entities can perform specific actions.
*   **Amazon CloudWatch:**
    *   **Choice:** CloudWatch is a monitoring and observability service.
    *   **Justification:** Collects and tracks metrics, collects log files, and sets alarms. Essential for monitoring the health and performance of EC2 instances, RDS, and other AWS resources, allowing for proactive issue resolution and performance optimization.

## Phase 1: Network Foundation Setup (VPC, Subnets, Internet Gateway, NAT Gateway)

### Step 1: Create a VPC (Virtual Private Cloud)

*   **Name tag:** `YoobeeCollegeVPC`
*   **IPv4 CIDR block:** `10.0.0.0/16`
*   **TAKE SCREENSHOT:** Of the VPCs list showing `YoobeeCollegeVPC` created.

### Step 2: Create Subnets (4 Subnets Across 2 AZs)

*   **VPC ID:** Select `YoobeeCollegeVPC`.
*   **Public Subnet A:**
    *   **Name tag:** `YoobeePublicSubnetA`
    *   **Availability Zone:** Select a specific AZ identifier (e.g., `ap-southeast-2a`).
    *   **IPv4 CIDR block:** `10.0.1.0/24`
*   **Private Subnet A:**
    *   **Name tag:** `YoobeePrivateSubnetA`
    *   **Availability Zone:** *Same AZ* as Public Subnet A.
    *   **IPv4 CIDR block:** `10.0.2.0/24`
*   **Public Subnet B:**
    *   **Name tag:** `YoobeePublicSubnetB`
    *   **Availability Zone:** Select a *different AZ* from A (e.g., `ap-southeast-2b`).
    *   **IPv4 CIDR block:** `10.0.3.0/24`
*   **Private Subnet B:**
    *   **Name tag:** `YoobeePrivateSubnetB`
    *   **Availability Zone:** *Same AZ* as Public Subnet B.
    **IPv4 CIDR block:** `10.0.4.0/24`
*   **Action:** Enable auto-assign public IPv4 addresses for `YoobeePublicSubnetA` and `YoobeePublicSubnetB`.
*   **TAKE SCREENSHOT:** Of the Subnets list showing all four subnets created.

### Step 3: Create and Attach an Internet Gateway (IGW)

*   **Name tag:** `YoobeeCollegeIGW`
*   **Action:** Attach the IGW to `YoobeeCollegeVPC`.
*   **TAKE SCREENSHOT:** Showing the `YoobeeCollegeIGW` attached to `YoobeeCollegeVPC`.

### Step 4: Create NAT Gateway (Cost Optimized Design: Only 1)

*   **Purpose:** Provide outbound internet access for private subnets via the public subnet in AZ A.
*   **Name tag:** `YoobeeNATGatewayA`
*   **Subnet:** Choose **`YoobeePublicSubnetA`** (Only one is created, aligning with cost-optimized design).
*   **Elastic IP allocation:** Click "Allocate Elastic IP".
*   **TAKE SCREENSHOT:** Showing `YoobeeNATGatewayA` in "Available" status.

### Step 5: Configure Route Tables

*   **1. Configure Public Route Table (`YoobeePublicRT`):**
    *   **Action:** Rename the default route table to `YoobeePublicRT`.
    *   **Route:** Add route: Destination `0.0.0.0/0` -> Target `YoobeeCollegeIGW`.
    *   **Association:** Associate with `YoobeePublicSubnetA` and `YoobeePublicSubnetB`.
*   **2. Create and Configure Private Route Table A (`YoobeePrivateRTA`):**
    *   **Route:** Add route: Destination `0.0.0.0/0` -> Target **`YoobeeNATGatewayA`**.
    *   **Association:** Associate with `YoobeePrivateSubnetA`.
*   **3. Create and Configure Private Route Table B (`YoobeePrivateRTB`):**
    *   **Route:** Add route: Destination `0.0.0.0/0` -> Target **`YoobeeNATGatewayA`**. (Uses the single NAT Gateway in AZ A)
    *   **Association:** Associate with `YoobeePrivateSubnetB`.
*   **TAKE SCREENSHOT:** Showing routes and subnet associations for `YoobeePublicRT`, `YoobeePrivateRTA`, and `YoobeePrivateRTB`.

## Phase 2: Security Setup (Security Groups and IAM)

### Step 6: Create Security Groups

*   **Purpose:** Control traffic flow based on the principle of least privilege. (Note: No Bastion Host is created; administrative access is handled by SSM).

*   **`ALB-SG` (Application Load Balancer Security Group):**
    *   **Inbound:** HTTP 80 (`0.0.0.0/0`), HTTPS 443 (`0.0.0.0/0`).
    *   **Outbound:** To `LMS-SG` and `Faculty-SG` (Ports 80/443).
*   **`LMS-SG` (LMS Servers Security Group):**
    *   **Inbound:** HTTP 80/443 (Source: `ALB-SG`), **SSM Managed Instance Access (no SSH port open)**.
    *   **Outbound:** To `RDS-SG` (Port **5432**), HTTPS 443 (`0.0.0.0/0`) for updates.
*   **`Faculty-SG` (Faculty App Servers Security Group):**
    *   **Inbound:** HTTP 80/443 (Source: `ALB-SG`), **SSM Managed Instance Access (no RDP port open)**.
    *   **Outbound:** To `RDS-SG` (Port **5432**), HTTPS 443 (`0.0.0.0/0`) for updates.
*   **`RDS-SG` (RDS Database Security Group):**
    *   **Inbound:** PostgreSQL Port **5432** (Source: `LMS-SG` and `Faculty-SG`).
    *   **Outbound:** **Remove all default outbound rules** (strictest security).
*   **TAKE SCREENSHOT:** Of the `RDS-SG` showing the PostgreSQL inbound rule and no outbound rules.

### Step 7: Create IAM Roles and Policies

*   **Purpose:** Define permissions for services, including enabling EC2 instances for secure management (SSM) and resource access (S3/CloudWatch).

*   **1. Create `YoobeeEC2AppRole`:**
    *   **Use case:** EC2
    *   **Attach Policies (Managed):**
        1.  `AmazonSSMManagedInstanceCore` **(Crucial for SSM Access)**
        2.  `AmazonS3ReadOnlyAccess`
        3.  `CloudWatchAgentServerPolicy`
*   **2. Create `YoobeeDeveloperRole`:**
    *   **Action:** Create the **custom policy** `YoobeeDeveloperPolicy` using the JSON provided in your report.
    *   **Action:** Create the role `YoobeeDeveloperRole` and attach the custom policy to it.
*   **TAKE SCREENSHOT:** Of the `YoobeeEC2AppRole` details page showing the attached policies, especially confirming `AmazonSSMManagedInstanceCore`.

## 3. Theoretical Evaluation: Security Considerations and IAM Policies

Security is paramount for Yoobee College. The architecture incorporates a multi-layered security approach.

### 3.1 Network Security Controls

*   **Security Groups:** Act as virtual firewalls for EC2 instances and other resources, controlling inbound and outbound traffic at the instance level. Rules will be defined to allow only necessary traffic (e.g., HTTP/HTTPS to ALBs, database port to application servers).
*   **Network Access Control Lists (NACLs):** Provide an additional, stateless layer of security at the subnet level, allowing or denying traffic to and from subnets.
*   **Private Subnets:** Placing application servers and databases in private subnets prevents direct internet access, significantly reducing the attack surface.

### 3.1.1 Security Group Rules

Security Groups are stateful firewalls that control traffic at the instance level. The following rules will be implemented to enforce the principle of least privilege:

*   **`ALB-SG` (Application Load Balancer Security Group):**
    *   **Inbound:**
        *   Allow HTTP (Port 80) from anywhere (0.0.0.0/0) for web traffic.
        *   Allow HTTPS (Port 443) from anywhere (0.0.0.0/0) for secure web traffic.
    *   **Outbound:**
        *   Allow traffic to the `LMS-SG` and `Faculty-SG` on the application ports (e.g., 80/443).

*   **`LMS-SG` (LMS Servers Security Group):**
    *   **Inbound:**
        *   Allow traffic on the application port (e.g., 80/443) from the `ALB-SG`.
    *   **Outbound:**
        *   Allow traffic to the `RDS-SG` on the database port (5432).
        *   Allow HTTP (Port 80) and HTTPS (Port 443) to the internet (0.0.0.0/0) via the NAT Gateway for software updates.

*   **`Faculty-SG` (Faculty App Servers Security Group):**
    *   **Inbound:**
        *   Allow traffic on the application port (e.g., 80/443) from the `ALB-SG`.
    *   **Outbound:**
        *   Allow traffic to the `RDS-SG` on the database port (5432).
        *   Allow HTTP (Port 80) and HTTPS (Port 443) to the internet (0.0.0.0/0) via the NAT Gateway for software updates.

*   **`RDS-SG` (RDS Database Security Group):**
    *   **Inbound:**
        *   Allow PostgreSQL Port (5432) from the `LMS-SG` and `Faculty-SG`.
    *   **Outbound:**
        *   No outbound traffic is required for the database. All outbound rules will be removed to enforce the strictest security posture.

### 3.1.2 Secure Administrative Access (AWS Systems Manager)

To align with modern security best practices and simplify the architecture, administrative access to EC2 instances is handled by **AWS Systems Manager (SSM) Session Manager** instead of a traditional Bastion Host (Amazon Web Services, 2025c).

#### Justification for IT Admin Position and Connection

**1. Positional Justification**
The placement of the IT Admin icon outside the VPC in the architecture diagram is appropriate for the following reasons:
*   **External Presence:** The IT Admin accesses the system from a logical network external to the AWS VPC, such as a home or corporate network.
*   **AWS Console Access:** The Admin connects to the AWS Management Console via the internet and utilizes IAM and SSM services from there to manage resources within the VPC.

**2. Logical Interpretation of SSM Connection**
In the current architecture without a Bastion Host, the connection from the Admin to the EC2 instances is interpreted as follows:
*   **Admin (Actor):** A person outside the VPC who logs into the AWS Management Console.
*   **Connection Path (Diagram Representation):** The absence of a solid connection line (or the use of a dotted line) is intentional. A direct network connection is not required. SSM connects the Admin's browser session to the SSM Agent on the EC2 instance through the AWS control plane.
*   **Authentication/Authorization (Underlying Prerequisite):** Access is predicated on IAM. The Admin is authenticated as an IAM user/role, and the SSM connection is authorized based on the associated IAM policies.

Therefore, placing the Admin outside the VPC and not drawing a specific network line (e.g., through an IGW) best represents the **"policy-based logical connection"** nature of SSM. This diagram clearly illustrates the best practice of using SSM for administrative access.

### 3.2 AWS IAM Policies for Security and Compliance

AWS IAM is central to ensuring strong security compliance by managing access to resources.

*   **Key IAM Principles:**
    *   **Least Privilege:** Users and roles are granted only the minimum permissions required to perform their tasks (Amazon Web Services, n.d.).
    *   **Role-Based Access Control (RBAC):** Permissions are assigned to roles, and users assume these roles, simplifying management and enhancing security.
    *   **Strong Authentication (MFA):** Multi-Factor Authentication will be enforced for all administrative and sensitive user accounts to add an extra layer of security.
*   **Proposed IAM Roles and Policies:**
    *   **Administrator Role (`YoobeeAdminRole`):** For IT staff requiring full administrative access, protected by MFA.
    *   **Developer/Application Deployment Role (`YoobeeDeveloperRole`):** For developers to manage specific resources (EC2, ELB, S3, CloudWatch) related to application deployment, with permissions scoped to their needs.
    *   **Read-Only Auditor/Monitor Role (`YoobeeAuditorRole`):** For staff needing to view configurations, logs, and metrics without modification privileges.
    *   **EC2 Instance Role (`YoobeeEC2AppRole`):** Attached to EC2 instances, granting necessary permissions for applications to interact with other AWS services (e.g., S3 for data, RDS for database access, CloudWatch for metrics).
    *   **RDS Role (`YoobeeRDSAccessRole`):** For RDS to interact with other AWS services (e.g., S3 for backups).

*   **Example IAM Policy Documents:**

    To illustrate the principle of least privilege, here are some example policy documents for the proposed roles.

    **1. `YoobeeDeveloperRole` Policy:**
    This policy allows developers to manage application-related services but restricts access to sensitive resources like IAM and billing.

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ec2:Describe*",
                    "ec2:StartInstances",
                    "ec2:StopInstances",
                    "ec2:RebootInstances",
                    "elasticloadbalancing:Describe*",
                    "s3:ListBucket",
                    "s3:GetObject",
                    "s3:PutObject",
                    "rds:Describe*",
                    "cloudwatch:GetMetricData",
                    "cloudwatch:DescribeAlarms"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject"
                ],
                "Resource": "arn:aws:s3:::yoobee-app-data/*"
            }
        ]
    }
    ```

    **2. `YoobeeEC2AppRole` Policy:**
    This policy is attached to the EC2 instances and allows the application running on them to access the S3 bucket for course data and write logs to CloudWatch.

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::yoobee-course-data",
                    "arn:aws:s3:::yoobee-course-data/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            }
        ]
    }
    ```

*   **Security Policies and Compliance:** Implementation will include strong password policies, regular access key rotation, AWS CloudTrail for API activity logging, and AWS Config for continuous configuration monitoring to ensure compliance and auditability.

## 4. Justification for Selected Configurations

The chosen architecture and service configurations directly address Yoobee College's key requirements:

*   **Cost-Effectiveness:** Leveraging a hybrid pricing model (Reserved Instances for predictable workloads, On-Demand with Auto Scaling for variable loads) minimizes expenditure. The pay-as-you-go model and dynamic scaling prevent over-provisioning.
*   **Scalability:** The architecture supports scalability by allowing for the addition of more EC2 instances, which can be placed behind the Application Load Balancer.
*   **Security:** A multi-layered approach with VPC isolation, granular Security Groups, and comprehensive IAM policies (Least Privilege, RBAC, MFA) protects sensitive academic and student data. CloudTrail and AWS Config provide auditing and compliance capabilities.
*   **High Availability:** Multi-AZ deployments for both EC2 instances and RDS databases, combined with Application Load Balancers, eliminate single points of failure. This ensures continuous service availability even during component failures or AZ outages.

This design provides a robust, secure, and flexible foundation for Yoobee College's digital transformation, enabling them to deliver enhanced academic services efficiently.

---

## 5. Practical Implementation and Verification

The initial network infrastructure, including the Virtual Private Cloud (VPC), subnets across multiple Availability Zones, Internet Gateway, and NAT Gateways, has been successfully deployed in AWS as per the design outlined in Section 2.1. This foundational deployment establishes the secure and highly available network environment for Yoobee College's applications.

*(Placeholder for a high-level screenshot of the deployed VPC and subnets in the AWS Console)*

The detailed practical implementation of the core compute, storage, and load balancing components (EC2 instances, S3 bucket, Elastic Load Balancer) designed in this report is thoroughly documented, with step-by-step configurations and supporting screenshots, in **[Task 3 Report: Practical Implementation of Virtual Machines, Storage, and Load Balancing](C:\Portfolio\LINZ_Cloud_CV\A3_result\Task3_Report.md)**.

Furthermore, the implementation of security enhancements, CloudWatch monitoring and alerting, and the cost optimization strategy, including their verification, are detailed in **[Task 4 Report: Optimization and Security](C:\Portfolio\LINZ_Cloud_CV\A4_result\Task4_Report.md)**.

These comprehensive reports collectively serve as verification of the deployed architecture and its adherence to the design principles outlined herein.

---

## Appendix: Architecture Diagram Source Code

```mermaid
graph TD
    %% === Design and Style Definitions ===
    classDef vpc fill:#f8fafc,stroke:#64748b,stroke-width:2px,stroke-dasharray: 5 5;
    classDef public fill:#dcfce7,stroke:#166534,stroke-width:2px;
    classDef private fill:#e0e7ff,stroke:#3730a3,stroke-width:2px;
    classDef db fill:#3b82f6,stroke:#1e3a8a,stroke-width:2px,color:white;
    classDef compute fill:#f97316,stroke:#c2410c,stroke-width:2px,color:white;
    classDef network fill:#8b5cf6,stroke:#5b21b6,stroke-width:2px,color:white;
    classDef storage fill:#16a34a,stroke:#14532d,stroke-width:2px,color:white;
    classDef admin fill:#a16207,stroke:#713f12,stroke-width:2px,color:white;
    classDef user fill:#0ea5e9,stroke:#0369a1,stroke-width:2px,color:white;

    %% === Actors ===
    User((Student/Faculty<br>Internet User)):::user
    Admin((IT Admin<br>via AWS Console/SSM)):::admin

    %% === AWS Cloud Region ===
    subgraph AWS [AWS Cloud Region]
        
        %% S3 (Outside VPC)
        S3(S3 Bucket<br>Course Data):::storage

        %% VPC (Virtual Network)
        subgraph VPC [VPC: 10.0.0.0/16]
            class VPC vpc

            IGW(Internet Gateway):::network
            VPC_Endpoint(VPC Gateway Endpoint<br>for S3):::network %% Added VPC Endpoint

            %% --- Availability Zone A ---
            subgraph AZ_A [Availability Zone ap-southeast-2a]
                style AZ_A fill:#ffffff,stroke:#94a3b8

                %% Public Subnet A
                subgraph Pub_A [Public Subnet A<br>10.0.1.0/24]
                    class Pub_A public
                    ALB(Application Load Balancer):::network
                    NAT(NAT Gateway):::network
                end

                %% Private Subnet A
                subgraph Priv_A [Private Subnet A<br>10.0.2.0/24]
                    class Priv_A private
                    LMS_A[LMS Server A<br>Linux EC2]:::compute
                    Fac_A[Faculty App A<br>Windows EC2]:::compute
                    RDS_M[(RDS Master<br>PostgreSQL)]:::db
                end
            end

            %% --- Availability Zone B ---
            subgraph AZ_B [Availability Zone ap-southeast-2b]
                style AZ_B fill:#ffffff,stroke:#94a3b8

                %% Public Subnet B
                subgraph Pub_B [Public Subnet B<br>10.0.3.0/24]
                    class Pub_B public
                    %% ALB Redundancy Area
                end

                %% Private Subnet B
                subgraph Priv_B [Private Subnet B<br>10.0.4.0/24]
                    class Priv_B private
                    LMS_B[LMS Server B<br>Standby]:::compute
                    Fac_B[Faculty App B<br>Standby]:::compute
                    RDS_S[(RDS Standby<br>Replica<br>PostgreSQL)]:::db
                end
            end
        end
    end

    %% === Communication Flow ===
    User --> IGW %% Removed HTTPS label
    IGW --> ALB
    ALB -->|Traffic Dist| LMS_A & Fac_A
    ALB -->|Traffic Dist| LMS_B & Fac_B

    %% Admin Access (Via SSM - not a direct network path)
    Admin -.->|SSM Session Manager| LMS_A & Fac_A & LMS_B & Fac_B & RDS_M %% Updated label

    %% Database & S3 Access
    LMS_A & Fac_A -->|Read/Write| RDS_M
    LMS_B & Fac_B -->|Read/Write| RDS_M
    LMS_A & Fac_A & LMS_B & Fac_B -.->|IAM Role via Route Table| VPC_Endpoint %% Modified S3 access
    VPC_Endpoint -.->|Private Link| S3 %% Modified S3 access

    %% Outbound (Via NAT)
    LMS_A & Fac_A -.->|Updates| NAT
    LMS_B & Fac_B -.->|Updates| NAT
    NAT -.-> IGW
    
    %% DB Sync
    RDS_M -.->|Sync Replication| RDS_S
```

---

## References

Amazon Web Services. (2025c). *AWS Systems Manager features*. Amazon Web Services. https://aws.amazon.com/systems-manager/features/
Amazon Web Services. (n.d.). *Security best practices in IAM*. AWS Identity and Access Management. Retrieved November 23, 2025, from https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege
Amazon Web Services. (2025a). *Amazon RDS Multi-AZ deployments*. Amazon Web Services. https://aws.amazon.com/rds/features/multi-az/
Amazon Web Services. (2025b). *AWS Asia Pacific (Auckland) Region (ap-southeast-6) now open*. AWS News Blog. Retrieved November 22, 2025, from https://aws.amazon.com/blogs/aws/

---

## Task 2: AWS Virtualization Architecture - Implementation Guide

# Task 2: AWS Virtualization Architecture - Implementation Guide

This guide provides step-by-step instructions for implementing the foundational AWS network and security architecture designed in your Task 2 report. It is intended for beginners and will focus on using the AWS Management Console (GUI).

**Goal:** To deploy the secure, highly available network foundation (VPC, Subnets, Route Tables, Security Groups, and IAM Roles) for the Yoobee College AWS architecture.

**Reference Files:**
*   Your main report: `C:\Portfolio\LINZ_Cloud_CV\A2_result\Task2_Report_and_Diagram_Code.md`
*   Your architecture diagram: `C:\Portfolio\LINZ_Cloud_CV\A2_result\diagram_script\yoobee_college_aws_architecture.png`

**Important Considerations:**
*   **Region:** Use the **Sydney (ap-southeast-2) Region**.
*   **Documentation for Your Report:** For each significant step, take clear, labeled screenshots. You will use these screenshots for the "5. Practical Implementation and Verification" section of your report.

---

## Phase 1: Network Foundation Setup (VPC, Subnets, Internet Gateway, NAT Gateway)

### Step 1: Create a VPC (Virtual Private Cloud)

*   **Name tag:** `YoobeeCollegeVPC`
*   **IPv4 CIDR block:** `10.0.0.0/16`
*   **TAKE SCREENSHOT:** Of the VPCs list showing `YoobeeCollegeVPC` created.

### Step 2: Create Subnets (4 Subnets Across 2 AZs)

*   **VPC ID:** Select `YoobeeCollegeVPC`.
*   **Public Subnet A:**
    *   **Name tag:** `YoobeePublicSubnetA`
    *   **Availability Zone:** Select a specific AZ identifier (e.g., `ap-southeast-2a`).
    *   **IPv4 CIDR block:** `10.0.1.0/24`
*   **Private Subnet A:**
    *   **Name tag:** `YoobeePrivateSubnetA`
    *   **Availability Zone:** *Same AZ* as Public Subnet A.
    *   **IPv4 CIDR block:** `10.0.2.0/24`
*   **Public Subnet B:**
    *   **Name tag:** `YoobeePublicSubnetB`
    *   **Availability Zone:** Select a *different AZ* from A (e.g., `ap-southeast-2b`).
    *   **IPv4 CIDR block:** `10.0.3.0/24`
*   **Private Subnet B:**
    *   **Name tag:** `YoobeePrivateSubnetB`
    *   **Availability Zone:** *Same AZ* as Public Subnet B.
    *   **IPv4 CIDR block:** `10.0.4.0/24`
*   **Action:** Enable auto-assign public IPv4 addresses for `YoobeePublicSubnetA` and `YoobeePublicSubnetB`.
*   **TAKE SCREENSHOT:** Of the Subnets list showing all four subnets created.

### Step 3: Create and Attach an Internet Gateway (IGW)

*   **Name tag:** `YoobeeCollegeIGW`
*   **Action:** Attach the IGW to `YoobeeCollegeVPC`.
*   **TAKE SCREENSHOT:** Showing the `YoobeeCollegeIGW` attached to `YoobeeCollegeVPC`.

### Step 4: Create NAT Gateway (Cost Optimized Design: Only 1)

*   **Purpose:** Provide outbound internet access for private subnets via the public subnet in AZ A.
*   **Name tag:** `YoobeeNATGatewayA`
*   **Subnet:** Choose **`YoobeePublicSubnetA`** (Only one is created, aligning with cost-optimized design).
*   **Elastic IP allocation:** Click "Allocate Elastic IP".
*   **TAKE SCREENSHOT:** Showing `YoobeeNATGatewayA` in "Available" status.

### Step 5: Configure Route Tables

*   **1. Configure Public Route Table (`YoobeePublicRT`):**
    *   **Action:** Rename the default route table to `YoobeePublicRT`.
    *   **Route:** Add route: Destination `0.0.0.0/0` -> Target `YoobeeCollegeIGW`.
    *   **Association:** Associate with `YoobeePublicSubnetA` and `YoobeePublicSubnetB`.
*   **2. Create and Configure Private Route Table A (`YoobeePrivateRTA`):**
    *   **Route:** Add route: Destination `0.0.0.0/0` -> Target **`YoobeeNATGatewayA`**.
    *   **Association:** Associate with `YoobeePrivateSubnetA`.
*   **3. Create and Configure Private Route Table B (`YoobeePrivateRTB`):**
    *   **Route:** Add route: Destination `0.0.0.0/0` -> Target **`YoobeeNATGatewayA`**. (Uses the single NAT Gateway in AZ A)
    *   **Association:** Associate with `YoobeePrivateSubnetB`.
*   **TAKE SCREENSHOT:** Showing routes and subnet associations for `YoobeePublicRT`, `YoobeePrivateRTA`, and `YoobeePrivateRTB`.

---

## Phase 2: Security Setup (Security Groups and IAM)

### Step 6: Create Security Groups

*   **Purpose:** Control traffic flow based on the principle of least privilege. (Note: No Bastion Host is created; administrative access is handled by SSM).

*   **`ALB-SG` (Application Load Balancer Security Group):**
    *   **Inbound:** HTTP 80 (`0.0.0.0/0`), HTTPS 443 (`0.0.0.0/0`).
    *   **Outbound:** To `LMS-SG` and `Faculty-SG` (Ports 80/443).
*   **`LMS-SG` (LMS Servers Security Group):**
    *   **Inbound:** HTTP 80/443 (Source: `ALB-SG`), **SSM Managed Instance Access (no SSH port open)**.
    *   **Outbound:** To `RDS-SG` (Port **5432**), HTTPS 443 (`0.0.0.0/0`) for updates.
*   **`Faculty-SG` (Faculty App Servers Security Group):**
    *   **Inbound:** HTTP 80/443 (Source: `ALB-SG`), **SSM Managed Instance Access (no RDP port open)**.
    *   **Outbound:** To `RDS-SG` (Port **5432**), HTTPS 443 (`0.0.0.0/0`) for updates.
*   **`RDS-SG` (RDS Database Security Group):**
    *   **Inbound:** PostgreSQL Port **5432** (Source: `LMS-SG` and `Faculty-SG`).
    *   **Outbound:** **Remove all default outbound rules** (strictest security).
*   **TAKE SCREENSHOT:** Of the `RDS-SG` showing the PostgreSQL inbound rule and no outbound rules.

### Step 7: Create IAM Roles and Policies

*   **Purpose:** Define permissions for services, including enabling EC2 instances for secure management (SSM) and resource access (S3/CloudWatch).

*   **1. Create `YoobeeEC2AppRole`:**
    *   **Use case:** EC2
    *   **Attach Policies (Managed):**
        1.  `AmazonSSMManagedInstanceCore` **(Crucial for SSM Access)**
        2.  `AmazonS3ReadOnlyAccess`
        3.  `CloudWatchAgentServerPolicy`
*   **2. Create `YoobeeDeveloperRole`:**
    *   **Action:** Create the **custom policy** `YoobeeDeveloperPolicy` using the JSON provided in your report.
    *   **Action:** Create the role `YoobeeDeveloperRole` and attach the custom policy to it.
*   **TAKE SCREENSHOT:** Of the `YoobeeEC2AppRole` details page showing the attached policies, especially confirming `AmazonSSMManagedInstanceCore`.

---

## 5. Verification (Foundation Complete)

*   **Action:** Check the VPC Dashboard to confirm the VPC, 4 subnets, 1 IGW, 1 NAT Gateway, and 3 Route Tables are all present and correctly configured.
*   **TAKE SCREENSHOT:** (Optional) A single, comprehensive screenshot of the VPC topology, if available, or a final check of the VPC dashboard summary.

---

## Cleanup (Crucial for Cost Management!)

After you have completed this Task 2 implementation and obtained the necessary screenshots, you can proceed to Task 3 (EC2, RDS, ALB, S3). If you need to stop work, delete the NAT Gateway and its associated Elastic IP to stop incurring significant charges.

**Full Deletion Order (After completing Task 4):**
1.  Delete all EC2 instances, ASGs, Launch Templates, ALB, RDS, S3.
2.  **Delete NAT Gateway and release Elastic IP.**
3.  Detach and Delete Internet Gateway.
4.  Delete Route Tables (Private RTs first).
5.  Delete Security Groups (after all associated resources are gone).
6.  Delete Subnets.
7.  Delete VPC.
8.  Delete IAM Roles and Policies.
