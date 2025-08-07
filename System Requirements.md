# Code Ocean VPC System Requirements

## Overview

This document provides a comprehensive overview of the system requirements and infrastructure components defined in the Code Ocean VPC CloudFormation template. It serves as a reference for understanding the deployment architecture, resource dependencies, and configuration parameters required for the Code Ocean VPC system.

The full resource configuration, including all properties, dependencies, and conditions, is available in the CloudFormation template file. This document provides a high-level summary with direct links to the complete definitions.

### Document Structure
- **System Overview**: High-level architecture and components
- **Parameters**: Configurable values that customize the deployment
- **Resources**: AWS infrastructure resources

All parameters and resources are linked to their exact line numbers in the template file for easy reference to the complete configuration

**Template Version:** v3.8.2  
**Commit:** c29f4c0f168e73e3de27bccc7422a6b5787715a5

## System Overview

### VPC Network

If you choose to install Code Ocean into its own dedicated AWS VPC the CloudFormation template will provision a new VPC across two availability zones with public and private subnets in your selected AWS region. The availability zones and CIDR blocks for VPC and subnets are configurable.

If you choose to install Code Ocean into an existing AWS VPC you can configure the CloudFormation template with the two availability zones and the private and public subnets to deploy to. Public subnets are required if you choose an internet-facing deployment.

Dedicated machines can run across up to six availability zones to provide maximum instance type availability throughout the region. The availability zones and CIDR blocks for the subnets are configurable.

### EC2, Batch and ECS

Code Ocean uses an HTTPS-only AWS application load balancer (ALB) to expose the system to users and to allow access to its internal Git server and Docker registry. The ALB can be internet-facing or internal for deployments behind a VPN.

The system manages five types of EC2 instances:

* Services - Single machine in an auto-scale group attached to an internal load balancer that runs all internal system services.

* Flex Workers - Two auto-scale groups of worker machines where the actual users computations are running. One auto scale group for GPU based computations and the other for general non-GPU computations. When you run a Compute Capsule within Code Ocean it gets scheduled to run on one of the worker machines. The system will automatically provision more worker machines (scale out) as the load increases and deprovision worker machines (scale in) as the load decreases.

* Dedicated Machines - Instances launched exclusively to run user computations. Users can select the instance type from a wide range of instance specifications, including spot instance to reduce cost. Administrators can configure the list of available instance specifications.

* System Jobs - An AWS Batch ECS cluster of instances designed to run asynchronous, resource intensive system jobs such as the creation and indexing of large data assets. The number and types of instances in the cluster are automatically determined by ECS based on the number of jobs and their resource requirements.

* Pipelines - Four AWS Batch ECS clusters of instances that support the execution of Nextflow pipelines, with options for GPU or non-GPU instances, and Spot or On-Demand types. The number and types of instances in the cluster are automatically determined by ECS based on the number of running pipelines and their resource requirements.

The deployment is configured with security groups to control network flow between parts of the system and IAM instance roles for each instance type to limit access to AWS resources.

Shell access to the EC2 instances is available through AWS SSM Session Manager.

### AMI

Each version of Code Ocean VPC comes with a dedicated AMI that is specified in the CloudFormation template. The AMI is based on Amazon Linux 2023 and is used for all types of Code Ocean instances. 
Code Ocean AMIs are shared with customers as soon as the corresponding version is released.

In environments subject to stringent external AMI usage policies, you may instead build your own AMI and override the default by supplying its ID via the custom AMI ID parameter in the CloudFormation template.

### ECR

Docker images for Code Ocean services and tools are published to the [Code Ocean registry](https://gallery.ecr.aws/codeocean) in AWS Public ECR and are automatically pulled by Code Ocean instances, delivering fast, reliable distribution and a consistent container-based microservices architecture.

If you operate under strict security or compliance constraints, you can mirror each release's docker images into your own private ECR or any OCI-compatible registry by:

1. Pulling the required images from AWS Public ECR.
1. Pushing them into your private registry.
1. Overriding the defaults in the CloudFormation stack by providing your registry's URI and the access-secret ARN via the Custom Upstream Docker Registry CloudFormation template parameters.

### DNS

The system is hosted on a subdomain managed with an AWS Route53 hosted zone. For internet-facing Code Ocean deployments the hosted zone is public, and you will need to delegate to it from your parent or root domain. For internal deployments behind a VPN the Route53 hosted zone will be private. See our [Choose a Hosting Domain](https://docs.codeocean.com/admin-guide/deployment-guide/prerequisites#choose-a-hosting-domain) section for details.

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
| **Domain Configuration** | | | |
| [pDnsName](codeocean.template.yaml#L482) | String | `codeocean` | Code Ocean application subdomain |
| [pDnsRootDomain](codeocean.template.yaml#L486) | String |  | Root domain name (e.g. acmecorp.com) |
| [pHostedZoneId](codeocean.template.yaml#L489) | String |  | (Optional) Existing Route 53 hosted zone ID |
| **TLS Certificate Configuration** | | | |
| [pCertificateArn](codeocean.template.yaml#L493) | String |  | (Optional) Existing ACM certificate ARN |
| [pPrivateCA](codeocean.template.yaml#L497) | String | `false` | Is the certificate signed by a private certificate authority? |
| **VPC Configuration (Use Existing)** | | | |
| [pVpcId](codeocean.template.yaml#L304) | String |  | Existing VPC ID. If not specified, a VPC will be created. |
| [pAvailabilityZone1](codeocean.template.yaml#L308) | String |  | Availability Zone 1 for the existing VPC |
| [pAvailabilityZone2](codeocean.template.yaml#L320) | String |  | Availability Zone 2 for the existing VPC |
| [pPrivateSubnet1Id](codeocean.template.yaml#L312) | String |  | Subnet ID for private subnet 1 located in Availability Zone 1 in Existing VPC |
| [pPrivateSubnet2Id](codeocean.template.yaml#L324) | String |  | Subnet ID for private subnet 2 located in Availability Zone 2 in Existing VPC |
| [pPublicSubnet1Id](codeocean.template.yaml#L316) | String |  | Subnet ID for public subnet 1 located in Availability Zone 1 in Existing VPC |
| [pPublicSubnet2Id](codeocean.template.yaml#L328) | String |  | Subnet ID for public subnet 2 located in Availability Zone 2 in Existing VPC |
| **VPC Configuration (Create New)** | | | |
| [pNewVpcAvailabilityZone1](codeocean.template.yaml#L386) | String |  | Availability Zone 1 for the new VPC |
| [pNewVpcAvailabilityZone2](codeocean.template.yaml#L402) | String |  | Availability Zone 2 for the new VPC |
| [pVpcCIDR](codeocean.template.yaml#L380) | String | `10.0.0.0/16` | CIDR block for the VPC |
| [pPrivateSubnet1CIDR](codeocean.template.yaml#L390) | String | `10.0.0.0/20` | CIDR block for private subnet 1 located in Availability Zone 1 |
| [pPrivateSubnet2CIDR](codeocean.template.yaml#L406) | String | `10.0.16.0/20` | CIDR block for private subnet 2 located in Availability Zone 2 |
| [pPublicSubnet1CIDR](codeocean.template.yaml#L396) | String | `10.0.96.0/20` | CIDR block for public subnet 1 located in Availability Zone 1 |
| [pPublicSubnet2CIDR](codeocean.template.yaml#L412) | String | `10.0.112.0/20` | CIDR block for public subnet 2 located in Availability Zone 2 |
| **Custom Upstream Docker Registry Configuration** | | | |
| [pCustomUpstreamDockerRegistryEndpoint](codeocean.template.yaml#L504) | String |  | (Optional) Custom upstream Docker registry endpoint |
| [pCustomUpstreamDockerRegistrySecret](codeocean.template.yaml#L509) | String |  | (Optional) Secret Manager secret ARN for private registry authentication |
| **Deployment Type Configuration** | | | |
| [pDeploymentType](codeocean.template.yaml#L518) | String | `internet-facing` | Make the deployment internet addressable (default) or require a VPN to connect |
| **Custom AMI Configuration** | | | |
| [pCustomAmi](codeocean.template.yaml#L513) | String |  | (Optional) Custom AMI ID to use for services, workers, and batch instances |
| **Services Machine Configuration** | | | |
| [pServicesInstanceType](codeocean.template.yaml#L525) | String | `m7i.large` | EC2 instance type for services machine. |
| **Worker Configuration** | | | |
| [pWorkerInstanceType](codeocean.template.yaml#L535) | String | `r5d.4xlarge` | EC2 instance type for general purpose workers. Instance type must be from the 'r5d' family. |
| [pWorkersAsgMaxSize](codeocean.template.yaml#L547) | Number | `10` | Maximum number of running worker instances |
| [pMinWorkersAvailable](codeocean.template.yaml#L555) | Number | `1` | Minimum number of worker instances the system keeps in its auto scaling warm pool that are ready to receive computations |
| [pGPUWorkerInstanceType](codeocean.template.yaml#L541) | String | `g4dn.4xlarge` | EC2 instance type for GPU Workers. Instance type must belong to the P (3\|3dn\|4d\|5) or G (4ad\|4dn\|5\|6\|r6) families. |
| [pGpuWorkersAsgMaxSize](codeocean.template.yaml#L551) | Number | `10` | Maximum number of running GPU worker instances |
| [pMinGpuWorkersAvailable](codeocean.template.yaml#L559) | Number | `1` | Minimum number of GPU worker instances the system keeps in its auto scaling warm pool that are ready to receive computations |
| [pAutoScalingIdleTimeout](codeocean.template.yaml#L563) | Number | `60` | Number of minutes before system scales-in idle workers |
| **Analytics RDS Configuration** | | | |
| [pRdsInstanceType](codeocean.template.yaml#L567) | String | `db.t4g.small` | RDS instance type for analytics |
| [pRdsAllocatedStorage](codeocean.template.yaml#L574) | Number | `20` | RDS instance allocated storage |
| [pRdsMaxAllocatedStorage](codeocean.template.yaml#L579) | Number | `100` | RDS instance maximum allocated storage |
| **IAM Configuration** | | | |
| [pAssumableRoles](codeocean.template.yaml#L584) | CommaDelimitedList |  |  |
| **Pipeline Configuration** | | | |
| [pBatchMaxvCpus](codeocean.template.yaml#L587) | Number | `256` | Maximum number of vCPUs that can be used by all batch instances |
| [BatchInstanceTypes](codeocean.template.yaml#L591) | CommaDelimitedList | `c7i,m7i,r7i,optimal` | Comma-delimited list of batch instance types for pipelines |
| [BatcGpuInstanceTypes](codeocean.template.yaml#L595) | CommaDelimitedList | `g4dn` | Comma-delimited list of batch instance types for GPU pipelines |
| [pBatchVolumeSize](codeocean.template.yaml#L599) | Number | `300` | Volume size, in gigabytes, of the Docker's EBS volumes for batch instances |
| [pBatchVolumeIops](codeocean.template.yaml#L605) | Number | `5000` | Volume IOPS, number of I/O operations per second, of the Docker's EBS volumes for batch instances |
| [pBatchVolumeThroughput](codeocean.template.yaml#L611) | Number | `500` | Volume Throughput, in MiB/s, of the Docker's EBS volumes for batch instances |
| **(Optional) Network Extension Configurations for Existing VPC** | | | |
| [pAvailabilityZone3](codeocean.template.yaml#L332) | String |  | Availability Zone 3 for the existing VPC |
| [pPrivateSubnet3Id](codeocean.template.yaml#L336) | String |  | Subnet ID for private subnet 3 located in Availability Zone 3 in Existing VPC |
| [pPublicSubnet3Id](codeocean.template.yaml#L340) | String |  | Subnet ID for public subnet 3 located in Availability Zone 3 in Existing VPC |
| [pAvailabilityZone4](codeocean.template.yaml#L344) | String |  | Availability Zone 4 for the existing VPC |
| [pPrivateSubnet4Id](codeocean.template.yaml#L348) | String |  | Subnet ID for private subnet 4 located in Availability Zone 4 in Existing VPC |
| [pPublicSubnet4Id](codeocean.template.yaml#L352) | String |  | Subnet ID for public subnet 4 located in Availability Zone 4 in Existing VPC |
| [pAvailabilityZone5](codeocean.template.yaml#L356) | String |  | Availability Zone 5 for the existing VPC |
| [pPrivateSubnet5Id](codeocean.template.yaml#L360) | String |  | Subnet ID for private subnet 5 located in Availability Zone 5 in Existing VPC |
| [pPublicSubnet5Id](codeocean.template.yaml#L364) | String |  | Subnet ID for public subnet 5 located in Availability Zone 5 in Existing VPC |
| [pAvailabilityZone6](codeocean.template.yaml#L368) | String |  | Availability Zone 6 for the existing VPC |
| [pPrivateSubnet6Id](codeocean.template.yaml#L372) | String |  | Subnet ID for private subnet 6 located in Availability Zone 6 in Existing VPC |
| [pPublicSubnet6Id](codeocean.template.yaml#L376) | String |  | Subnet ID for public subnet 6 located in Availability Zone 6 in Existing VPC |
| **(Optional) Network Extension Configurations for New VPC** | | | |
| [pNewVpcAvailabilityZone3](codeocean.template.yaml#L418) | String |  | Availability Zone 3 for the new VPC |
| [pPrivateSubnet3CIDR](codeocean.template.yaml#L422) | String | `10.0.32.0/20` | CIDR block for private subnet 3 located in Availability Zone 3 |
| [pPublicSubnet3CIDR](codeocean.template.yaml#L428) | String | `10.0.128.0/20` | CIDR block for public subnet 3 located in Availability Zone 3 |
| [pNewVpcAvailabilityZone4](codeocean.template.yaml#L434) | String |  | Availability Zone 4 for the new VPC |
| [pPrivateSubnet4CIDR](codeocean.template.yaml#L438) | String | `10.0.48.0/20` | CIDR block for private subnet 4 located in Availability Zone 4 |
| [pPublicSubnet4CIDR](codeocean.template.yaml#L444) | String | `10.0.144.0/20` | CIDR block for public subnet 4 located in Availability Zone 4 |
| [pNewVpcAvailabilityZone5](codeocean.template.yaml#L450) | String |  | Availability Zone 5 for the new VPC |
| [pPrivateSubnet5CIDR](codeocean.template.yaml#L454) | String | `10.0.64.0/20` | CIDR block for private subnet 5 located in Availability Zone 5 |
| [pPublicSubnet5CIDR](codeocean.template.yaml#L460) | String | `10.0.160.0/20` | CIDR block for public subnet 5 located in Availability Zone 5 |
| [pNewVpcAvailabilityZone6](codeocean.template.yaml#L466) | String |  | Availability Zone 6 for the new VPC |
| [pPrivateSubnet6CIDR](codeocean.template.yaml#L470) | String | `10.0.80.0/20` | CIDR block for private subnet 6 located in Availability Zone 6 |
| [pPublicSubnet6CIDR](codeocean.template.yaml#L476) | String | `10.0.176.0/20` | CIDR block for public subnet 6 located in Availability Zone 6 |
| **(Optional) Backup Configuration** | | | |
| [pBackupSchedule](codeocean.template.yaml#L617) | String | `cron(0 4 ? * * *)` | Backup schedule CRON expression |
| [pBackupRetentionPeriod](codeocean.template.yaml#L621) | Number | `14` | Backup retention period in days |
| [pDestinationBackupVaultArn](codeocean.template.yaml#L626) | String |  | Copy backup snapshots to a destination backup vault |
| [pDestinationBackupVaultCrossRegion](codeocean.template.yaml#L630) | String | `no` | Is the destination backup vault in a different region? |
| [pDestinationBackupRetentionPeriod](codeocean.template.yaml#L637) | Number | `14` | Backup retention period in days for snapshots copied to the destination backup vault |
| [pDestinationBackupS3KmsKey](codeocean.template.yaml#L642) | String |  | AWS KMS key ARN to use for encrypting S3 object backup replicas |
| [pDestinationBackupS3StorageClass](codeocean.template.yaml#L646) | String | `GLACIER_IR` | AWS S3 storage class for backup object replicas |
| [pDestinationBackupCapsulesBucketArn](codeocean.template.yaml#L653) | String |  | Destination backup S3 capsules bucket ARN |
| [pDestinationBackupDatasetsBucketArn](codeocean.template.yaml#L657) | String |  | Destination backup S3 datasets bucket ARN |
| [pDestinationBackupDockerRegistryBucketArn](codeocean.template.yaml#L661) | String |  | Destination backup S3 docker registry bucket ARN |
| [pDestinationBackupInputFilesBucketArn](codeocean.template.yaml#L665) | String |  | Destination backup S3 input files bucket ARN |
| [pDestinationBackupLicensesBucketArn](codeocean.template.yaml#L669) | String |  | Destination backup S3 licenses bucket ARN |
| [pDestinationBackupMLflowBucketArn](codeocean.template.yaml#L673) | String |  | Destination backup S3 MLflow bucket ARN |
| [pDestinationBackupPackagesBucketArn](codeocean.template.yaml#L677) | String |  | Destination backup S3 packages bucket ARN |
| [pDestinationBackupPublicBucketArn](codeocean.template.yaml#L681) | String |  | Destination backup S3 public bucket ARN |
| [pDestinationBackupResultsBucketArn](codeocean.template.yaml#L685) | String |  | Destination backup S3 results bucket ARN |
| **Restore Configuration** | | | |
| [pRestoreSourceAccountId](codeocean.template.yaml#L689) | String |  | (Optional) AWS Account ID to restore backups from |

## Resources

| Logical Name | Resource Type | Description |
| ------------ | ------------- | ----------- |
| [LogGroupInstances](codeocean.template.yaml#L809) | AWS::Logs::LogGroup | CloudWatch log group for EC2 instances |
| [LogGroupLambda](codeocean.template.yaml#L825) | AWS::Logs::LogGroup | CloudWatch log group for Lambda functions |
| [LogGroupPipelines](codeocean.template.yaml#L841) | AWS::Logs::LogGroup | CloudWatch log group for pipelines |
| [LogGroupServices](codeocean.template.yaml#L857) | AWS::Logs::LogGroup | CloudWatch log group for services |
| [LogGroupWorkers](codeocean.template.yaml#L873) | AWS::Logs::LogGroup | CloudWatch log group for workers |
| [Vpc](codeocean.template.yaml#L889) | AWS::EC2::VPC | Virtual Private Cloud network |
| [InternetGateway](codeocean.template.yaml#L908) | AWS::EC2::InternetGateway | Internet gateway for public access |
| [VpcGatewayAttachment](codeocean.template.yaml#L922) | AWS::EC2::VPCGatewayAttachment |  |
| [VpcGatewayAttachmentWaitHandle](codeocean.template.yaml#L930) | AWS::CloudFormation::WaitConditionHandle | Wait condition handle |
| [WaitHandle](codeocean.template.yaml#L935) | AWS::CloudFormation::WaitConditionHandle | Wait condition handle |
| [VpcGatewayAttachmentWaitCondition](codeocean.template.yaml#L937) | AWS::CloudFormation::WaitCondition | Wait condition for stack coordination |
| [PublicSubnet1](codeocean.template.yaml#L947) | AWS::EC2::Subnet | Public subnet for internet-accessible resources |
| [PublicSubnet1RouteTable](codeocean.template.yaml#L968) | AWS::EC2::RouteTable | Public subnet for internet-accessible resources |
| [PublicSubnet1RouteTableAssociation](codeocean.template.yaml#L984) | AWS::EC2::SubnetRouteTableAssociation | Public subnet for internet-accessible resources |
| [PublicSubnet1DefaultRoute](codeocean.template.yaml#L992) | AWS::EC2::Route | Public subnet for internet-accessible resources |
| [PublicSubnet1EIP](codeocean.template.yaml#L1003) | AWS::EC2::EIP | Public subnet for internet-accessible resources |
| [PublicSubnet1NATGateway](codeocean.template.yaml#L1012) | AWS::EC2::NatGateway | Public subnet for internet-accessible resources |
| [PrivateSubnet1](codeocean.template.yaml#L1032) | AWS::EC2::Subnet | Private subnet for internal resources |
| [PrivateSubnet1RouteTable](codeocean.template.yaml#L1052) | AWS::EC2::RouteTable | Private subnet for internal resources |
| [PrivateSubnet1RouteTableAssociation](codeocean.template.yaml#L1068) | AWS::EC2::SubnetRouteTableAssociation | Private subnet for internal resources |
| [PrivateSubnet1DefaultRoute](codeocean.template.yaml#L1076) | AWS::EC2::Route | Private subnet for internal resources |
| [PublicSubnet2](codeocean.template.yaml#L1085) | AWS::EC2::Subnet | Public subnet for internet-accessible resources |
| [PublicSubnet2RouteTable](codeocean.template.yaml#L1106) | AWS::EC2::RouteTable | Public subnet for internet-accessible resources |
| [PublicSubnet2RouteTableAssociation](codeocean.template.yaml#L1122) | AWS::EC2::SubnetRouteTableAssociation | Public subnet for internet-accessible resources |
| [PublicSubnet2DefaultRoute](codeocean.template.yaml#L1130) | AWS::EC2::Route | Public subnet for internet-accessible resources |
| [PublicSubnet2EIP](codeocean.template.yaml#L1141) | AWS::EC2::EIP | Public subnet for internet-accessible resources |
| [PublicSubnet2NATGateway](codeocean.template.yaml#L1150) | AWS::EC2::NatGateway | Public subnet for internet-accessible resources |
| [PrivateSubnet2](codeocean.template.yaml#L1170) | AWS::EC2::Subnet | Private subnet for internal resources |
| [PrivateSubnet2RouteTable](codeocean.template.yaml#L1190) | AWS::EC2::RouteTable | Private subnet for internal resources |
| [PrivateSubnet2RouteTableAssociation](codeocean.template.yaml#L1206) | AWS::EC2::SubnetRouteTableAssociation | Private subnet for internal resources |
| [PrivateSubnet2DefaultRoute](codeocean.template.yaml#L1214) | AWS::EC2::Route | Private subnet for internal resources |
| [PublicSubnet3](codeocean.template.yaml#L1223) | AWS::EC2::Subnet | Public subnet for internet-accessible resources |
| [PublicSubnet3RouteTable](codeocean.template.yaml#L1244) | AWS::EC2::RouteTable | Public subnet for internet-accessible resources |
| [PublicSubnet3RouteTableAssociation](codeocean.template.yaml#L1260) | AWS::EC2::SubnetRouteTableAssociation | Public subnet for internet-accessible resources |
| [PublicSubnet3DefaultRoute](codeocean.template.yaml#L1268) | AWS::EC2::Route | Public subnet for internet-accessible resources |
| [PublicSubnet3EIP](codeocean.template.yaml#L1279) | AWS::EC2::EIP | Public subnet for internet-accessible resources |
| [PublicSubnet3NATGateway](codeocean.template.yaml#L1288) | AWS::EC2::NatGateway | Public subnet for internet-accessible resources |
| [PrivateSubnet3](codeocean.template.yaml#L1308) | AWS::EC2::Subnet | Private subnet for internal resources |
| [PrivateSubnet3RouteTable](codeocean.template.yaml#L1328) | AWS::EC2::RouteTable | Private subnet for internal resources |
| [PrivateSubnet3RouteTableAssociation](codeocean.template.yaml#L1344) | AWS::EC2::SubnetRouteTableAssociation | Private subnet for internal resources |
| [PrivateSubnet3DefaultRoute](codeocean.template.yaml#L1352) | AWS::EC2::Route | Private subnet for internal resources |
| [PublicSubnet4](codeocean.template.yaml#L1361) | AWS::EC2::Subnet | Public subnet for internet-accessible resources |
| [PublicSubnet4RouteTable](codeocean.template.yaml#L1382) | AWS::EC2::RouteTable | Public subnet for internet-accessible resources |
| [PublicSubnet4RouteTableAssociation](codeocean.template.yaml#L1398) | AWS::EC2::SubnetRouteTableAssociation | Public subnet for internet-accessible resources |
| [PublicSubnet4DefaultRoute](codeocean.template.yaml#L1406) | AWS::EC2::Route | Public subnet for internet-accessible resources |
| [PublicSubnet4EIP](codeocean.template.yaml#L1417) | AWS::EC2::EIP | Public subnet for internet-accessible resources |
| [PublicSubnet4NATGateway](codeocean.template.yaml#L1426) | AWS::EC2::NatGateway | Public subnet for internet-accessible resources |
| [PrivateSubnet4](codeocean.template.yaml#L1446) | AWS::EC2::Subnet | Private subnet for internal resources |
| [PrivateSubnet4RouteTable](codeocean.template.yaml#L1466) | AWS::EC2::RouteTable | Private subnet for internal resources |
| [PrivateSubnet4RouteTableAssociation](codeocean.template.yaml#L1482) | AWS::EC2::SubnetRouteTableAssociation | Private subnet for internal resources |
| [PrivateSubnet4DefaultRoute](codeocean.template.yaml#L1490) | AWS::EC2::Route | Private subnet for internal resources |
| [PublicSubnet5](codeocean.template.yaml#L1499) | AWS::EC2::Subnet | Public subnet for internet-accessible resources |
| [PublicSubnet5RouteTable](codeocean.template.yaml#L1520) | AWS::EC2::RouteTable | Public subnet for internet-accessible resources |
| [PublicSubnet5RouteTableAssociation](codeocean.template.yaml#L1536) | AWS::EC2::SubnetRouteTableAssociation | Public subnet for internet-accessible resources |
| [PublicSubnet5DefaultRoute](codeocean.template.yaml#L1544) | AWS::EC2::Route | Public subnet for internet-accessible resources |
| [PublicSubnet5EIP](codeocean.template.yaml#L1555) | AWS::EC2::EIP | Public subnet for internet-accessible resources |
| [PublicSubnet5NATGateway](codeocean.template.yaml#L1564) | AWS::EC2::NatGateway | Public subnet for internet-accessible resources |
| [PrivateSubnet5](codeocean.template.yaml#L1584) | AWS::EC2::Subnet | Private subnet for internal resources |
| [PrivateSubnet5RouteTable](codeocean.template.yaml#L1604) | AWS::EC2::RouteTable | Private subnet for internal resources |
| [PrivateSubnet5RouteTableAssociation](codeocean.template.yaml#L1620) | AWS::EC2::SubnetRouteTableAssociation | Private subnet for internal resources |
| [PrivateSubnet5DefaultRoute](codeocean.template.yaml#L1628) | AWS::EC2::Route | Private subnet for internal resources |
| [PublicSubnet6](codeocean.template.yaml#L1637) | AWS::EC2::Subnet | Public subnet for internet-accessible resources |
| [PublicSubnet6RouteTable](codeocean.template.yaml#L1658) | AWS::EC2::RouteTable | Public subnet for internet-accessible resources |
| [PublicSubnet6RouteTableAssociation](codeocean.template.yaml#L1674) | AWS::EC2::SubnetRouteTableAssociation | Public subnet for internet-accessible resources |
| [PublicSubnet6DefaultRoute](codeocean.template.yaml#L1682) | AWS::EC2::Route | Public subnet for internet-accessible resources |
| [PublicSubnet6EIP](codeocean.template.yaml#L1693) | AWS::EC2::EIP | Public subnet for internet-accessible resources |
| [PublicSubnet6NATGateway](codeocean.template.yaml#L1702) | AWS::EC2::NatGateway | Public subnet for internet-accessible resources |
| [PrivateSubnet6](codeocean.template.yaml#L1722) | AWS::EC2::Subnet | Private subnet for internal resources |
| [PrivateSubnet6RouteTable](codeocean.template.yaml#L1742) | AWS::EC2::RouteTable | Private subnet for internal resources |
| [PrivateSubnet6RouteTableAssociation](codeocean.template.yaml#L1758) | AWS::EC2::SubnetRouteTableAssociation | Private subnet for internal resources |
| [PrivateSubnet6DefaultRoute](codeocean.template.yaml#L1766) | AWS::EC2::Route | Private subnet for internal resources |
| [S3VpcEndpoint](codeocean.template.yaml#L1775) | AWS::EC2::VPCEndpoint |  |
| [S3AccessLogsBucket](codeocean.template.yaml#L1817) | AWS::S3::Bucket |  |
| [S3AccessLogsBucketPolicy](codeocean.template.yaml#L1846) | AWS::S3::BucketPolicy |  |
| [S3BatchBucket](codeocean.template.yaml#L1908) | AWS::S3::Bucket |  |
| [S3BatchBucketPolicy](codeocean.template.yaml#L1941) | AWS::S3::BucketPolicy |  |
| [S3CapsulesBucket](codeocean.template.yaml#L1967) | AWS::S3::Bucket |  |
| [S3CapsulesBucketPolicy](codeocean.template.yaml#L2042) | AWS::S3::BucketPolicy |  |
| [S3DatasetsBucket](codeocean.template.yaml#L2097) | AWS::S3::Bucket |  |
| [S3DatasetsBucketPolicy](codeocean.template.yaml#L2172) | AWS::S3::BucketPolicy |  |
| [S3DatasetsInputBucket](codeocean.template.yaml#L2227) | AWS::S3::Bucket |  |
| [S3DatasetsInputBucketPolicy](codeocean.template.yaml#L2257) | AWS::S3::BucketPolicy |  |
| [S3InputFilesBucket](codeocean.template.yaml#L2283) | AWS::S3::Bucket |  |
| [S3InputFilesBucketPolicy](codeocean.template.yaml#L2358) | AWS::S3::BucketPolicy |  |
| [S3LicensesBucket](codeocean.template.yaml#L2413) | AWS::S3::Bucket |  |
| [S3LicensesBucketPolicy](codeocean.template.yaml#L2478) | AWS::S3::BucketPolicy |  |
| [S3MLflowBucket](codeocean.template.yaml#L2533) | AWS::S3::Bucket |  |
| [S3MLflowBucketPolicy](codeocean.template.yaml#L2608) | AWS::S3::BucketPolicy |  |
| [S3PackagesBucket](codeocean.template.yaml#L2663) | AWS::S3::Bucket |  |
| [S3PackagesBucketPolicy](codeocean.template.yaml#L2738) | AWS::S3::BucketPolicy |  |
| [S3PublicBucket](codeocean.template.yaml#L2793) | AWS::S3::Bucket |  |
| [S3PublicBucketPolicy](codeocean.template.yaml#L2858) | AWS::S3::BucketPolicy |  |
| [S3DockerRegistryBucket](codeocean.template.yaml#L2913) | AWS::S3::Bucket |  |
| [S3DockerRegistryBucketPolicy](codeocean.template.yaml#L2988) | AWS::S3::BucketPolicy |  |
| [S3ResultsBucket](codeocean.template.yaml#L3043) | AWS::S3::Bucket |  |
| [S3ResultsBucketPolicy](codeocean.template.yaml#L3118) | AWS::S3::BucketPolicy |  |
| [S3ScratchBucket](codeocean.template.yaml#L3173) | AWS::S3::Bucket |  |
| [S3ScratchBucketPolicy](codeocean.template.yaml#L3211) | AWS::S3::BucketPolicy |  |
| [S3TempBucket](codeocean.template.yaml#L3237) | AWS::S3::Bucket |  |
| [S3TempBucketPolicy](codeocean.template.yaml#L3270) | AWS::S3::BucketPolicy |  |
| [S3BackupRole](codeocean.template.yaml#L3296) | AWS::IAM::Role | Provides AWS S3 permissions to backup buckets. |
| [S3BackupReplicationPolicy](codeocean.template.yaml#L3316) | AWS::IAM::Policy |  |
| [OpenSearchSecurityGroup](codeocean.template.yaml#L3471) | AWS::EC2::SecurityGroup | Security group for access control |
| [OpenSearchSecurityGroupEgressDefault](codeocean.template.yaml#L3484) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [OpenSearchSecurityGroupIngressJobs](codeocean.template.yaml#L3492) | AWS::EC2::SecurityGroupIngress | es from jobs |
| [OpenSearchSecurityGroupIngressServices](codeocean.template.yaml#L3503) | AWS::EC2::SecurityGroupIngress | es from services |
| [OpenSearchDomain](codeocean.template.yaml#L3514) | AWS::OpenSearchService::Domain |  |
| [DatasetsEfs](codeocean.template.yaml#L3556) | AWS::EFS::FileSystem |  |
| [DatasetsEfsSecurityGroup](codeocean.template.yaml#L3595) | AWS::EC2::SecurityGroup | Security group for access control |
| [DatasetsEfsSecurityGroupEgressDefault](codeocean.template.yaml#L3608) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [DatasetsEfsSecurityGroupIngressJobs](codeocean.template.yaml#L3616) | AWS::EC2::SecurityGroupIngress | efs from jobs |
| [DatasetsEfsSecurityGroupIngressBatch](codeocean.template.yaml#L3627) | AWS::EC2::SecurityGroupIngress | efs from batch |
| [DatasetsEfsSecurityGroupIngressWorkers](codeocean.template.yaml#L3638) | AWS::EC2::SecurityGroupIngress | efs from workers |
| [DatasetsEfsSecurityGroupIngressServices](codeocean.template.yaml#L3649) | AWS::EC2::SecurityGroupIngress | efs from services |
| [DatasetsEfsMountTarget1](codeocean.template.yaml#L3660) | AWS::EFS::MountTarget |  |
| [DatasetsEfsMountTarget2](codeocean.template.yaml#L3672) | AWS::EFS::MountTarget |  |
| [DatasetsEfsMountTarget3](codeocean.template.yaml#L3684) | AWS::EFS::MountTarget |  |
| [DatasetsEfsMountTarget4](codeocean.template.yaml#L3697) | AWS::EFS::MountTarget |  |
| [DatasetsEfsMountTarget5](codeocean.template.yaml#L3710) | AWS::EFS::MountTarget |  |
| [DatasetsEfsMountTarget6](codeocean.template.yaml#L3723) | AWS::EFS::MountTarget |  |
| [ScratchEfs](codeocean.template.yaml#L3736) | AWS::EFS::FileSystem |  |
| [ScratchEfsSecurityGroup](codeocean.template.yaml#L3776) | AWS::EC2::SecurityGroup | Security group for access control |
| [ScratchEfsSecurityGroupEgressDefault](codeocean.template.yaml#L3789) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [ScratchEfsSecurityGroupIngressJobs](codeocean.template.yaml#L3797) | AWS::EC2::SecurityGroupIngress | efs from jobs |
| [ScratchEfsSecurityGroupIngressWorkers](codeocean.template.yaml#L3808) | AWS::EC2::SecurityGroupIngress | efs from workers |
| [ScratchEfsSecurityGroupIngressServices](codeocean.template.yaml#L3819) | AWS::EC2::SecurityGroupIngress | efs from services |
| [ScratchEfsMountTarget1](codeocean.template.yaml#L3830) | AWS::EFS::MountTarget |  |
| [ScratchEfsMountTarget2](codeocean.template.yaml#L3842) | AWS::EFS::MountTarget |  |
| [ScratchEfsMountTarget3](codeocean.template.yaml#L3854) | AWS::EFS::MountTarget |  |
| [ScratchEfsMountTarget4](codeocean.template.yaml#L3867) | AWS::EFS::MountTarget |  |
| [ScratchEfsMountTarget5](codeocean.template.yaml#L3880) | AWS::EFS::MountTarget |  |
| [ScratchEfsMountTarget6](codeocean.template.yaml#L3893) | AWS::EFS::MountTarget |  |
| [RedisSecurityGroup](codeocean.template.yaml#L3906) | AWS::EC2::SecurityGroup | Security group for access control |
| [RedisSecurityGroupEgressDefault](codeocean.template.yaml#L3919) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [RedisSecurityGroupIngressJobs](codeocean.template.yaml#L3927) | AWS::EC2::SecurityGroupIngress | redis from jobs |
| [RedisSecurityGroupIngressWorkers](codeocean.template.yaml#L3938) | AWS::EC2::SecurityGroupIngress | redis from workers |
| [RedisSecurityGroupIngressServices](codeocean.template.yaml#L3949) | AWS::EC2::SecurityGroupIngress | redis from services |
| [RedisSubnetGroup](codeocean.template.yaml#L3960) | AWS::ElastiCache::SubnetGroup | Subnet group for Code Ocean Redis |
| [RedisAuthToken](codeocean.template.yaml#L3982) | AWS::SecretsManager::Secret | Redis auth token |
| [RedisReplicationGroup](codeocean.template.yaml#L4001) | AWS::ElastiCache::ReplicationGroup |  |
| [ExternalHostedZone](codeocean.template.yaml#L4036) | AWS::Route53::HostedZone |  |
| [InternalHostedZone](codeocean.template.yaml#L4063) | AWS::Route53::HostedZone |  |
| [DeleteRecordSetCustomResourcePolicy](codeocean.template.yaml#L4081) | AWS::IAM::ManagedPolicy | Permissions for custom resource |
| [DeleteRecordSetRole](codeocean.template.yaml#L4098) | AWS::IAM::Role | Allows AWS Lambda to call AWS services to delete internal code ocean dns records on cloudformation stack deletion. |
| [DeleteRecordSetFunction](codeocean.template.yaml#L4120) | AWS::Lambda::Function | Delete internal Code Ocean DNS records on CloudFormation stack deletion. |
| [DeleteRecordSetCustomResource](codeocean.template.yaml#L4216) | AWS::CloudFormation::CustomResource |  |
| [Certificate](codeocean.template.yaml#L4228) | AWS::CertificateManager::Certificate |  |
| [AnalyticsDBSecurityGroup](codeocean.template.yaml#L4279) | AWS::EC2::SecurityGroup | Security group for access control |
| [AnalyticsDBSecurityGroupEgressDefault](codeocean.template.yaml#L4292) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [AnalyticsDBSecurityGroupIngressServices](codeocean.template.yaml#L4300) | AWS::EC2::SecurityGroupIngress | analyticsdb from services |
| [AnalyticsDBParameterGroup](codeocean.template.yaml#L4311) | AWS::RDS::DBParameterGroup | A parmeter group that includes pg_cron |
| [AnalyticsDBSubnetGroup](codeocean.template.yaml#L4322) | AWS::RDS::DBSubnetGroup |  |
| [AnalyticsDBMasterPassword](codeocean.template.yaml#L4339) | AWS::SecretsManager::Secret | Analytics DB master password |
| [AnalyticsDBInstance](codeocean.template.yaml#L4358) | AWS::RDS::DBInstance | RDS database instance |
| [ExternalSecurityGroup](codeocean.template.yaml#L4397) | AWS::EC2::SecurityGroup | Security group for access control |
| [ExternalSecurityGroupEgressDefault](codeocean.template.yaml#L4410) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [ExternalSecurityGroupIngressHttpIpv4](codeocean.template.yaml#L4418) | AWS::EC2::SecurityGroupIngress |  |
| [ExternalSecurityGroupIngressHttpIpv6](codeocean.template.yaml#L4427) | AWS::EC2::SecurityGroupIngress |  |
| [ExternalSecurityGroupIngressHttpsIpv4](codeocean.template.yaml#L4436) | AWS::EC2::SecurityGroupIngress |  |
| [ExternalSecurityGroupIngressHttpsIpv6](codeocean.template.yaml#L4445) | AWS::EC2::SecurityGroupIngress |  |
| [ExternalLoadBalancer](codeocean.template.yaml#L4454) | AWS::ElasticLoadBalancingV2::LoadBalancer |  |
| [TargetGroupAnalytics](codeocean.template.yaml#L4504) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupAssets](codeocean.template.yaml#L4523) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupCWProxy](codeocean.template.yaml#L4542) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupFileProxy](codeocean.template.yaml#L4561) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupGitProxy](codeocean.template.yaml#L4580) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupApiService](codeocean.template.yaml#L4599) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupGW](codeocean.template.yaml#L4618) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupRegistry](codeocean.template.yaml#L4637) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupScim](codeocean.template.yaml#L4656) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [TargetGroupWeb](codeocean.template.yaml#L4675) | AWS::ElasticLoadBalancingV2::TargetGroup |  |
| [ListenerExternalHTTP](codeocean.template.yaml#L4694) | AWS::ElasticLoadBalancingV2::Listener |  |
| [ListenerExternalHTTPS](codeocean.template.yaml#L4707) | AWS::ElasticLoadBalancingV2::Listener |  |
| [ListenerRuleAnalytics](codeocean.template.yaml#L4725) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleFileProxy](codeocean.template.yaml#L4745) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleFileProxyAuthCallback](codeocean.template.yaml#L4760) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleFileProxyDatasets](codeocean.template.yaml#L4775) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleFileProxyDatasetsAuthCallback](codeocean.template.yaml#L4790) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleFileProxyInput](codeocean.template.yaml#L4805) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleFileProxyInputAuthCallback](codeocean.template.yaml#L4820) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleCWProxy](codeocean.template.yaml#L4835) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleMLflow](codeocean.template.yaml#L4850) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleMLflowApp](codeocean.template.yaml#L4865) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleAPIService](codeocean.template.yaml#L4880) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleGW](codeocean.template.yaml#L4895) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleDockerRegistry](codeocean.template.yaml#L4910) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleAssets](codeocean.template.yaml#L4930) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleGitProxy](codeocean.template.yaml#L4945) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ListenerRuleScim](codeocean.template.yaml#L4960) | AWS::ElasticLoadBalancingV2::ListenerRule |  |
| [ExternalDnsRecord](codeocean.template.yaml#L4975) | AWS::Route53::RecordSet |  |
| [DockerRegistryDnsRecord](codeocean.template.yaml#L5003) | AWS::Route53::RecordSet |  |
| [AnalyticsDnsRecord](codeocean.template.yaml#L5032) | AWS::Route53::RecordSet |  |
| [CustomRegistrySecretAccessPolicy](codeocean.template.yaml#L5061) | AWS::IAM::ManagedPolicy | Permissions for Code Ocean instances to get the custom registry secret |
| [JobsSecurityGroup](codeocean.template.yaml#L5079) | AWS::EC2::SecurityGroup | Security group for access control |
| [JobsSecurityGroupEgressDefault](codeocean.template.yaml#L5092) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [JobsInstancePolicy](codeocean.template.yaml#L5100) | AWS::IAM::ManagedPolicy | Permissions for jobs instances |
| [JobsInstanceRole](codeocean.template.yaml#L5219) | AWS::IAM::Role | Allows EC2 jobs instances to call AWS services. |
| [JobsAssumeRolePolicy](codeocean.template.yaml#L5251) | AWS::IAM::Policy |  |
| [BatchJobsInstanceProfile](codeocean.template.yaml#L5265) | AWS::IAM::InstanceProfile |  |
| [BatchJobsLaunchTemplate](codeocean.template.yaml#L5270) | AWS::EC2::LaunchTemplate |  |
| [BatchJobsComputeEnvironment](codeocean.template.yaml#L5599) | AWS::Batch::ComputeEnvironment |  |
| [BatchJobsJobQueue](codeocean.template.yaml#L5645) | AWS::Batch::JobQueue |  |
| [BatchInstancePolicy](codeocean.template.yaml#L5657) | AWS::IAM::ManagedPolicy | Permissions for batch instance |
| [BatchInstanceRole](codeocean.template.yaml#L5710) | AWS::IAM::Role | Allows EC2 instances in a Code Ocean AWS Batch ECS cluster to access ECS and other required AWS services. |
| [BatchInstanceProfile](codeocean.template.yaml#L5744) | AWS::IAM::InstanceProfile |  |
| [BatchSecurityGroup](codeocean.template.yaml#L5749) | AWS::EC2::SecurityGroup | Security group for access control |
| [BatchSecurityGroupEgressDefault](codeocean.template.yaml#L5764) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [BatchLaunchTemplate](codeocean.template.yaml#L5772) | AWS::EC2::LaunchTemplate |  |
| [BatchOnDemandComputeEnvironment](codeocean.template.yaml#L5959) | AWS::Batch::ComputeEnvironment |  |
| [BatchOnDemandJobQueue](codeocean.template.yaml#L6005) | AWS::Batch::JobQueue |  |
| [BatchGpuOnDemandComputeEnvironment](codeocean.template.yaml#L6022) | AWS::Batch::ComputeEnvironment |  |
| [BatchGpuOnDemandJobQueue](codeocean.template.yaml#L6068) | AWS::Batch::JobQueue |  |
| [BatchSpotComputeEnvironment](codeocean.template.yaml#L6085) | AWS::Batch::ComputeEnvironment |  |
| [BatchSpotJobQueue](codeocean.template.yaml#L6131) | AWS::Batch::JobQueue |  |
| [BatchGpuSpotComputeEnvironment](codeocean.template.yaml#L6148) | AWS::Batch::ComputeEnvironment |  |
| [BatchGpuSpotJobQueue](codeocean.template.yaml#L6194) | AWS::Batch::JobQueue |  |
| [BatchJobPolicy](codeocean.template.yaml#L6211) | AWS::IAM::ManagedPolicy | Permissions for Batch job |
| [BatchJobRole](codeocean.template.yaml#L6363) | AWS::IAM::Role | Allows Code Ocean AWS Batch jobs to access to AWS services. |
| [WorkersSecurityGroup](codeocean.template.yaml#L6393) | AWS::EC2::SecurityGroup | Security group for access control |
| [WorkersSecurityGroupEgressDefault](codeocean.template.yaml#L6406) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [WorkersSecurityGroupIngressServices](codeocean.template.yaml#L6414) | AWS::EC2::SecurityGroupIngress | worker proxies from services |
| [WorkersSecurityGroupIngressComputations](codeocean.template.yaml#L6425) | AWS::EC2::SecurityGroupIngress | worker runners/computations from services |
| [WorkerInstancePolicy](codeocean.template.yaml#L6436) | AWS::IAM::ManagedPolicy | Permissions for worker instance |
| [WorkerInstanceRole](codeocean.template.yaml#L6604) | AWS::IAM::Role | Allows EC2 worker instances to call AWS services. |
| [WorkerAssumeRolePolicy](codeocean.template.yaml#L6631) | AWS::IAM::Policy |  |
| [WorkerInstanceProfile](codeocean.template.yaml#L6645) | AWS::IAM::InstanceProfile |  |
| [WorkersLaunchTemplate](codeocean.template.yaml#L6650) | AWS::EC2::LaunchTemplate |  |
| [GPUWorkersLaunchTemplate](codeocean.template.yaml#L7006) | AWS::EC2::LaunchTemplate |  |
| [WorkersAutoScalingGroup](codeocean.template.yaml#L7367) | AWS::AutoScaling::AutoScalingGroup |  |
| [WorkersAutoScalingWarmPool](codeocean.template.yaml#L7419) | AWS::AutoScaling::WarmPool |  |
| [IdleWorkersScaleInPolicy](codeocean.template.yaml#L7426) | AWS::AutoScaling::ScalingPolicy |  |
| [GPUWorkersAutoScalingGroup](codeocean.template.yaml#L7436) | AWS::AutoScaling::AutoScalingGroup |  |
| [GPUWorkersAutoScalingWarmPool](codeocean.template.yaml#L7488) | AWS::AutoScaling::WarmPool |  |
| [GPUIdleWorkersScaleInPolicy](codeocean.template.yaml#L7495) | AWS::AutoScaling::ScalingPolicy |  |
| [IdleWorkersHighAlarm](codeocean.template.yaml#L7505) | AWS::CloudWatch::Alarm |  |
| [GPUIdleWorkersHighAlarm](codeocean.template.yaml#L7536) | AWS::CloudWatch::Alarm |  |
| [DedicatedMachinesLaunchTemplate](codeocean.template.yaml#L7567) | AWS::EC2::LaunchTemplate |  |
| [WorkersAvailableSlotsScaleOutPolicy](codeocean.template.yaml#L7938) | AWS::AutoScaling::ScalingPolicy |  |
| [WorkersAvailableSlotsLowAlarm](codeocean.template.yaml#L7949) | AWS::CloudWatch::Alarm |  |
| [GPUWorkersAvailableSlotsScaleOutPolicy](codeocean.template.yaml#L7973) | AWS::AutoScaling::ScalingPolicy |  |
| [GPUWorkersAvailableSlotsLowAlarm](codeocean.template.yaml#L7984) | AWS::CloudWatch::Alarm |  |
| [ServicesSecurityGroup](codeocean.template.yaml#L8008) | AWS::EC2::SecurityGroup | Security group for access control |
| [ServicesSecurityGroupEgressDefault](codeocean.template.yaml#L8021) | AWS::EC2::SecurityGroupEgress | Allow all outbound traffic by default |
| [ServicesSecurityGroupIngressSelf](codeocean.template.yaml#L8029) | AWS::EC2::SecurityGroupIngress | self |
| [ServicesSecurityGroupIngressGitProxy](codeocean.template.yaml#L8040) | AWS::EC2::SecurityGroupIngress | git-proxy |
| [ServicesSecurityGroupIngressRegistry](codeocean.template.yaml#L8051) | AWS::EC2::SecurityGroupIngress | registry |
| [ServicesSecurityGroupIngressWeb](codeocean.template.yaml#L8062) | AWS::EC2::SecurityGroupIngress | web |
| [ServicesSecurityGroupIngressGW](codeocean.template.yaml#L8073) | AWS::EC2::SecurityGroupIngress | gw |
| [ServicesSecurityGroupIngressCWProxy](codeocean.template.yaml#L8084) | AWS::EC2::SecurityGroupIngress | cw-proxy |
| [ServicesSecurityGroupIngressAssets](codeocean.template.yaml#L8095) | AWS::EC2::SecurityGroupIngress | assets |
| [ServicesSecurityGroupIngressAPIService](codeocean.template.yaml#L8106) | AWS::EC2::SecurityGroupIngress | api-service |
| [ServicesSecurityGroupIngressFileProxy](codeocean.template.yaml#L8117) | AWS::EC2::SecurityGroupIngress | file-proxy |
| [ServicesSecurityGroupIngressAnalytics](codeocean.template.yaml#L8128) | AWS::EC2::SecurityGroupIngress | analytics |
| [ServicesSecurityGroupIngressScim](codeocean.template.yaml#L8139) | AWS::EC2::SecurityGroupIngress | scim |
| [ServicesSecurityGroupIngressJobs](codeocean.template.yaml#L8150) | AWS::EC2::SecurityGroupIngress | jobs |
| [ServicesSecurityGroupIngressRCache](codeocean.template.yaml#L8161) | AWS::EC2::SecurityGroupIngress | rcache from workers |
| [ServicesSecurityGroupIngressWapi](codeocean.template.yaml#L8172) | AWS::EC2::SecurityGroupIngress | wapi from workers |
| [ServicesSecurityGroupIngressWDT](codeocean.template.yaml#L8183) | AWS::EC2::SecurityGroupIngress | wdt from workers |
| [ServicesInstanceRole](codeocean.template.yaml#L8194) | AWS::IAM::Role | Allows EC2 services instances to call AWS services. |
| [ServicesAssumeRolePolicy](codeocean.template.yaml#L8724) | AWS::IAM::Policy |  |
| [ServicesInstanceProfile](codeocean.template.yaml#L8738) | AWS::IAM::InstanceProfile |  |
| [DataVolume](codeocean.template.yaml#L8743) | AWS::EC2::Volume |  |
| [ServicesLaunchTemplate](codeocean.template.yaml#L8761) | AWS::EC2::LaunchTemplate |  |
| [ServicesAutoScalingGroup](codeocean.template.yaml#L9275) | AWS::AutoScaling::AutoScalingGroup |  |
| [AlarmsTopic](codeocean.template.yaml#L9318) | AWS::SNS::Topic |  |
| [ServicesRootVolumeUsage90Alarm](codeocean.template.yaml#L9325) | AWS::CloudWatch::Alarm |  |
| [ServicesDataVolumeUsage70Alarm](codeocean.template.yaml#L9351) | AWS::CloudWatch::Alarm |  |
| [ServicesDataVolumeUsage95Alarm](codeocean.template.yaml#L9377) | AWS::CloudWatch::Alarm |  |
| [ServicesDockerVolumeUsage90Alarm](codeocean.template.yaml#L9403) | AWS::CloudWatch::Alarm |  |
| [ServicesCpuUsageHighAlarm](codeocean.template.yaml#L9429) | AWS::CloudWatch::Alarm |  |
| [ServicesMemoryUsageHighAlarm](codeocean.template.yaml#L9453) | AWS::CloudWatch::Alarm |  |
| [ServicesUnhealthyHostAlarm](codeocean.template.yaml#L9477) | AWS::CloudWatch::Alarm |  |
| [Services500MetricFilter](codeocean.template.yaml#L9508) | AWS::Logs::MetricFilter |  |
| [Workers500MetricFilter](codeocean.template.yaml#L9522) | AWS::Logs::MetricFilter |  |
| [ServicesCriticalMetricFilter](codeocean.template.yaml#L9536) | AWS::Logs::MetricFilter |  |
| [WorkersCriticalMetricFilter](codeocean.template.yaml#L9550) | AWS::Logs::MetricFilter |  |
| [CriticalErrorsAlarm](codeocean.template.yaml#L9564) | AWS::CloudWatch::Alarm |  |
| [AnalyticsDBStorageAlarm](codeocean.template.yaml#L9608) | AWS::CloudWatch::Alarm |  |
| [AnalyticsDBCpuAlarm](codeocean.template.yaml#L9632) | AWS::CloudWatch::Alarm |  |
| [BackupRole](codeocean.template.yaml#L9656) | AWS::IAM::Role | Provides AWS Backup permission to create backups and perform restores on your behalf across AWS services. |
| [BackupKMSKey](codeocean.template.yaml#L9682) | AWS::KMS::Key | KMS key for AWS Backup Vault |
| [BackupKMSKeyAlias](codeocean.template.yaml#L9754) | AWS::KMS::Alias |  |
| [BackupVault](codeocean.template.yaml#L9767) | AWS::Backup::BackupVault |  |
| [BackupPlan](codeocean.template.yaml#L9806) | AWS::Backup::BackupPlan |  |
| [BackupSelection](codeocean.template.yaml#L9830) | AWS::Backup::BackupSelection |  |
| [BackupCopyPolicy](codeocean.template.yaml#L9850) | AWS::IAM::ManagedPolicy | Permissions for backup copy |
| [BackupCopyRole](codeocean.template.yaml#L9867) | AWS::IAM::Role | Allows BackupCopyFunction lambda to call AWS services |
| [BackupCopyFunction](codeocean.template.yaml#L9890) | AWS::Lambda::Function | Lambda function to automate copy of backup snapshots to a destination backup vault |
| [BackupCopyFunctionPermission](codeocean.template.yaml#L10011) | AWS::Lambda::Permission |  |
| [BackupJobEventRule](codeocean.template.yaml#L10019) | AWS::Events::Rule | Rule to direct AWS Backup backup job events to handler Lambda |
| [CopyJobEventRule](codeocean.template.yaml#L10042) | AWS::Events::Rule | Rule to direct AWS Backup copy job events to handler Lambda |
| [BackupEventBridgeRole](codeocean.template.yaml#L10065) | AWS::IAM::Role | Allows EventBridge to call AWS services |
| [CopyJobCompletedEventRule](codeocean.template.yaml#L10106) | AWS::Events::Rule | Rule to direct AWS Backup copy job events to the destination default event bus |
