# Code Ocean VPC System Requirements

This repository contains system requirements documentation for the Code Ocean VPC deployment 
infrastructure. The documentation is automatically generated from CloudFormation templates and 
provides a comprehensive overview of the AWS resources, parameters, and configurations required 
for deploying Code Ocean in your AWS environment.

## Documentation Structure

System requirements documents are organized by version and can be found in the corresponding 
branches of this repository. For example, system requirements for Code Ocean VPC v3.7.0 can be 
found in the **v3.7.0** branch.

## How to Use

1. Navigate to the branch corresponding to your desired Code Ocean version
2. Open the [`System Requirements.md`](System%20Requirements.md) file to view the complete documentation
3. Use the table of contents and links to navigate to specific sections
4. Reference the line numbers to examine specific configurations in the CloudFormation template

## Generation Tool

The system requirements documentation is generated using Python scripts in the `.tools` directory:

```bash
.tools/generate_requirements.py
```

This tool automatically parses the CloudFormation template and creates human-readable 
documentation with proper links and formatting.
