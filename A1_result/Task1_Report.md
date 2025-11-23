### Report: A Recommended Cloud-Based Virtualization Solution for Yoobee College

**1. Introduction**

Yoobee College of Creative Innovation is undertaking a digital transformation to overcome the performance bottlenecks and security challenges of its current on-premises server infrastructure. This report outlines a theoretical evaluation for migrating the college's five key systems—two Learning Management System (LMS) servers, two Faculty Application servers, and one Student Database—to a server-based virtualization infrastructure on Amazon Web Services (AWS). The proposed solution is designed to meet the institution's primary goals of cost-effectiveness, scalability, security, and high availability, providing a robust foundation for future growth.

**2. Key Cloud Infrastructure Requirements**

A successful migration hinges on addressing four critical requirements that are fundamental to modern cloud architecture.

*   **Cost-Effectiveness:** The primary financial driver is the shift from a Capital Expenditure (CAPEX) model, which involves upfront hardware costs, to an Operational Expenditure (OPEX) model where services are paid for on an ongoing basis (Investopedia, n.d.). The infrastructure must leverage the cloud’s pay-as-you-go nature, ensuring the college pays only for the resources it consumes. This prevents over-provisioning and reduces the total cost of ownership by eliminating expenses related to power, cooling, and physical server maintenance.

*   **Scalability:** The infrastructure must dynamically adapt to fluctuating user loads. Student activity varies significantly throughout the academic year, with peaks during enrollment and exam periods. The system must automatically scale out (add resources) to handle increased demand and scale in (remove resources) during quiet periods to optimize costs, ensuring a consistently responsive experience for all users.

*   **Security:** Protecting sensitive student and academic data is paramount. The cloud solution must implement a multi-layered security strategy, leveraging AWS's advanced security services. This includes strict access controls, network isolation, data encryption at rest and in transit, and protection against common cyber threats like DDoS attacks, ensuring compliance with data protection best practices.

*   **High Availability:** Critical systems like the LMS and student database must be operational 24/7. The architecture must be designed to be fault-tolerant, eliminating single points of failure. By distributing resources across multiple physical locations (Availability Zones) and implementing automated failover mechanisms, the infrastructure can withstand server or even data center-level failures without service interruption.

**3. Comparison of AWS Pricing Models and Recommendation**

Choosing the correct pricing model is essential for achieving cost-effectiveness. A hybrid strategy, mixing different EC2 pricing models, is recommended for Yoobee College's specific workloads.

*   **Analysis of Models:** According to Amazon Web Services (n.d.-b), the primary pricing models offer trade-offs between commitment and cost:
    *   **On-Demand Instances:** Offer maximum flexibility with no commitment, but at the highest per-hour cost. Ideal for unpredictable workloads and initial development.
    *   **Reserved Instances (RIs):** Provide significant discounts (up to 72%) for a one- or three-year commitment. Best for stable, predictable workloads.
    *   **Spot Instances:** Offer the deepest discounts (up to 90%) on spare capacity but can be terminated by AWS with a two-minute warning, making them unsuitable for critical applications.

*   **Recommended Pricing Strategy:**
    *   **Student Database (1 System):** A **One-Year Reserved Instance** is recommended. This workload is predictable and critical, making it a perfect candidate for the cost savings of an RI.
    *   **Faculty Applications (2 Servers):** **One-Year Reserved Instances** are also suitable here, as their usage is likely stable throughout the business week. This guarantees capacity at a discounted rate.
    *   **Learning Management Systems (2 Servers):** A combination is best. Use **Reserved Instances** for the baseline, 24/7 capacity and supplement with **On-Demand Instances** managed by an Auto Scaling group. This allows the infrastructure to handle demand spikes during peak academic periods in the most cost-effective way.

**4. Improving Application Availability and Performance**

To implement the required scalability and high availability, two services are crucial: Elastic Load Balancing (ELB) and AWS Auto Scaling.

*   **Elastic Load Balancing (ELB):** An ELB acts as a traffic controller, automatically distributing incoming requests across multiple EC2 instances. This prevents any single server from being overloaded, which improves performance. Critically, it also provides high availability by performing health checks and automatically rerouting traffic away from any failed or unhealthy instances, thus preventing downtime (Amazon Web Services, n.d.-c).

*   **AWS Auto Scaling:** This service automates capacity management. It monitors metrics like CPU utilization and adds or removes instances based on predefined policies (Amazon Web Services, n.d.-a). For the LMS, it can automatically add servers to handle an influx of students during an exam and then remove them afterward to save money. It also contributes to high availability by ensuring a minimum number of healthy instances are always running, automatically replacing any that fail.

When used together, ELB and Auto Scaling create a self-healing, elastic system that adapts to demand and recovers from failures without manual intervention, forming the backbone of a modern cloud application.

**5. Justification and Conclusion**

The proposed AWS solution directly addresses the limitations of Yoobee College's on-premises infrastructure. By adopting a hybrid cloud strategy, the college can achieve its digital transformation goals effectively. The use of a mixed pricing model—combining Reserved Instances for predictable workloads and On-Demand instances for variable traffic—ensures maximum cost-effectiveness. The synergistic use of Elastic Load Balancing and Auto Scaling provides a robust framework for both high availability and dynamic scalability, guaranteeing that applications remain performant and accessible, even during peak loads or in the event of a server failure. Furthermore, leveraging AWS's comprehensive, managed security services will provide a stronger security posture than is feasible in the current on-premises environment.

In conclusion, migrating to this AWS infrastructure will provide Yoobee College with a secure, resilient, and cost-efficient platform that not only solves current challenges but also supports the institution's long-term growth and academic mission.

### References

Amazon Web Services. (n.d.-a). *AWS Auto Scaling*. Retrieved November 21, 2025, from https://aws.amazon.com/autoscaling/

Amazon Web Services. (n.d.-b). *Amazon EC2 pricing*. Retrieved November 21, 2025, from https://aws.amazon.com/ec2/pricing/

Amazon Web Services. (n.d.-c). *Elastic Load Balancing*. Retrieved November 21, 2025, from https://aws.amazon.com/elasticloadbalancing/

Investopedia. (n.d.). *Capital expenditures (CAPEX) vs. operating expenditures (OPEX)*. Retrieved November 21, 2025, from https://www.investopedia.com/ask/answers/041015/what-difference-between-capital-expenditures-capex-and-operating-expenditures-opex.asp