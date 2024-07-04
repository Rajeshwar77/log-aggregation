import * as cdk from '@aws-cdk/core';
import * as ecs from '@aws-cdk/aws-ecs';
import * as ec2 from '@aws-cdk/aws-ec2';
import { LokiService } from './loki-service';
import { GrafanaService } from './grafana-service';

export class MyEcsStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'MyVpc', { maxAzs: 2 });
    const cluster = new ecs.Cluster(this, 'MyCluster', { vpc });

    // Create Loki Service
    LokiService.createLokiService(this, cluster);

    // Create Grafana Service
    GrafanaService.createGrafanaService(this, cluster);
  }
}