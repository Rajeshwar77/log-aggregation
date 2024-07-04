#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import aws_cdk as cdk
from log_aggregation_stack.vpc_stack import VpcStack
from log_aggregation_stack.s3_bucket_stack import S3BucketStack
from log_aggregation_stack.ecs_cluster_stack import EcsServicesStack

# Load environment variables
load_dotenv()

app = cdk.App()

vpc_stack = VpcStack(app, "VpcStack")
s3_bucket_stack = S3BucketStack(app, "S3BucketStack")
ecs_cluster_stack = EcsServicesStack(app, "EcsServicesStack", 
    vpc=vpc_stack.vpc, 
    loki_bucket=s3_bucket_stack.loki_bucket,
    loki_config_path=os.path.join(os.path.dirname(__file__), 'config', 'loki_config.yaml')
)

app.synth()
