# Code Ocean VPC System Requirements

## Overview

This document provides a comprehensive overview of the system requirements and infrastructure components defined in the Code Ocean VPC CloudFormation template. It serves as a reference for understanding the deployment architecture, resource dependencies, and configuration parameters required for the Code Ocean VPC system.

The full resource configuration, including all properties, dependencies, and conditions, is available in the CloudFormation template file. This document provides a high-level summary with direct links to the complete definitions.

### Document Structure
- **System Overview**: High-level architecture and components
- **Parameters**: Configurable values that customize the deployment
- **Resources**: AWS infrastructure resources

All parameters and resources are linked to their exact line numbers in the template file for easy reference to the complete configuration

**Template Version:** v3.7.0  
**Commit:** 60cc19ecdfb0b7ebccb25677b6d38dfd518a8546

## System Overview

### VPC Network

If you choose to install Code Ocean into its own dedicated AWS VPC the CloudFormation template will provision a new VPC across two availability zones with public and private subnets in your selected AWS region. The availability zones and CIDR blocks for VPC and subnets are configurable.

If you choose to install Code Ocean into an existing AWS VPC you can configure the CloudFormation template with the two availability zones and the private and public subnets to deploy to. Public subnets are required if you choose an internet-facing deployment.

### EC2

Code Ocean uses an HTTPS-only AWS application load balancer (ALB) to expose the system to users and to allow access to its internal Git server and Docker registry. The ALB can be internet-facing or internal for deployments behind a VPN.

The system manages two types of EC2 instances:

* Services - Single machine in an auto-scale group attached to an internal load balancer that runs all internal system services.
* Workers - Two auto-scale groups of worker machines where the actual users computations are running. One auto scale group for GPU based computations and the other for general non-GPU computations. When you run a Compute Capsule within Code Ocean it gets scheduled to run on one of the worker machines. The system will automatically provision more worker machines (scale out) as the load increases and deprovision worker machines (scale in) as the load decreases.

The deployment is configured with security groups to control network flow between parts of the system and IAM instance roles for each instance type to limit access to AWS resources.

Shell access to the EC2 instances is available through AWS SSM Session Manager.

### DNS

The system is hosted on a subdomain managed with an AWS Route53 hosted zone. For internet-facing Code Ocean deployments the hosted zone is public, and you will need to delegate to it from your parent or root domain. For internal deployments behind a VPN the Route53 hosted zone will be private.

The system also uses an internal Route53 private hosted zone for internal service discovery.

### Storage

There are three types of storage medium used:

*   EBS data volume:

    Where most of the internal persistent system data is stored. For example, a Compute Capsule in the system is backed by a git repo which is persisted in this storage type.

    The volume is configured with encryption at rest.
*   S3 buckets:

    Used to store input (datasets) and output (results) data of Compute Capsules, as well as the internal docker registry storage and other system persistent storage buckets.

    All S3 buckets are private, with server-side encryption, and access logs enabled by default. S3 bucket versioning is enabled on buckets that store persistent data.
*   EFS:

    The Datasets Cache EFS provides a computation (Compute Capsule) running on a worker instance machine with fast access to datasets. Once a dataset is available it is cached on EFS which gets mounted to the worker instance machines.

    The Scratch EFS provides a dedicated folder per compute capsule for intermediate data that persists through the lifetime of the capsule.

    Encryption at rest is enabled by default on all EFS storage.

### Monitoring

Code Ocean natively reports all metrics to AWS CloudWatch. In addition to metrics from AWS services that Code Ocean uses, such as CPU utilization from EC2 and disk IO metrics from EBS, the system also reports custom metrics to a custom `CodeOcean` CloudWatch metrics namespace. For example, this includes Code Ocean worker machine utilization, and memory and disk utilization on all machines.

The deployment provisions AWS CloudWatch alarms and an SNS topic to easily get notifications on system issues.

Code Ocean pushes all OS and application logs to CloudWatch Logs. This log data can help with troubleshooting system issue.

## Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| [pVpcId](codeocean.template.yaml#L295) | String |  | Existing VPC ID. If not specified, a VPC will be created. |
| [pAvailabilityZone1](codeocean.template.yaml#L299) | String |  | Availability Zone 1 for the existing VPC |
| [pPrivateSubnet1Id](codeocean.template.yaml#L303) | String |  | Subnet ID for private subnet 1 located in Availability Zone 1 in Existing VPC |
| [pPublicSubnet1Id](codeocean.template.yaml#L307) | String |  | Subnet ID for public subnet 1 located in Availability Zone 1 in Existing VPC |
| [pAvailabilityZone2](codeocean.template.yaml#L311) | String |  | Availability Zone 2 for the existing VPC |
| [pPrivateSubnet2Id](codeocean.template.yaml#L315) | String |  | Subnet ID for private subnet 2 located in Availability Zone 2 in Existing VPC |
| [pPublicSubnet2Id](codeocean.template.yaml#L319) | String |  | Subnet ID for public subnet 2 located in Availability Zone 2 in Existing VPC |
| [pAvailabilityZone3](codeocean.template.yaml#L323) | String |  | Availability Zone 3 for the existing VPC |
| [pPrivateSubnet3Id](codeocean.template.yaml#L327) | String |  | Subnet ID for private subnet 3 located in Availability Zone 3 in Existing VPC |
| [pPublicSubnet3Id](codeocean.template.yaml#L331) | String |  | Subnet ID for public subnet 3 located in Availability Zone 3 in Existing VPC |
| [pAvailabilityZone4](codeocean.template.yaml#L335) | String |  | Availability Zone 4 for the existing VPC |
| [pPrivateSubnet4Id](codeocean.template.yaml#L339) | String |  | Subnet ID for private subnet 4 located in Availability Zone 4 in Existing VPC |
| [pPublicSubnet4Id](codeocean.template.yaml#L343) | String |  | Subnet ID for public subnet 4 located in Availability Zone 4 in Existing VPC |
| [pAvailabilityZone5](codeocean.template.yaml#L347) | String |  | Availability Zone 5 for the existing VPC |
| [pPrivateSubnet5Id](codeocean.template.yaml#L351) | String |  | Subnet ID for private subnet 5 located in Availability Zone 5 in Existing VPC |
| [pPublicSubnet5Id](codeocean.template.yaml#L355) | String |  | Subnet ID for public subnet 5 located in Availability Zone 5 in Existing VPC |
| [pAvailabilityZone6](codeocean.template.yaml#L359) | String |  | Availability Zone 6 for the existing VPC |
| [pPrivateSubnet6Id](codeocean.template.yaml#L363) | String |  | Subnet ID for private subnet 6 located in Availability Zone 6 in Existing VPC |
| [pPublicSubnet6Id](codeocean.template.yaml#L367) | String |  | Subnet ID for public subnet 6 located in Availability Zone 6 in Existing VPC |
| [pVpcCIDR](codeocean.template.yaml#L371) | String | `10.0.0.0/16` | CIDR block for the VPC |
| [pNewVpcAvailabilityZone1](codeocean.template.yaml#L377) | String |  | Availability Zone 1 for the new VPC |
| [pPrivateSubnet1CIDR](codeocean.template.yaml#L381) | String | `10.0.0.0/20` | CIDR block for private subnet 1 located in Availability Zone 1 |
| [pPublicSubnet1CIDR](codeocean.template.yaml#L387) | String | `10.0.96.0/20` | CIDR block for public subnet 1 located in Availability Zone 1 |
| [pNewVpcAvailabilityZone2](codeocean.template.yaml#L393) | String |  | Availability Zone 2 for the new VPC |
| [pPrivateSubnet2CIDR](codeocean.template.yaml#L397) | String | `10.0.16.0/20` | CIDR block for private subnet 2 located in Availability Zone 2 |
| [pPublicSubnet2CIDR](codeocean.template.yaml#L403) | String | `10.0.112.0/20` | CIDR block for public subnet 2 located in Availability Zone 2 |
| [pNewVpcAvailabilityZone3](codeocean.template.yaml#L409) | String |  | Availability Zone 3 for the new VPC |
| [pPrivateSubnet3CIDR](codeocean.template.yaml#L413) | String | `10.0.32.0/20` | CIDR block for private subnet 3 located in Availability Zone 3 |
| [pPublicSubnet3CIDR](codeocean.template.yaml#L419) | String | `10.0.128.0/20` | CIDR block for public subnet 3 located in Availability Zone 3 |
| [pNewVpcAvailabilityZone4](codeocean.template.yaml#L425) | String |  | Availability Zone 4 for the new VPC |
| [pPrivateSubnet4CIDR](codeocean.template.yaml#L429) | String | `10.0.48.0/20` | CIDR block for private subnet 4 located in Availability Zone 4 |
| [pPublicSubnet4CIDR](codeocean.template.yaml#L435) | String | `10.0.144.0/20` | CIDR block for public subnet 4 located in Availability Zone 4 |
| [pNewVpcAvailabilityZone5](codeocean.template.yaml#L441) | String |  | Availability Zone 5 for the new VPC |
| [pPrivateSubnet5CIDR](codeocean.template.yaml#L445) | String | `10.0.64.0/20` | CIDR block for private subnet 5 located in Availability Zone 5 |
| [pPublicSubnet5CIDR](codeocean.template.yaml#L451) | String | `10.0.160.0/20` | CIDR block for public subnet 5 located in Availability Zone 5 |
| [pNewVpcAvailabilityZone6](codeocean.template.yaml#L457) | String |  | Availability Zone 6 for the new VPC |
| [pPrivateSubnet6CIDR](codeocean.template.yaml#L461) | String | `10.0.80.0/20` | CIDR block for private subnet 6 located in Availability Zone 6 |
| [pPublicSubnet6CIDR](codeocean.template.yaml#L467) | String | `10.0.176.0/20` | CIDR block for public subnet 6 located in Availability Zone 6 |
| [pDnsName](codeocean.template.yaml#L473) | String | `codeocean` | Code Ocean application subdomain |
| [pDnsRootDomain](codeocean.template.yaml#L477) | String |  | Root domain name (e.g. acmecorp.com) |
| [pHostedZoneId](codeocean.template.yaml#L480) | String |  | (Optional) Existing Route 53 hosted zone ID |
| [pCertificateArn](codeocean.template.yaml#L484) | String |  | (Optional) Existing ACM certificate ARN |
| [pPrivateCA](codeocean.template.yaml#L488) | String | `false` | Is the certificate signed by a private certificate authority? |
| [pCustomAmi](codeocean.template.yaml#L495) | String |  | (Optional) Custom AMI ID to use for services, workers, and batch instances |
| [pDeploymentType](codeocean.template.yaml#L500) | String | `internet-facing` | Make the deployment internet addressable (default) or require a VPN to connect |
| [pServicesInstanceType](codeocean.template.yaml#L507) | String | `m7i.large` | EC2 instance type for services machine. |
| [pWorkerInstanceType](codeocean.template.yaml#L517) | String | `r5d.4xlarge` | EC2 instance type for general purpose workers. Instance type must be from the 'r5d' family. |
| [pGPUWorkerInstanceType](codeocean.template.yaml#L523) | String | `g4dn.4xlarge` | EC2 instance type for GPU Workers. Instance type must belong to the P (3\|3dn\|4d\|5) or G (4ad\|4dn\|5\|6\|r6) families. |
| [pWorkersAsgMaxSize](codeocean.template.yaml#L529) | Number | `10` | Maximum number of running worker instances |
| [pGpuWorkersAsgMaxSize](codeocean.template.yaml#L533) | Number | `10` | Maximum number of running GPU worker instances |
| [pMinWorkersAvailable](codeocean.template.yaml#L537) | Number | `1` | Minimum number of worker instances the system keeps in its auto scaling warm pool that are ready to receive computations |
| [pMinGpuWorkersAvailable](codeocean.template.yaml#L541) | Number | `1` | Minimum number of GPU worker instances the system keeps in its auto scaling warm pool that are ready to receive computations |
| [pAutoScalingIdleTimeout](codeocean.template.yaml#L545) | Number | `60` | Number of minutes before system scales-in idle workers |
| [pRdsInstanceType](codeocean.template.yaml#L549) | String | `db.t4g.small` | RDS instance type for analytics |
| [pRdsAllocatedStorage](codeocean.template.yaml#L556) | Number | `20` | RDS instance allocated storage |
| [pRdsMaxAllocatedStorage](codeocean.template.yaml#L561) | Number | `100` | RDS instance maximum allocated storage |
| [pAssumableRoles](codeocean.template.yaml#L566) | CommaDelimitedList |  |  |
| [pBatchMaxvCpus](codeocean.template.yaml#L569) | Number | `256` | Maximum number of vCPUs that can be used by all batch instances |
| [BatchInstanceTypes](codeocean.template.yaml#L573) | CommaDelimitedList | `c7i,m7i,r7i,optimal` | Comma-delimited list of batch instance types for pipelines |
| [BatcGpuInstanceTypes](codeocean.template.yaml#L577) | CommaDelimitedList | `g4dn` | Comma-delimited list of batch instance types for GPU pipelines |
| [pBatchVolumeSize](codeocean.template.yaml#L581) | Number | `300` | Volume size, in gigabytes, of the Docker's EBS volumes for batch instances |
| [pBatchVolumeIops](codeocean.template.yaml#L587) | Number | `5000` | Volume IOPS, number of I/O operations per second, of the Docker's EBS volumes for batch instances |
| [pBatchVolumeThroughput](codeocean.template.yaml#L593) | Number | `500` | Volume Throughput, in MiB/s, of the Docker's EBS volumes for batch instances |
| [pBackupSchedule](codeocean.template.yaml#L599) | String | `cron(0 4 ? * * *)` | Backup schedule CRON expression |
| [pBackupRetentionPeriod](codeocean.template.yaml#L603) | Number | `14` | Backup retention period in days |
| [pDestinationBackupVaultArn](codeocean.template.yaml#L608) | String |  | Copy backup snapshots to a destination backup vault |
| [pDestinationBackupVaultCrossRegion](codeocean.template.yaml#L612) | String | `no` | Is the destination backup vault in a different region? |
| [pDestinationBackupRetentionPeriod](codeocean.template.yaml#L619) | Number | `14` | Backup retention period in days for snapshots copied to the destination backup vault |
| [pDestinationBackupS3KmsKey](codeocean.template.yaml#L624) | String |  | AWS KMS key ARN to use for encrypting S3 object backup replicas |
| [pDestinationBackupS3StorageClass](codeocean.template.yaml#L628) | String | `GLACIER_IR` | AWS S3 storage class for backup object replicas |
| [pDestinationBackupCapsulesBucketArn](codeocean.template.yaml#L635) | String |  | Destination backup S3 capsules bucket ARN |
| [pDestinationBackupDatasetsBucketArn](codeocean.template.yaml#L639) | String |  | Destination backup S3 datasets bucket ARN |
| [pDestinationBackupDockerRegistryBucketArn](codeocean.template.yaml#L643) | String |  | Destination backup S3 docker registry bucket ARN |
| [pDestinationBackupInputFilesBucketArn](codeocean.template.yaml#L647) | String |  | Destination backup S3 input files bucket ARN |
| [pDestinationBackupLicensesBucketArn](codeocean.template.yaml#L651) | String |  | Destination backup S3 licenses bucket ARN |
| [pDestinationBackupMLflowBucketArn](codeocean.template.yaml#L655) | String |  | Destination backup S3 MLflow bucket ARN |
| [pDestinationBackupPackagesBucketArn](codeocean.template.yaml#L659) | String |  | Destination backup S3 packages bucket ARN |
| [pDestinationBackupPublicBucketArn](codeocean.template.yaml#L663) | String |  | Destination backup S3 public bucket ARN |
| [pDestinationBackupResultsBucketArn](codeocean.template.yaml#L667) | String |  | Destination backup S3 results bucket ARN |
| [pRestoreSourceAccountId](codeocean.template.yaml#L671) | String |  | (Optional) AWS Account ID to restore backups from |

## Resources

| Logical Name | Resource Type | Description |
| ------------ | ------------- | ----------- |
| [LogGroupInstances](codeocean.template.yaml#L776) | AWS::Logs::LogGroup | CloudWatch log group for EC2 instances |
| [LogGroupLambda](codeocean.template.yaml#L792) | AWS::Logs::LogGroup | CloudWatch log group for Lambda functions |
| [LogGroupPipelines](codeocean.template.yaml#L808) | AWS::Logs::LogGroup | CloudWatch log group for pipelines |
| [LogGroupServices](codeocean.template.yaml#L824) | AWS::Logs::LogGroup | CloudWatch log group for services |
| [LogGroupWorkers](codeocean.template.yaml#L840) | AWS::Logs::LogGroup | CloudWatch log group for workers |
| [Vpc](codeocean.template.yaml#L856) | AWS::EC2::VPC | Virtual Private Cloud network |
| [InternetGateway](codeocean.template.yaml#L875) | AWS::EC2::InternetGateway | Internet gateway for public access |
| [VpcGatewayAttachment](codeocean.template.yaml#L889) | AWS::EC2::VPCGatewayAttachment |  |
| [VpcGatewayAttachmentWaitHandle](codeocean.template.yaml#L897) | AWS::CloudFormation::WaitConditionHandle | Wait condition handle |
| [WaitHandle](codeocean.template.yaml#L902) | AWS::CloudFormation::WaitConditionHandle | Wait condition handle |
| [VpcGatewayAttachmentWaitCondition](codeocean.template.yaml#L904) | AWS::CloudFormation::WaitCondition | Wait condition for stack coordination |
| [PublicSubnet1](codeocean.template.yaml#L914) | AWS::EC2::Subnet | Public subnet for internet-accessible resources |
| [PublicSubnet1RouteTable](codeocean.template.yaml#L935) | AWS::EC2::RouteTable | Public subnet for internet-accessible resources |
| [PublicSubnet1RouteTableAssociation](codeocean.template.yaml#L951) | AWS::EC2::SubnetRouteTableAssociation | Public subnet for internet-accessible resources |
| [PublicSubnet1DefaultRoute](codeocean.template.yaml#L959) | AWS::EC2::Route | Public subnet for internet-accessible resources |
| [PublicSubnet1EIP](codeocean.template.yaml#L970) | AWS::EC2::EIP | Public subnet for internet-accessible resources |
| [PublicSubnet1NATGateway](codeocean.template.yaml#L979) | AWS::EC2::NatGateway | Public subnet for internet-accessible resources |
| [PrivateSubnet1](codeocean.template.yaml#L999) | AWS::EC2::Subnet | Private subnet for internal resources |
| [PrivateSubnet1RouteTable](codeocean.template.yaml#L1019) | AWS::EC2::RouteTable | Private subnet for internal resources |
| [PrivateSubnet1RouteTableAssociation](codeocean.template.yaml#L1035) | AWS::EC2::SubnetRouteTableAssociation | Private subnet for internal resources |
| [PrivateSubnet1DefaultRoute](codeocean.template.yaml#L1043) | AWS::EC2::Route | Private subnet for internal resources |
| [PublicSubnet2](codeocean.template.yaml#L1052) | AWS::EC2::Subnet | Public subnet for internet-accessible resources |
| [PublicSubnet2RouteTable](codeocean.template.yaml#L1073) | AWS::EC2::RouteTable | Public subnet for internet-accessible resources |
| [PublicSubnet2RouteTableAssociation](codeocean.template.yaml#L1089) | AWS::EC2::SubnetRouteTableAssociation | Public subnet for internet-accessible resources |
| [PublicSubnet2DefaultRoute](codeocean.template.yaml#L1097) | AWS::EC2::Route | Public subnet for internet-accessible resources |
| [PublicSubnet2EIP](codeocean.template.yaml#L1108) | AWS::EC2::EIP | Public subnet for internet-accessible resources |
| [PublicSubnet2NATGateway](codeocean.template.yaml#L1117) | AWS::EC2::NatGateway | Public subnet for internet-accessible resources |
| [PrivateSubnet2](codeocean.template.yaml#L1137) | AWS::EC2::Subnet | Private subnet for internal resources |
| [PrivateSubnet2RouteTable](codeocean.template.yaml#L1157) | AWS::EC2::RouteTable | Private subnet for internal resources |
| [PrivateSubnet2RouteTableAssociation](codeocean.template.yaml#L1173) | AWS::EC2::SubnetRouteTableAssociation | Private subnet for internal resources |
| [PrivateSubnet2DefaultRoute](codeocean.template.yaml#L1181) | AWS::EC2::Route | Private subnet for internal resources |
| [PublicSubnet3](codeocean.template.yaml#L1190) | AWS::EC2::Subnet | Public subnet for internet-accessible resources |
| [PublicSubnet3RouteTable](codeocean.template.yaml#L1211) | AWS::EC2::RouteTable | Public subnet for internet-accessible resources |
| [PublicSubnet3RouteTableAssociation](codeocean.template.yaml#L1227) | AWS::EC2::SubnetRouteTableAssociation | Public subnet for internet-accessible resources |
| [PublicSubnet3DefaultRoute](codeocean.template.yaml#L1235) | AWS::EC2::Route | Public subnet for internet-accessible resources |
| [PublicSubnet3EIP](codeocean.template.yaml#L1246) | AWS::EC2::EIP | Public subnet for internet-accessible resources |
| [PublicSubnet3NATGateway](codeocean.template.yaml#L1255) | AWS::EC2::NatGateway | Public subnet for internet-accessible resources |
| [PrivateSubnet3](codeocean.template.yaml#L1275) | AWS::EC2::Subnet | Private subnet for internal resources |
| [PrivateSubnet3RouteTable](codeocean.template.yaml#L1295) | AWS::EC2::RouteTable | Private subnet for internal resources |
| [PrivateSubnet3RouteTableAssociation](codeocean.template.yaml#L1311) | AWS::EC2::SubnetRouteTableAssociation | Private subnet for internal resources |
| [PrivateSubnet3DefaultRoute](codeocean.template.yaml#L1319) | AWS::EC2::Route | Private subnet for internal resources |
| [PublicSubnet4](codeocean.template.yaml#L1328) | AWS::EC2::Subnet | Public subnet for internet-accessible resources |
| [PublicSubnet4RouteTable](codeocean.template.yaml#L1349) | AWS::EC2::RouteTable | Public subnet for internet-accessible resources |
| [PublicSubnet4RouteTableAssociation](codeocean.template.yaml#L1365) | AWS::EC2::SubnetRouteTableAssociation | Public subnet for internet-accessible resources |
| [PublicSubnet4DefaultRoute](codeocean.template.yaml#L1373) | AWS::EC2::Route | Public subnet for internet-accessible resources |
| [PublicSubnet4EIP](codeocean.template.yaml#L1384) | AWS::EC2::EIP | Public subnet for internet-accessible resources |
| [PublicSubnet4NATGateway](codeocean.template.yaml#L1393) | AWS::EC2::NatGateway | Public subnet for internet-accessible resources |
| [PrivateSubnet4](codeocean.template.yaml#L1413) | AWS::EC2::Subnet | Private subnet for internal resources |
| [PrivateSubnet4RouteTable](codeocean.template.yaml#L1433) | AWS::EC2::RouteTable | Private subnet for internal resources |
| [PrivateSubnet4RouteTableAssociation](codeocean.template.yaml#L1449) | AWS::EC2::SubnetRouteTableAssociation | Private subnet for internal resources |
| [PrivateSubnet4DefaultRoute](codeocean.template.yaml#L1457) | AWS::EC2::Route | Private subnet for internal resources |
| [PublicSubnet5](codeocean.template.yaml#L1466) | AWS::EC2::Subnet | Public subnet for internet-accessible resources |
| [PublicSubnet5RouteTable](codeocean.template.yaml#L1487) | AWS::EC2::RouteTable | Public subnet for internet-accessible resources |
| [PublicSubnet5RouteTableAssociation](codeocean.template.yaml#L1503) | AWS::EC2::SubnetRouteTableAssociation | Public subnet for internet-accessible resources |
| [PublicSubnet5DefaultRoute](codeocean.template.yaml#L1511) | AWS::EC2::Route | Public subnet for internet-accessible resources |
| [PublicSubnet5EIP](codeocean.template.yaml#L1522) | AWS::EC2::EIP | Public subnet for internet-accessible resources |
| [PublicSubnet5NATGateway](codeocean.template.yaml#L1531) | AWS::EC2::NatGateway | Public subnet for internet-accessible resources |
| [PrivateSubnet5](codeocean.template.yaml#L1551) | AWS::EC2::Subnet | Private subnet for internal resources |
| [PrivateSubnet5RouteTable](codeocean.template.yaml#L1571) | AWS::EC2::RouteTable | Private subnet for internal resources |
| [PrivateSubnet5RouteTableAssociation](codeocean.template.yaml#L1587) | AWS::EC2::SubnetRouteTableAssociation | Private subnet for internal resources |
| [PrivateSubnet5DefaultRoute](codeocean.template.yaml#L1595) | AWS::EC2::Route | Private subnet for internal resources |
| [PublicSubnet6](codeocean.template.yaml#L1604) | AWS::EC2::Subnet | Public subnet for internet-accessible resources |
| [PublicSubnet6RouteTable](codeocean.template.yaml#L1625) | AWS::EC2::RouteTable | Public subnet for internet-accessible resources |
| [PublicSubnet6RouteTableAssociation](codeocean.template.yaml#L1641) | AWS::EC2::SubnetRouteTableAssociation | Public subnet for internet-accessible resources |
| [PublicSubnet6DefaultRoute](codeocean.template.yaml#L1649) | AWS::EC2::Route | Public subnet for internet-accessible resources |
| [PublicSubnet6EIP](codeocean.template.yaml#L1660) | AWS::EC2::EIP | Public subnet for internet-accessible resources |
| [PublicSubnet6NATGateway](codeocean.template.yaml#L1669) | AWS::EC2::NatGateway | Public subnet for internet-accessible resources |
| [PrivateSubnet6](codeocean.template.yaml#L1689) | AWS::EC2::Subnet | Private subnet for internal resources |
| [PrivateSubnet6RouteTable](codeocean.template.yaml#L1709) | AWS::EC2::RouteTable | Private subnet for internal resources |
| [PrivateSubnet6RouteTableAssociation](codeocean.template.yaml#L1725) | AWS::EC2::SubnetRouteTableAssociation | Private subnet for internal resources |
| [PrivateSubnet6DefaultRoute](codeocean.template.yaml#L1733) | AWS::EC2::Route | Private subnet for internal resources |
| [S3VpcEndpoint](codeocean.template.yaml#L1742) | AWS::EC2::VPCEndpoint |  |
| [S3AccessLogsBucket](codeocean.template.yaml#L1784) | AWS::S3::Bucket |  |
| [S3AccessLogsBucketPolicy](codeocean.template.yaml#L1811) | AWS::S3::BucketPolicy |  |
| [S3BatchBucket](codeocean.template.yaml#L1873) | AWS::S3::Bucket |  |
| [S3BatchBucketPolicy](codeocean.template.yaml#L1904) | AWS::S3::BucketPolicy |  |
| [S3CapsulesBucket](codeocean.template.yaml#L1930) | AWS::S3::Bucket |  |
| [S3CapsulesBucketPolicy](codeocean.template.yaml#L2003) | AWS::S3::BucketPolicy |  |
| [S3DatasetsBucket](codeocean.template.yaml#L2058) | AWS::S3::Bucket |  |
| [S3DatasetsBucketPolicy](codeocean.template.yaml#L2131) | AWS::S3::BucketPolicy |  |
| [S3DatasetsInputBucket](codeocean.template.yaml#L2186) | AWS::S3::Bucket |  |
| [S3DatasetsInputBucketPolicy](codeocean.template.yaml#L2214) | AWS::S3::BucketPolicy |  |
| [S3InputFilesBucket](codeocean.template.yaml#L2240) | AWS::S3::Bucket |  |
| [S3InputFilesBucketPolicy](codeocean.template.yaml#L2313) | AWS::S3::BucketPolicy |  |
| [S3LicensesBucket](codeocean.template.yaml#L2368) | AWS::S3::Bucket |  |
| [S3LicensesBucketPolicy](codeocean.template.yaml#L2431) | AWS::S3::BucketPolicy |  |
| [S3MLflowBucket](codeocean.template.yaml#L2486) | AWS::S3::Bucket |  |
| [S3MLflowBucketPolicy](codeocean.template.yaml#L2559) | AWS::S3::BucketPolicy |  |
| [S3PackagesBucket](codeocean.template.yaml#L2614) | AWS::S3::Bucket |  |
| [S3PackagesBucketPolicy](codeocean.template.yaml#L2687) | AWS::S3::BucketPolicy |  |
| [S3PublicBucket](codeocean.template.yaml#L2742) | AWS::S3::Bucket |  |
| [S3PublicBucketPolicy](codeocean.template.yaml#L2805) | AWS::S3::BucketPolicy |  |
| [S3DockerRegistryBucket](codeocean.template.yaml#L2860) | AWS::S3::Bucket |  |
| [S3DockerRegistryBucketPolicy](codeocean.template.yaml#L2933) | AWS::S3::BucketPolicy |  |
| [S3ResultsBucket](codeocean.template.yaml#L2988) | AWS::S3::Bucket |  |
| [S3ResultsBucketPolicy](codeocean.template.yaml#L3061) | AWS::S3::BucketPolicy |  |
| [S3ScratchBucket](codeocean.template.yaml#L3116) | AWS::S3::Bucket |  |
| [S3ScratchBucketPolicy](codeocean.template.yaml#L3152) | AWS::S3::BucketPolicy |  |
| [S3TempBucket](codeocean.template.yaml#L3178) | AWS::S3::Bucket |  |
| [S3TempBucketPolicy](codeocean.template.yaml#L3209) | AWS::S3::BucketPolicy |  |
| [S3BackupRole](codeocean.template.yaml#L3235) | AWS::IAM::Role | Provides AWS S3 permissions to backup buckets. |
| [S3BackupReplicationPolicy](codeocean.template.yaml#L3255) | AWS::IAM::Policy |  |
| [OpenSearchSecurityGroup](codeocean.template.yaml#L3410) | AWS::EC2::SecurityGroup | Security group for access control |
| [OpenSearchSecurityGroupEgressDefault](codeocean.template.yaml#L3423) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [OpenSearchSecurityGroupIngressJobs](codeocean.template.yaml#L3431) | AWS::EC2::SecurityGroupIngress | es from jobs |
| [OpenSearchSecurityGroupIngressServices](codeocean.template.yaml#L3442) | AWS::EC2::SecurityGroupIngress | es from services |
| [OpenSearchDomain](codeocean.template.yaml#L3453) | AWS::OpenSearchService::Domain |  |
| [DatasetsEfs](codeocean.template.yaml#L3495) | AWS::EFS::FileSystem |  |
| [DatasetsEfsSecurityGroup](codeocean.template.yaml#L3534) | AWS::EC2::SecurityGroup | Security group for access control |
| [DatasetsEfsSecurityGroupEgressDefault](codeocean.template.yaml#L3547) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [DatasetsEfsSecurityGroupIngressJobs](codeocean.template.yaml#L3555) | AWS::EC2::SecurityGroupIngress | efs from jobs |
| [DatasetsEfsSecurityGroupIngressBatch](codeocean.template.yaml#L3566) | AWS::EC2::SecurityGroupIngress | efs from batch |
| [DatasetsEfsSecurityGroupIngressServices](codeocean.template.yaml#L3577) | AWS::EC2::SecurityGroupIngress | efs from services |
| [DatasetsEfsSecurityGroupIngressWorkers](codeocean.template.yaml#L3588) | AWS::EC2::SecurityGroupIngress | efs from workers |
| [DatasetsEfsMountTarget1](codeocean.template.yaml#L3599) | AWS::EFS::MountTarget |  |
| [DatasetsEfsMountTarget2](codeocean.template.yaml#L3611) | AWS::EFS::MountTarget |  |
| [DatasetsEfsMountTarget3](codeocean.template.yaml#L3623) | AWS::EFS::MountTarget |  |
| [DatasetsEfsMountTarget4](codeocean.template.yaml#L3636) | AWS::EFS::MountTarget |  |
| [DatasetsEfsMountTarget5](codeocean.template.yaml#L3649) | AWS::EFS::MountTarget |  |
| [DatasetsEfsMountTarget6](codeocean.template.yaml#L3662) | AWS::EFS::MountTarget |  |
| [ScratchEfs](codeocean.template.yaml#L3675) | AWS::EFS::FileSystem |  |
| [ScratchEfsSecurityGroup](codeocean.template.yaml#L3715) | AWS::EC2::SecurityGroup | Security group for access control |
| [ScratchEfsSecurityGroupEgressDefault](codeocean.template.yaml#L3728) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [ScratchEfsSecurityGroupIngressJobs](codeocean.template.yaml#L3736) | AWS::EC2::SecurityGroupIngress | efs from jobs |
| [ScratchEfsSecurityGroupIngressServices](codeocean.template.yaml#L3747) | AWS::EC2::SecurityGroupIngress | efs from services |
| [ScratchEfsSecurityGroupIngressWorkers](codeocean.template.yaml#L3758) | AWS::EC2::SecurityGroupIngress | efs from workers |
| [ScratchEfsMountTarget1](codeocean.template.yaml#L3769) | AWS::EFS::MountTarget |  |
| [ScratchEfsMountTarget2](codeocean.template.yaml#L3781) | AWS::EFS::MountTarget |  |
| [ScratchEfsMountTarget3](codeocean.template.yaml#L3793) | AWS::EFS::MountTarget |  |
| [ScratchEfsMountTarget4](codeocean.template.yaml#L3806) | AWS::EFS::MountTarget |  |
| [ScratchEfsMountTarget5](codeocean.template.yaml#L3819) | AWS::EFS::MountTarget |  |
| [ScratchEfsMountTarget6](codeocean.template.yaml#L3832) | AWS::EFS::MountTarget |  |
| [RedisSecurityGroup](codeocean.template.yaml#L3845) | AWS::EC2::SecurityGroup | Security group for access control |
| [RedisSecurityGroupEgressDefault](codeocean.template.yaml#L3858) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [RedisSecurityGroupIngressJobs](codeocean.template.yaml#L3866) | AWS::EC2::SecurityGroupIngress | redis from jobs |
| [RedisSecurityGroupIngressServices](codeocean.template.yaml#L3877) | AWS::EC2::SecurityGroupIngress | redis from services |
| [RedisSecurityGroupIngressWorkers](codeocean.template.yaml#L3888) | AWS::EC2::SecurityGroupIngress | redis from workers |
| [RedisSubnetGroup](codeocean.template.yaml#L3899) | AWS::ElastiCache::SubnetGroup | Subnet group for Code Ocean Redis |
| [RedisAuthToken](codeocean.template.yaml#L3921) | AWS::SecretsManager::Secret | Redis auth token |
| [RedisReplicationGroup](codeocean.template.yaml#L3938) | AWS::ElastiCache::ReplicationGroup |  |
| [ExternalHostedZone](codeocean.template.yaml#L3973) | AWS::Route53::HostedZone |  |
| [InternalHostedZone](codeocean.template.yaml#L4000) | AWS::Route53::HostedZone |  |
| [DeleteRecordSetCustomResourcePolicy](codeocean.template.yaml#L4018) | AWS::IAM::ManagedPolicy | Permissions for custom resource |
| [DeleteRecordSetRole](codeocean.template.yaml#L4035) | AWS::IAM::Role | Allows AWS Lambda to call AWS services to delete internal code ocean dns records on cloudformation stack deletion. |
| [DeleteRecordSetFunction](codeocean.template.yaml#L4057) | AWS::Lambda::Function | Delete internal Code Ocean DNS records on CloudFormation stack deletion. |
| [DeleteRecordSetCustomResource](codeocean.template.yaml#L4153) | AWS::CloudFormation::CustomResource |  |
| [Certificate](codeocean.template.yaml#L4165) | AWS::CertificateManager::Certificate |  |
| [AnalyticsDBSecurityGroup](codeocean.template.yaml#L4216) | AWS::EC2::SecurityGroup | Security group for access control |
| [AnalyticsDBSecurityGroupEgressDefault](codeocean.template.yaml#L4229) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [AnalyticsDBSecurityGroupIngressServices](codeocean.template.yaml#L4237) | AWS::EC2::SecurityGroupIngress | analyticsdb from services |
| [AnalyticsDBParameterGroup](codeocean.template.yaml#L4248) | AWS::RDS::DBParameterGroup | A parmeter group that includes pg_cron |
| [AnalyticsDBSubnetGroup](codeocean.template.yaml#L4259) | AWS::RDS::DBSubnetGroup |  |
| [AnalyticsDBMasterPassword](codeocean.template.yaml#L4276) | AWS::SecretsManager::Secret | Analytics DB master password |
| [AnalyticsDBInstance](codeocean.template.yaml#L4293) | AWS::RDS::DBInstance | RDS database instance |
| [ExternalSecurityGroup](codeocean.template.yaml#L4332) | AWS::EC2::SecurityGroup | Security group for access control |
| [ExternalSecurityGroupEgressDefault](codeocean.template.yaml#L4345) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [ExternalSecurityGroupIngressHttpIpv4](codeocean.template.yaml#L4353) | AWS::EC2::SecurityGroupIngress |  |
| [ExternalSecurityGroupIngressHttpIpv6](codeocean.template.yaml#L4362) | AWS::EC2::SecurityGroupIngress |  |
| [ExternalSecurityGroupIngressHttpsIpv4](codeocean.template.yaml#L4371) | AWS::EC2::SecurityGroupIngress |  |
| [ExternalSecurityGroupIngressHttpsIpv6](codeocean.template.yaml#L4380) | AWS::EC2::SecurityGroupIngress |  |
| [ExternalLoadBalancer](codeocean.template.yaml#L4389) | AWS::ElasticLoadBalancingV2::LoadBalancer |  |
| [TargetGroupAnalytics](codeocean.template.yaml#L4439) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupAssets](codeocean.template.yaml#L4458) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupCWProxy](codeocean.template.yaml#L4477) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupFileProxy](codeocean.template.yaml#L4496) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupGitProxy](codeocean.template.yaml#L4515) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupApiService](codeocean.template.yaml#L4534) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupGW](codeocean.template.yaml#L4553) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupRegistry](codeocean.template.yaml#L4572) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupScim](codeocean.template.yaml#L4591) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupWeb](codeocean.template.yaml#L4610) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [ListenerExternalHTTP](codeocean.template.yaml#L4629) | AWS::ElasticLoadBalancingV2::Listener |  |
| [ListenerExternalHTTPS](codeocean.template.yaml#L4642) | AWS::ElasticLoadBalancingV2::Listener |  |
| [ListenerRuleAnalytics](codeocean.template.yaml#L4660) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleFileProxy](codeocean.template.yaml#L4680) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleFileProxyAuthCallback](codeocean.template.yaml#L4695) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleFileProxyDatasets](codeocean.template.yaml#L4710) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleFileProxyDatasetsAuthCallback](codeocean.template.yaml#L4725) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleFileProxyInput](codeocean.template.yaml#L4740) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleFileProxyInputAuthCallback](codeocean.template.yaml#L4755) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleCWProxy](codeocean.template.yaml#L4770) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleMLflow](codeocean.template.yaml#L4785) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleMLflowApp](codeocean.template.yaml#L4800) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleAPIService](codeocean.template.yaml#L4815) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleGW](codeocean.template.yaml#L4830) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleDockerRegistry](codeocean.template.yaml#L4845) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleAssets](codeocean.template.yaml#L4865) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleGitProxy](codeocean.template.yaml#L4880) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleScim](codeocean.template.yaml#L4895) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ExternalDnsRecord](codeocean.template.yaml#L4910) | AWS::Route53::RecordSet |  |
| [DockerRegistryDnsRecord](codeocean.template.yaml#L4938) | AWS::Route53::RecordSet |  |
| [AnalyticsDnsRecord](codeocean.template.yaml#L4967) | AWS::Route53::RecordSet |  |
| [JobsSecurityGroup](codeocean.template.yaml#L4996) | AWS::EC2::SecurityGroup | Security group for access control |
| [JobsSecurityGroupEgressDefault](codeocean.template.yaml#L5009) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [JobsInstancePolicy](codeocean.template.yaml#L5017) | AWS::IAM::ManagedPolicy | Permissions for jobs instances |
| [JobsInstanceRole](codeocean.template.yaml#L5130) | AWS::IAM::Role | Allows EC2 jobs instances to call AWS services. |
| [BatchJobsInstanceProfile](codeocean.template.yaml#L5162) | AWS::IAM::InstanceProfile |  |
| [BatchJobsLaunchTemplate](codeocean.template.yaml#L5167) | AWS::EC2::LaunchTemplate |  |
| [BatchJobsComputeEnvironment](codeocean.template.yaml#L5478) | AWS::Batch::ComputeEnvironment |  |
| [BatchJobsJobQueue](codeocean.template.yaml#L5524) | AWS::Batch::JobQueue |  |
| [BatchInstancePolicy](codeocean.template.yaml#L5536) | AWS::IAM::ManagedPolicy | Permissions for batch instance |
| [BatchInstanceRole](codeocean.template.yaml#L5583) | AWS::IAM::Role | Allows EC2 instances in a Code Ocean AWS Batch ECS cluster to access ECS and other required AWS services. |
| [BatchInstanceProfile](codeocean.template.yaml#L5617) | AWS::IAM::InstanceProfile |  |
| [BatchSecurityGroup](codeocean.template.yaml#L5622) | AWS::EC2::SecurityGroup | Security group for access control |
| [BatchSecurityGroupEgressDefault](codeocean.template.yaml#L5637) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [BatchLaunchTemplate](codeocean.template.yaml#L5645) | AWS::EC2::LaunchTemplate |  |
| [BatchOnDemandComputeEnvironment](codeocean.template.yaml#L5808) | AWS::Batch::ComputeEnvironment |  |
| [BatchOnDemandJobQueue](codeocean.template.yaml#L5854) | AWS::Batch::JobQueue |  |
| [BatchGpuOnDemandComputeEnvironment](codeocean.template.yaml#L5871) | AWS::Batch::ComputeEnvironment |  |
| [BatchGpuOnDemandJobQueue](codeocean.template.yaml#L5917) | AWS::Batch::JobQueue |  |
| [BatchSpotComputeEnvironment](codeocean.template.yaml#L5934) | AWS::Batch::ComputeEnvironment |  |
| [BatchSpotJobQueue](codeocean.template.yaml#L5980) | AWS::Batch::JobQueue |  |
| [BatchGpuSpotComputeEnvironment](codeocean.template.yaml#L5997) | AWS::Batch::ComputeEnvironment |  |
| [BatchGpuSpotJobQueue](codeocean.template.yaml#L6043) | AWS::Batch::JobQueue |  |
| [BatchJobPolicy](codeocean.template.yaml#L6060) | AWS::IAM::ManagedPolicy | Permissions for Batch job |
| [BatchJobRole](codeocean.template.yaml#L6212) | AWS::IAM::Role | Allows Code Ocean AWS Batch jobs to access to AWS services. |
| [ServicesSecurityGroup](codeocean.template.yaml#L6242) | AWS::EC2::SecurityGroup | Security group for access control |
| [ServicesSecurityGroupEgressDefault](codeocean.template.yaml#L6255) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [ServicesSecurityGroupIngressSelf](codeocean.template.yaml#L6263) | AWS::EC2::SecurityGroupIngress | self |
| [ServicesSecurityGroupIngressGitProxy](codeocean.template.yaml#L6274) | AWS::EC2::SecurityGroupIngress | git-proxy |
| [ServicesSecurityGroupIngressRegistry](codeocean.template.yaml#L6285) | AWS::EC2::SecurityGroupIngress | registry |
| [ServicesSecurityGroupIngressWeb](codeocean.template.yaml#L6296) | AWS::EC2::SecurityGroupIngress | web |
| [ServicesSecurityGroupIngressGW](codeocean.template.yaml#L6307) | AWS::EC2::SecurityGroupIngress | gw |
| [ServicesSecurityGroupIngressCWProxy](codeocean.template.yaml#L6318) | AWS::EC2::SecurityGroupIngress | cw-proxy |
| [ServicesSecurityGroupIngressAssets](codeocean.template.yaml#L6329) | AWS::EC2::SecurityGroupIngress | assets |
| [ServicesSecurityGroupIngressAPIService](codeocean.template.yaml#L6340) | AWS::EC2::SecurityGroupIngress | api-service |
| [ServicesSecurityGroupIngressFileProxy](codeocean.template.yaml#L6351) | AWS::EC2::SecurityGroupIngress | file-proxy |
| [ServicesSecurityGroupIngressAnalytics](codeocean.template.yaml#L6362) | AWS::EC2::SecurityGroupIngress | analytics |
| [ServicesSecurityGroupIngressScim](codeocean.template.yaml#L6373) | AWS::EC2::SecurityGroupIngress | scim |
| [ServicesSecurityGroupIngressJobs](codeocean.template.yaml#L6384) | AWS::EC2::SecurityGroupIngress | jobs |
| [ServicesSecurityGroupIngressRCache](codeocean.template.yaml#L6395) | AWS::EC2::SecurityGroupIngress | rcache from workers |
| [ServicesSecurityGroupIngressWapi](codeocean.template.yaml#L6406) | AWS::EC2::SecurityGroupIngress | wapi from workers |
| [ServicesSecurityGroupIngressWDT](codeocean.template.yaml#L6417) | AWS::EC2::SecurityGroupIngress | wdt from workers |
| [ServicesInstanceRole](codeocean.template.yaml#L6428) | AWS::IAM::Role | Allows EC2 services instances to call AWS services. |
| [ServicesAssumeRolePolicy](codeocean.template.yaml#L6811) | AWS::IAM::Policy |  |
| [ServicesInstanceProfile](codeocean.template.yaml#L6825) | AWS::IAM::InstanceProfile |  |
| [DataVolume](codeocean.template.yaml#L6830) | AWS::EC2::Volume |  |
| [ServicesLaunchTemplate](codeocean.template.yaml#L6846) | AWS::EC2::LaunchTemplate |  |
| [ServicesAutoScalingGroup](codeocean.template.yaml#L7339) | AWS::AutoScaling::AutoScalingGroup |  |
| [WorkersSecurityGroup](codeocean.template.yaml#L7380) | AWS::EC2::SecurityGroup | Security group for access control |
| [WorkersSecurityGroupEgressDefault](codeocean.template.yaml#L7393) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [WorkersSecurityGroupIngressServices](codeocean.template.yaml#L7401) | AWS::EC2::SecurityGroupIngress | worker proxies from services |
| [WorkersSecurityGroupIngressComputations](codeocean.template.yaml#L7412) | AWS::EC2::SecurityGroupIngress | worker runners/computations from services |
| [WorkerInstancePolicy](codeocean.template.yaml#L7423) | AWS::IAM::ManagedPolicy | Permissions for worker instance |
| [WorkerInstanceRole](codeocean.template.yaml#L7585) | AWS::IAM::Role | Allows EC2 worker instances to call AWS services. |
| [WorkerAssumeRolePolicy](codeocean.template.yaml#L7612) | AWS::IAM::Policy |  |
| [WorkerInstanceProfile](codeocean.template.yaml#L7626) | AWS::IAM::InstanceProfile |  |
| [WorkersLaunchTemplate](codeocean.template.yaml#L7631) | AWS::EC2::LaunchTemplate |  |
| [GPUWorkersLaunchTemplate](codeocean.template.yaml#L7977) | AWS::EC2::LaunchTemplate |  |
| [WorkersAutoScalingGroup](codeocean.template.yaml#L8328) | AWS::AutoScaling::AutoScalingGroup |  |
| [WorkersAutoScalingWarmPool](codeocean.template.yaml#L8382) | AWS::AutoScaling::WarmPool |  |
| [WorkersAvailableSlotsScaleOutPolicy](codeocean.template.yaml#L8391) | AWS::AutoScaling::ScalingPolicy |  |
| [IdleWorkersScaleInPolicy](codeocean.template.yaml#L8402) | AWS::AutoScaling::ScalingPolicy |  |
| [GPUWorkersAutoScalingGroup](codeocean.template.yaml#L8412) | AWS::AutoScaling::AutoScalingGroup |  |
| [GPUWorkersAutoScalingWarmPool](codeocean.template.yaml#L8466) | AWS::AutoScaling::WarmPool |  |
| [GPUWorkersAvailableSlotsScaleOutPolicy](codeocean.template.yaml#L8475) | AWS::AutoScaling::ScalingPolicy |  |
| [GPUIdleWorkersScaleInPolicy](codeocean.template.yaml#L8486) | AWS::AutoScaling::ScalingPolicy |  |
| [WorkersAvailableSlotsLowAlarm](codeocean.template.yaml#L8496) | AWS::CloudWatch::Alarm |  |
| [IdleWorkersHighAlarm](codeocean.template.yaml#L8520) | AWS::CloudWatch::Alarm |  |
| [GPUWorkersAvailableSlotsLowAlarm](codeocean.template.yaml#L8551) | AWS::CloudWatch::Alarm |  |
| [GPUIdleWorkersHighAlarm](codeocean.template.yaml#L8575) | AWS::CloudWatch::Alarm |  |
| [DedicatedMachinesLaunchTemplate](codeocean.template.yaml#L8606) | AWS::EC2::LaunchTemplate |  |
| [ServicesInstanceDedicatedMachinesAccess](codeocean.template.yaml#L8967) | AWS::IAM::ManagedPolicy | Policy for managing dedicated machines |
| [AlarmsTopic](codeocean.template.yaml#L9107) | AWS::SNS::Topic |  |
| [ServicesRootVolumeUsage90Alarm](codeocean.template.yaml#L9114) | AWS::CloudWatch::Alarm |  |
| [ServicesDataVolumeUsage70Alarm](codeocean.template.yaml#L9140) | AWS::CloudWatch::Alarm |  |
| [ServicesDataVolumeUsage95Alarm](codeocean.template.yaml#L9166) | AWS::CloudWatch::Alarm |  |
| [ServicesDockerVolumeUsage90Alarm](codeocean.template.yaml#L9192) | AWS::CloudWatch::Alarm |  |
| [ServicesCpuUsageHighAlarm](codeocean.template.yaml#L9218) | AWS::CloudWatch::Alarm |  |
| [ServicesMemoryUsageHighAlarm](codeocean.template.yaml#L9242) | AWS::CloudWatch::Alarm |  |
| [ServicesUnhealthyHostAlarm](codeocean.template.yaml#L9266) | AWS::CloudWatch::Alarm |  |
| [Services500MetricFilter](codeocean.template.yaml#L9297) | AWS::Logs::MetricFilter |  |
| [Workers500MetricFilter](codeocean.template.yaml#L9311) | AWS::Logs::MetricFilter |  |
| [ServicesCriticalMetricFilter](codeocean.template.yaml#L9325) | AWS::Logs::MetricFilter |  |
| [WorkersCriticalMetricFilter](codeocean.template.yaml#L9339) | AWS::Logs::MetricFilter |  |
| [CriticalErrorsAlarm](codeocean.template.yaml#L9353) | AWS::CloudWatch::Alarm |  |
| [AnalyticsDBStorageAlarm](codeocean.template.yaml#L9397) | AWS::CloudWatch::Alarm |  |
| [AnalyticsDBCpuAlarm](codeocean.template.yaml#L9421) | AWS::CloudWatch::Alarm |  |
| [BackupRole](codeocean.template.yaml#L9445) | AWS::IAM::Role | Provides AWS Backup permission to create backups and perform restores on your behalf across AWS services. |
| [BackupKMSKey](codeocean.template.yaml#L9471) | AWS::KMS::Key | KMS key for AWS Backup Vault |
| [BackupKMSKeyAlias](codeocean.template.yaml#L9541) | AWS::KMS::Alias |  |
| [BackupVault](codeocean.template.yaml#L9554) | AWS::Backup::BackupVault |  |
| [BackupPlan](codeocean.template.yaml#L9592) | AWS::Backup::BackupPlan |  |
| [BackupSelection](codeocean.template.yaml#L9616) | AWS::Backup::BackupSelection |  |
| [BackupCopyPolicy](codeocean.template.yaml#L9636) | AWS::IAM::ManagedPolicy | Permissions for backup copy |
| [BackupCopyRole](codeocean.template.yaml#L9653) | AWS::IAM::Role | Allows BackupCopyFunction lambda to call AWS services |
| [BackupCopyFunction](codeocean.template.yaml#L9676) | AWS::Lambda::Function | Lambda function to automate copy of backup snapshots to a destination backup vault |
| [BackupCopyFunctionPermission](codeocean.template.yaml#L9797) | AWS::Lambda::Permission |  |
| [BackupJobEventRule](codeocean.template.yaml#L9805) | AWS::Events::Rule | Rule to direct AWS Backup backup job events to handler Lambda |
| [CopyJobEventRule](codeocean.template.yaml#L9828) | AWS::Events::Rule | Rule to direct AWS Backup copy job events to handler Lambda |
| [BackupEventBridgeRole](codeocean.template.yaml#L9851) | AWS::IAM::Role | Allows EventBridge to call AWS services |
| [CopyJobCompletedEventRule](codeocean.template.yaml#L9892) | AWS::Events::Rule | Rule to direct AWS Backup copy job events to the destination default event bus |
