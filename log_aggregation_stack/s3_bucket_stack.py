from aws_cdk import (
    Stack,
    aws_s3 as s3,
    Duration,
)
from constructs import Construct

class S3BucketStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.loki_bucket = s3.Bucket(self, "LokiStorageBucket",
            lifecycle_rules=[s3.LifecycleRule(
                id="MoveToIA",
                transitions=[s3.Transition(
                    storage_class=s3.StorageClass.INTELLIGENT_TIERING,
                    transition_after=Duration.days(30)
                )]
            )]
        )
        


