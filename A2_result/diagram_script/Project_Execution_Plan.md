# Project Execution Plan: Yoobee College AWS Architecture Implementation

This comprehensive plan details every step required to implement the Yoobee College AWS Architecture, from initial preparation through to the completion of Task 2, Task 3, and Task 4. This guide is designed for beginners, ensuring no omissions and providing clear instructions to minimize errors.

---

## Phase 0: Initial Preparation (Before Touching AWS Console)

**Goal:** Ensure all prerequisites are met and you have a clear understanding of the project scope and tools.

1.  **Read This Entire Plan:**
    *   **Action:** Read this `Project_Execution_Plan.md` document from beginning to end at least once.
    *   **Purpose:** To gain a high-level understanding of the entire project flow, dependencies, and expected outcomes.
    *   **Verification:** You have a general idea of what needs to be done.

2.  **Complete `Preparation_Guide.md`:**
    *   **Action:** Follow every step detailed in `C:\Portfolio\LINZ_Cloud_CV\A2_result\diagram_script\Preparation_Guide.md`.
    *   **Purpose:** To set up your AWS account, configure IAM users/roles, create EC2 Key Pairs, and understand service-specific planning. This is crucial for security and smooth execution.
    *   **Verification:**
        *   You have an active AWS account.
        *   You have an IAM user with `AdministratorAccess` (or equivalent) and MFA enabled.
        *   Your AWS root account has MFA enabled.
        *   You have thoroughly reviewed `Task3_Implementation_Guide.md` and `Task4_Implementation_Guide.md`.
        *   You have a basic understanding of the AWS services involved (VPC, EC2, RDS, S3, ELB, IAM, CloudWatch).

---

## Phase 1: Task 2 - Architecture Design & Documentation

**Goal:** Finalize the architecture design, implement the foundational network infrastructure and initial security configurations, and ensure the Task 2 report (`Task2_Report_and_Diagram_Code.md`) is complete with all theoretical details, practical steps, and references.

1.  **Review `Task2_Report_and_Diagram_Code.md`:**
    *   **Action:** Open `C:\Portfolio\LINZ_Cloud_CV\A2_result\diagram_script\Task2_Report_and_Diagram_Code.md`.
    *   **Purpose:** This document contains the theoretical design of the architecture. Ensure you understand all sections (Introduction, Infrastructure Design, Chosen AWS Services, Security Considerations, Justification).
    *   **Verification:** You have read and understood the design.

2.  **Generate/Verify Architecture Diagram:**
    *   **Action:** Execute the `create_diagram.py` script to generate the `yoobee_college_aws_architecture.png` file.
    *   **Command:** `.\venv\Scripts\python.exe create_diagram.py` (if using Windows PowerShell with venv) or `python3 create_diagram.py` (if using Linux/macOS with python3 in path).
    *   **Purpose:** To create the visual representation of your architecture, which is a deliverable for Task 2.
    *   **Verification:** The `yoobee_college_aws_architecture.png` file exists in the `diagram_script` directory and accurately reflects the design, including specific AZ names.

3.  **Finalize `Task2_Report_and_Diagram_Code.md` Content:**
    *   **Action:** Ensure all sections of `C:\Portfolio\LINZ_Cloud_CV\A2_result\diagram_script\Task2_Report_and_Diagram_Code.md` are complete and accurate.
    *   **Purpose:** This is your primary design deliverable. Section 5 should now correctly reference `Task3_Report.md` and `Task4_Report.md`.
    *   **Verification:** The report is ready for submission (except for the practical screenshot in Section 5, which will be added after deployment).

---

## Phase 2: Task 3 - Practical Implementation (Core Compute, Storage, and Load Balancing Deployment)

**Goal:** Deploy the core AWS infrastructure components (EC2, S3, RDS, ALB) as designed in Task 2, following `Task3_Implementation_Guide.md`, and document the results in `Task3_Report.md`. This phase builds upon the foundational network infrastructure and initial security configurations established in Task 2.

**Important:** Throughout this phase, **TAKE SCREENSHOTS** of every significant step and configuration in the AWS Management Console. These are crucial for `Task3_Report.md`.

1.  **Open `Task3_Implementation_Guide.md`:**
    *   **Action:** Open `C:\Portfolio\LINZ_Cloud_CV\A2_result\diagram_script\Task3_Implementation_Guide.md`.
    *   **Purpose:** This is your step-by-step guide for deployment.

2.  **Review Key Implementation Checkpoints:**
    *   **Action:** Re-read the "Key Implementation Checkpoints" section at the beginning of `Task3_Implementation_Guide.md`.
    *   **Purpose:** To remind yourself of critical considerations like Security Group cross-referencing, Region/AZ consistency, and cleanup.

3.  **Set AWS Region:**
    *   **Action:** Log in to the AWS Management Console with your IAM user and ensure the region is set to **Sydney (ap-southeast-2)**.
    *   **Purpose:** All resources must be deployed in this region.
    *   **Verification:** Console shows "Sydney" as the selected region.


    4.  **Launch EC2 Instances:**
        *   **Action:** Follow **Section 1.3: Launch LMS Server (Linux)** and **Section 1.4: Launch Faculty Application Server (Windows)** in `Task3_Implementation_Guide.md`.
        *   **Details:** Launch two Linux EC2 instances (LMS) and two Windows EC2 instances (Faculty App) into the correct private subnets (`Yoobee-Private-Subnet-A/B`), associating them with the correct Security Groups and `YoobeeEC2AppRole`.
        *   **Verification:** All four EC2 instances are running in the correct AZs and subnets.
        *   **Documentation:** Take screenshots of the running EC2 instances (e.g., from the EC2 dashboard).

    5.  **Create RDS Database:**
        *   **Action:** Follow **Section 1.5: Create RDS Database** in `Task3_Implementation_Guide.md`.
        *   **Details:** Create an Amazon RDS PostgreSQL database instance with Multi-AZ deployment, ensuring it's in the correct VPC and associated with `RDS-SG`.
        *   **Verification:** The RDS PostgreSQL instance is created and running in Multi-AZ.
        *   **Documentation:** Take screenshots of the RDS instance summary and configuration (Multi-AZ, engine, encryption).
    6.  **Create and Secure S3 Bucket:**    *   **Action:** Follow **Section 2.1: Create S3 Bucket** and **Section 2.2: Apply S3 Bucket Policy** in `Task3_Implementation_Guide.md`.
    *   **Details:** Create the `yoobee-course-data-<unique-suffix>` S3 bucket in the Sydney region, enable default encryption, and apply the specified bucket policy.
    *   **Verification:** S3 bucket is created, encrypted, and has the correct policy applied.
    *   **Documentation:** Take screenshots of the S3 bucket properties (encryption) and bucket policy.

    7.  **Setup Elastic Load Balancer (ALB):**    *   **Action:** Follow **Section 3.1: Create Target Groups** and **Section 3.2: Create Application Load Balancer (ALB)** in `Task3_Implementation_Guide.md`.
    *   **Details:** Create target groups for LMS and Faculty App instances, configure health checks, and create the `yoobee-alb` in the public subnets, associating it with `ALB-SG` and the target groups.
    *   **Verification:** ALB is active, target groups are healthy, and traffic can be routed.
    *   **Documentation:** Take screenshots of the ALB summary, listeners, and target group health.

    8.  **Fill in `Task3_Report.md`:**    *   **Action:** Open `C:\Portfolio\LINZ_Cloud_CV\A3_result\Task3_Report.md`.
    *   **Purpose:** Document all practical implementation steps and evidence.
    *   **Details:** Replace all placeholder text and screenshots with the actual details and screenshots you collected during Phase 2. Ensure all sections (EC2 Configuration, S3 Bucket Security, ELB Setup) are thoroughly completed.
    *   **Verification:** `Task3_Report.md` is complete with all practical results and screenshots.

    9.  **Update `Task2_Report_and_Diagram_Code.md` Section 5:**    *   **Action:** Open `C:\Portfolio\LINZ_Cloud_CV\A2_result\diagram_script\Task2_Report_and_Diagram_Code.md`.
    *   **Purpose:** Add the high-level practical evidence for Task 2.
    *   **Details:** Replace `*(Placeholder for a high-level screenshot of the deployed VPC and subnets in the AWS Console)*` with the actual screenshot you took in Step 4 of Phase 2.
    *   **Verification:** Section 5 of `Task2_Report_and_Diagram_Code.md` now contains the high-level screenshot.

---

## Phase 3: Task 4 - Practical Implementation (Optimization & Security)

**Goal:** Implement security enhancements and monitoring, and develop a cost optimization strategy, documenting results in `Task4_Report.md`.

**Important:** Throughout this phase, **TAKE SCREENSHOTS** of every significant step and configuration. These are crucial for `Task4_Report.md`.

1.  **Open `Task4_Implementation_Guide.md`:**
    *   **Action:** Open `C:\Portfolio\LINZ_Cloud_CV\A2_result\diagram_script\Task4_Implementation_Guide.md`.
    *   **Purpose:** This is your step-by-step guide for optimization and security.

2.  **Implement Security Enhancements:**
    *   **Action:** Follow **Section 1: Security Enhancements Implementation** in `Task4_Implementation_Guide.md`.
    *   **Details:**
        *   Verify/configure Security Groups (already done in Task 3, but ensure they align with Task 4's best practices).
        *   Verify/configure IAM Roles (already done in Task 3, but ensure least privilege).
        *   Enforce MFA for IAM users (if not done in preparation).
        *   Configure Encryption in Transit (ALB HTTPS Listener) and Encryption at Rest (S3, RDS).
        *   Configure CloudTrail for API call monitoring and security event alerts.
    *   **Verification:** All security enhancements are implemented.
    *   **Documentation:** Take screenshots of MFA settings, encryption settings (S3, RDS), ALB listener (HTTPS), CloudTrail EventBridge rules, and SNS topic.

3.  **Implement CloudWatch Monitoring and Alerting:**
    *   **Action:** Follow **Section 2: CloudWatch Monitoring and Alerting Implementation** in `Task4_Implementation_Guide.md`.
    *   **Details:**
        *   Create a CloudWatch alarm for EC2 CPU utilization.
        *   Create a custom CloudWatch dashboard for key metrics (EC2 CPU, ALB Network I/O, RDS connections/CPU).
    *   **Verification:** CloudWatch alarm is active, and the dashboard displays relevant metrics.
    *   **Documentation:** Take screenshots of the CloudWatch alarm configuration and the custom dashboard.

4.  **Develop Cost Optimization Strategy (Theoretical Analysis):**
    *   **Action:** Follow **Section 3: Cost Optimization Strategy (Theoretical Analysis)** in `Task4_Implementation_Guide.md`.
    *   **Details:**
        *   Perform theoretical assessment of AWS Trusted Advisor recommendations for your architecture.
        *   Develop broader cost reduction strategies (Instance Scheduling, RIs/Savings Plans, S3 Lifecycle Policies, Auto Scaling).
        *   Use the AWS Pricing Calculator to compare On-Demand vs. Optimized costs.
    *   **Verification:** You have a well-defined cost optimization strategy.
    *   **Documentation:** Collect any relevant screenshots from the AWS Pricing Calculator (if used for theoretical comparison) and document your findings.

5.  **Fill in `Task4_Report.md`:**
    *   **Action:** Open `C:\Portfolio\LINZ_Cloud_CV\A4_result\Task4_Report.md`.
    *   **Purpose:** Document all practical implementation steps, theoretical analysis, and evidence for optimization and security.
    *   **Details:** Replace all placeholder text and screenshots with the actual details and screenshots you collected during Phase 3. Ensure all sections (Security Enhancements, CloudWatch Monitoring, Cost Optimization Strategy) are thoroughly completed.
    *   **Verification:** `Task4_Report.md` is complete with all practical results, theoretical analysis, and screenshots.

---

## Phase 4: Final Review & Submission Preparation

**Goal:** Ensure all deliverables are complete, accurate, and ready for submission.

1.  **Review All Reports:**
    *   **Action:** Read through `Task2_Report_and_Diagram_Code.md`, `Task3_Report.md`, and `Task4_Report.md` one last time.
    *   **Purpose:** Check for clarity, completeness, consistency, and adherence to all assignment requirements. Ensure all screenshots are present and correctly labeled.
    *   **Verification:** All reports are polished and error-free.

2.  **Generate PDF Deliverables:**
    *   **Action:** Convert `Task2_Report_and_Diagram_Code.md`, `Task3_Report.md`, and `Task4_Report.md` to PDF format.
    *   **Details:** If you are copying to MS Word first, ensure formatting is preserved before saving as PDF.
    *   **Purpose:** Meet the submission requirements for PDF format.
    *   **Verification:** You have three PDF files ready for submission.

3.  **Perform Cleanup:**
    *   **Action:** Follow **Section "Cleanup"** in `C:\Portfolio\LINZ_Cloud_CV\A2_result\diagram_script\Task3_Implementation_Guide.md` meticulously.
    *   **Purpose:** To delete all AWS resources created during this project and avoid unexpected costs. This is a critical step.
    *   **Verification:** All AWS resources related to this project have been successfully deleted from your AWS account.

---

This comprehensive plan should guide you through the entire project with minimal issues. Good luck!