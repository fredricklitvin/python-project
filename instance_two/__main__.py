import pulumi
import pulumi_aws as aws

config = pulumi.Config("myapp")
ami_id = config.require("ami")
instance = config.require("instance")


# Create EC2 instance
ec2_instance = aws.ec2.Instance("user-instance",
    ami=ami_id,
    instance_type=instance,
    tags={"Name": "fredirck-instance-two",
          "Owner": "fredricklitvin"
          }
)

# Export instance details
pulumi.export("instance_id", ec2_instance.id)
pulumi.export("instance_public_ip", ec2_instance.public_ip)