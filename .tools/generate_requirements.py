#!/usr/bin/env python3
"""
System Requirements Document Generator

This script parses a CloudFormation template (codeocean.template.yaml) and generates
a comprehensive system requirements document in Markdown format.
"""

import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple


class SystemRequirementsGenerator:
    def __init__(self, template_path: str):
        """Initialize the generator with the CloudFormation template path."""
        self.template_path = Path(template_path)
        self.template_data = self._load_template()
        self.line_numbers = self._get_line_numbers()
    
    def _load_template(self) -> Dict[str, Any]:
        """Load and parse the CloudFormation template."""
        try:
            with open(self.template_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {self.template_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML template: {e}")
    
    def _get_line_numbers(self) -> Dict[str, int]:
        """Get line numbers for parameters and resources in the template."""
        line_numbers = {}
        
        with open(self.template_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        
        current_section = None
        for i, line in enumerate(lines, 1):            
            # Track sections
            if line.startswith("Parameters:"):
                current_section = "Parameters"
                continue
            elif line.startswith("Resources:"):
                current_section = "Resources"
                continue
            elif not line.startswith(" ") and not line.startswith("\t") and line.endswith(":"):
                current_section = None
            
            # Track parameter and resource names
            if current_section and line.startswith("  "):
                name = line.strip().rstrip(":")
                if current_section == "Parameters":
                    line_numbers[f"param_{name}"] = i
                elif current_section == "Resources":
                    line_numbers[f"resource_{name}"] = i
        
        return line_numbers
    
    def _generate_overview(self) -> str:
        """Generate the overview section."""
        metadata = self.template_data.get("Metadata", {})
        version_info = metadata.get("CodeOcean::VersionInfo", {})
        
        overview = f"""## Overview

This document provides a comprehensive overview of the system requirements and infrastructure components defined in the Code Ocean VPC CloudFormation template. It serves as a reference for understanding the deployment architecture, resource dependencies, and configuration parameters required for the Code Ocean VPC system.

The full resource configuration, including all properties, dependencies, and conditions, is available in the CloudFormation template file. This document provides a high-level summary with direct links to the complete definitions.

### Document Structure
- **System Overview**: High-level architecture and components
- **Parameters**: Configurable values that customize the deployment
- **Resources**: AWS infrastructure resources

All parameters and resources are linked to their exact line numbers in the template file for easy reference to the complete configuration
"""
        if version_info:
            version = version_info.get("Version", "Unknown")
            commit = version_info.get("Commit", "Unknown")
            overview += f"""
**Template Version:** {version}  
**Commit:** {commit}
"""
        
        return overview

    def _generate_system_overview(self) -> str:
        """Generate the overview section."""
        return """## System Overview

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
"""
    
    def _generate_parameters_table(self) -> str:
        """Generate the parameters table."""
        parameters = self.template_data.get("Parameters", {})
        
        if not parameters:
            return "## Parameters\n\nNo parameters defined in this template.\n"
        
        table = """## Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
"""
        
        for param_name, param_config in parameters.items():
            param_type = param_config.get("Type", "String")
            default = param_config.get("Default", "")
            description = param_config.get("Description", "").replace("\n", " ").replace("|", "\\|")
            
            # Get line number for link
            line_num = self.line_numbers.get(f"param_{param_name}", "")
            link_text = f"[{param_name}](codeocean.template.yaml#L{line_num})" if line_num else param_name
            
            # Format default value
            default_str = f"`{default}`" if default else ""
            
            table += f"| {link_text} | {param_type} | {default_str} | {description} |\n"
        
        return table
    
    def _get_resource_description(self, resource_name: str, resource_config: Dict[str, Any]) -> str:
        """Generate a human-readable description for a resource."""
        # Check if resource has a Description property
        properties = resource_config.get("Properties", {})
        if "Description" in properties:
            return properties["Description"]
        
        resource_type = resource_config.get("Type", "")
        
        # Common resource type descriptions
        descriptions = {
            "AWS::EC2::VPC": "Virtual Private Cloud network",
            "AWS::EC2::Subnet": "Network subnet",
            "AWS::EC2::InternetGateway": "Internet gateway for public access",
            "AWS::EC2::NatGateway": "NAT gateway for private subnet internet access",
            "AWS::EC2::RouteTable": "Route table for network routing",
            "AWS::EC2::Route": "Network route definition",
            "AWS::EC2::SecurityGroup": "Security group for access control",
            "AWS::EC2::Instance": "EC2 compute instance",
            "AWS::RDS::DBInstance": "RDS database instance",
            "AWS::Logs::LogGroup": "CloudWatch log group",
            "AWS::EIP": "Elastic IP address",
            "AWS::CloudFormation::WaitCondition": "Wait condition for stack coordination",
            "AWS::CloudFormation::WaitConditionHandle": "Wait condition handle",
        }
        
        base_description = descriptions.get(resource_type, "")
        
        # Add specific details based on resource name patterns
        if "Public" in resource_name and "Subnet" in resource_name:
            return "Public subnet for internet-accessible resources"
        elif "Private" in resource_name and "Subnet" in resource_name:
            return "Private subnet for internal resources"
        elif "LogGroup" in resource_name:
            if "Services" in resource_name:
                return "CloudWatch log group for services"
            elif "Workers" in resource_name:
                return "CloudWatch log group for workers"
            elif "Lambda" in resource_name:
                return "CloudWatch log group for Lambda functions"
            elif "Instances" in resource_name:
                return "CloudWatch log group for EC2 instances"
            elif "Pipelines" in resource_name:
                return "CloudWatch log group for pipelines"
        
        return base_description
    
    def _generate_resources_table(self) -> str:
        """Generate the resources table."""
        resources = self.template_data.get("Resources", {})
        
        if not resources:
            return "## Resources\n\nNo resources defined in this template.\n"
        
        table = """## Resources

| Logical Name | Resource Type | Description |
| ------------ | ------------- | ----------- |
"""
        
        for resource_name, resource_config in resources.items():
            resource_type = resource_config.get("Type", "Unknown")
            description = self._get_resource_description(resource_name, resource_config)
            
            # Get line number for link
            line_num = self.line_numbers.get(f"resource_{resource_name}", "")
            link_text = f"[{resource_name}](codeocean.template.yaml#L{line_num})" if line_num else resource_name
            
            table += f"| {link_text} | {resource_type} | {description} |\n"
        
        return table
    
    def generate_requirements_document(self) -> str:
        """Generate the complete system requirements document."""
        doc = """# Code Ocean VPC System Requirements

"""
        doc += self._generate_overview()
        doc += "\n"
        doc += self._generate_system_overview()
        doc += "\n"
        doc += self._generate_parameters_table()
        doc += "\n"
        doc += self._generate_resources_table()
        
        return doc
    
    def save_document(self, output_path: str = None) -> str:
        """Generate and save the requirements document."""
        if output_path is None:
            output_path = self.template_path.parent / "System Requirements.md"
        
        document = self.generate_requirements_document()
        
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(document)
        
        return str(output_path)


def main():
    """Main function to run the generator."""
    parser = argparse.ArgumentParser(
        description="Generate system requirements document from CloudFormation template"
    )
    parser.add_argument(
        "template_path",
        nargs="?",
        default="../codeocean.template.yaml",
        help="Path to the CloudFormation template file (default: codeocean.template.yaml)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: System Requirements.md in template directory)"
    )
    
    args = parser.parse_args()
    
    try:
        generator = SystemRequirementsGenerator(args.template_path)
        output_path = generator.save_document(args.output)
        print(f"System requirements document generated successfully: {output_path}")
        
        # Print summary statistics
        params_count = len(generator.template_data.get("Parameters", {}))
        resources_count = len(generator.template_data.get("Resources", {}))
        print(f"  - Parameters: {params_count}")
        print(f"  - Resources: {resources_count}")
        
    except Exception as e:
        print(f"Error generating requirements document: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    main()
