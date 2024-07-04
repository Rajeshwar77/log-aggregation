import os
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_elasticloadbalancingv2 as elbv2,
    aws_s3 as s3,
    Duration,
    CfnOutput,
)

def add_auto_scaling(service: ecs.FargateService, id: str):
    scaling = service.auto_scale_task_count(
        min_capacity=int(os.getenv("MIN_CAPACITY", 1)),
        max_capacity=int(os.getenv("MAX_CAPACITY", 5))
    )
    scaling.scale_on_cpu_utilization(f"{id}CpuScaling",
        target_utilization_percent=int(os.getenv("TARGET_UTILIZATION_PERCENT", 50)),
        scale_in_cooldown=Duration.seconds(60),
        scale_out_cooldown=Duration.seconds(60)
    )

class EcsServicesStack(Stack):

    def __init__(self, scope, id, vpc, loki_bucket, loki_config_path, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create an ECS cluster
        cluster = ecs.Cluster(self, "ECSCluster", vpc=vpc)

        # Create Network Load Balancer
        self.load_balancer = elbv2.NetworkLoadBalancer(self, "NLB",
            vpc=vpc,
            internet_facing=True
        )
        
        # Fluentd Task Definition
        fluentd_task_definition = ecs.FargateTaskDefinition(self, "FluentdTaskDefinition")
        fluentd_container = fluentd_task_definition.add_container("FluentdContainer",
            image=ecs.ContainerImage.from_registry(os.getenv("FLUENTD_IMAGE")),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="Fluentd"),
            environment={
                "LOKI_URL": f"http://{self.load_balancer.load_balancer_dns_name}:3100/loki/api/v1/push"
            }
        )
        fluentd_container.add_port_mappings(ecs.PortMapping(container_port=24224))

        
        # Fluentd Fargate Service with Spot
        fluentd_service = ecs.FargateService(self, "FluentdService",
            cluster=cluster,
            task_definition=fluentd_task_definition,
            desired_count=1,
            assign_public_ip=True,
            capacity_provider_strategies=[ecs.CapacityProviderStrategy(
                capacity_provider="FARGATE_SPOT",
                weight=1
            )]
        )
        fluentd_target_group = elbv2.NetworkTargetGroup(self, "FluentdTG",
            vpc=vpc,
            port=24224,
            protocol=elbv2.Protocol.TCP,
            targets=[fluentd_service]
        )
        self.load_balancer.add_listener("FluentdListener",
            port=24224,
            default_target_groups=[fluentd_target_group]
        )
        add_auto_scaling(fluentd_service, "FluentdScaling")
        """
        # Load Loki configuration from file
        with open(loki_config_path, 'r') as f:
            loki_config = f.read().replace("{s3_bucket_name}", loki_bucket.bucket_name)

        # Loki Task Definition
        loki_task_definition = ecs.FargateTaskDefinition(self, "LokiTaskDefinition")
        loki_container = loki_task_definition.add_container("LokiContainer",
            image=ecs.ContainerImage.from_registry(os.getenv("LOKI_IMAGE")),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="Loki"),
            environment={
                "LOKI_CONFIG_YAML": loki_config
            }
        )
        loki_container.add_port_mappings(ecs.PortMapping(container_port=3100))

        # Loki Fargate Service with Spot
        loki_service = ecs.FargateService(self, "LokiService",
            cluster=cluster,
            task_definition=loki_task_definition,
            desired_count=1,
            assign_public_ip=True,
            capacity_provider_strategies=[ecs.CapacityProviderStrategy(
                capacity_provider="FARGATE_SPOT",
                weight=1
            )]
        )
        loki_target_group = elbv2.NetworkTargetGroup(self, "LokiTG",
            vpc=vpc,
            port=3100,
            protocol=elbv2.Protocol.TCP,
            targets=[loki_service]
        )
        self.load_balancer.add_listener("LokiListener",
            port=3100,
            default_target_groups=[loki_target_group]
        )
        add_auto_scaling(loki_service, "LokiScaling")

        # Grafana Task Definition
        grafana_task_definition = ecs.FargateTaskDefinition(self, "GrafanaTaskDefinition")
        grafana_container = grafana_task_definition.add_container("GrafanaContainer",
            image=ecs.ContainerImage.from_registry(os.getenv("GRAFANA_IMAGE")),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="Grafana"),
            environment={
                "GF_SECURITY_ADMIN_PASSWORD": os.getenv("GF_SECURITY_ADMIN_PASSWORD"),
                "GF_USERS_ALLOW_SIGN_UP": os.getenv("GF_USERS_ALLOW_SIGN_UP", "false")
            }
        )
        grafana_container.add_port_mappings(ecs.PortMapping(container_port=3000))

        # Grafana Fargate Service with Spot
        grafana_service = ecs.FargateService(self, "GrafanaService",
            cluster=cluster,
            task_definition=grafana_task_definition,
            desired_count=1,
            assign_public_ip=True,
            capacity_provider_strategies=[ecs.CapacityProviderStrategy(
                capacity_provider="FARGATE_SPOT",
                weight=1
            )]
        )
        grafana_target_group = elbv2.NetworkTargetGroup(self, "GrafanaTG",
            vpc=vpc,
            port=3000,
            protocol=elbv2.Protocol.TCP,
            targets=[grafana_service]
        )
        self.load_balancer.add_listener("GrafanaListener",
            port=3000,
            default_target_groups=[grafana_target_group]
        )
        add_auto_scaling(grafana_service, "GrafanaScaling")

        # Output the Load Balancer DNS name
        CfnOutput(self, "LoadBalancerDNS", value=self.load_balancer.load_balancer_dns_name)
        """
