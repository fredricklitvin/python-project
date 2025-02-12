"""An AWS Python Pulumi program"""

import pulumi
from pulumi_aws import s3

config = pulumi.Config("myapp")
acl_choice = config.require("acl")

# Create an AWS resource (S3 Bucket)
bucket = s3.BucketV2('fredrick-bucket',
                     acl= acl_choice
                     )

# Export the name of the bucket
pulumi.export('bucket_name', bucket.id)
