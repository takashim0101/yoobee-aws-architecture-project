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
1.  Delete all EC2 instances, ALB, RDS, S3.
2.  **Delete NAT Gateway and release Elastic IP.**
3.  Detach and Delete Internet Gateway.
4.  Delete Route Tables (Private RTs first).
5.  Delete Security Groups (after all associated resources are gone).
6.  Delete Subnets.
7.  Delete VPC.
8.  Delete IAM Roles and Policies.

