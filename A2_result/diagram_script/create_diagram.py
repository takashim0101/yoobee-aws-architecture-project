# Deployment Region: Asia Pacific (Sydney) - ap-southeast-2

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.network import ELB, NATGateway, InternetGateway, Endpoint
from diagrams.aws.database import RDS
from diagrams.aws.storage import S3
from diagrams.aws.general import User

graph_attr = {
    "fontsize": "12",
    "nodesep": "0.8",
    "ranksep": "1.5",
    "labelloc": "b",
}

with Diagram("Yoobee College AWS Architecture", show=True, direction="TB", graph_attr=graph_attr):

    # Actors
    internet_user = User("Student/Faculty\nInternet User")
    it_admin = User("IT Admin\n(SSM Session Manager)")

    with Cluster("AWS Region"):
        s3 = S3("S3 Bucket\nCourse Data")

        with Cluster("VPC: 10.0.0.0/16"):
            igw = InternetGateway("Internet Gateway")
            alb = ELB("Application Load Balancer\n(SG: ALB-SG)")
            vpc_endpoint = Endpoint("VPC Gateway Endpoint\nfor S3")

            with Cluster("Availability Zone ap-southeast-2a"):
                with Cluster("Public Subnet A\n10.0.1.0/24\nNACL: Public-NACL"):
                    nat_a = NATGateway("NAT Gateway A") # Security managed by NACLs and Route Tables

                with Cluster("Private Subnet A\n10.0.2.0/24\nNACL: Private-NACL"):
                    ec2_lms_a = EC2("LMS Server A\nLinux EC2\n(SG: LMS-SG)")
                    ec2_faculty_a = EC2("Faculty App A\nWindows EC2\n(SG: Faculty-SG)")
                    rds_master = RDS("RDS Master\nPostgreSQL\n(SG: RDS-SG)")

            with Cluster("Availability Zone ap-southeast-2b"):
                with Cluster("Public Subnet B\n10.0.3.0/24\nNACL: Public-NACL"):
                    # Placeholder for ALB redundancy
                    pass
                with Cluster("Private Subnet B\n10.0.4.0/24\nNACL: Private-NACL"):
                    ec2_lms_b = EC2("LMS Server B\nStandby\n(SG: LMS-SG)")
                    ec2_faculty_b = EC2("Faculty App B\nStandby\n(SG: Faculty-SG)")
                    rds_standby = RDS("RDS Standby\nReplica\nPostgreSQL\n(SG: RDS-SG)")

            # User Traffic Flow
            internet_user >> igw >> alb
            alb >> [ec2_lms_a, ec2_lms_b]
            alb >> [ec2_faculty_a, ec2_faculty_b]

            # Admin Traffic Flow (via SSM, not a direct network path in the diagram)
            it_admin >> Edge(label="SSM Session Manager") >> ec2_lms_a
            it_admin >> Edge(label="SSM Session Manager") >> ec2_faculty_a
            it_admin >> Edge(label="SSM Session Manager") >> rds_master


            # Internal & Outbound Traffic
            [ec2_lms_a, ec2_faculty_a, ec2_lms_b, ec2_faculty_b] >> rds_master
            
            # S3 Access via VPC Endpoint
            ec2_instances = [ec2_lms_a, ec2_faculty_a, ec2_lms_b, ec2_faculty_b]
            ec2_instances >> Edge(label="IAM Role via Route Table") >> vpc_endpoint
            vpc_endpoint >> Edge(label="Private Link") >> s3
            
            # Outbound for OS Updates
            ec2_lms_a >> Edge(label="OS Updates") >> nat_a
            ec2_faculty_a >> Edge(label="OS Updates") >> nat_a
            nat_a >> igw

            ec2_lms_b >> Edge(label="OS Updates") >> nat_a # Assuming single NAT for simplicity
            ec2_faculty_b >> Edge(label="OS Updates") >> nat_a

            # DB Replication
            rds_master >> Edge(label="Sync Replication") >> rds_standby
