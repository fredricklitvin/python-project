# python-project

Overview

This project is a self-service AWS resource provisioning tool designed to automate the creation and management of AWS resources. Using Boto3 for AWS interaction and Streamlit for an easy-to-use UI, the tool allows developers to create and manage EC2 instances, S3 buckets, and Route 53 DNS records while ensuring compliance with DevOps best practices.

Installation

Prerequisites
open ports:
make sure port 8501 is open and allows access

Before running the project, ensure you have the following installed:
Python 3.9+
AWS CLI 
Boto3 (AWS SDK for Python)
Streamlit (UI framework)
Pandas (for data handling)

Setup Instructions

Clone the repository:
git clone https://github.com/fredricklitvin/python-project.git

Install dependencies manually:
pip install boto3 streamlit pandas

Configure AWS credentials:
aws configure

Run the Streamlit app:
streamlit run Instances.py

Features

EC2 Management
List Instances: Display EC2 instances created by the tool.

Create Instances:
Choose between t3.nano and t4g.nano instance types.
Select Amazon Linux or Ubuntu AMI.
Restrict instance creation to a maximum of two running instances.

Manage Instances:
Start, stop, or delete instances created by the tool.

S3 Bucket Management
List Buckets: Display S3 buckets created through the tool.

Create Buckets:
Choose between public and private access.
Requires confirmation for public bucket creation.

Upload Files: Upload files only to buckets created through the tool.

Route 53 DNS Management
Create Hosted Zones: Create new DNS zones in Route 53.

Manage DNS Records: Add, update, or delete DNS records for hosted zones created by the tool.

