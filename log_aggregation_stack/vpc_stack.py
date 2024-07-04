import os
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct

class VpcStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.vpc = ec2.Vpc(self, "LogAggregationVPC", cidr=os.getenv("VPC_CIDR", "10.0.0.0/16"))
        
from aws_cdk import Stack, aws_ec2 as ec2

class VpcStack(Stack):

    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Replace 'cidr' with 'ip_addresses' in VpcProps
        self.vpc = ec2.Vpc(self, "LogAggregationVPC",
            cidr=os.getenv("VPC_CIDR", "10.0.0.0/16"),  # Example CIDR, replace with your actual CIDR
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name="Public",
                    cidr_mask=24
                )
            ]
        )
