import * as ecs from '@aws-cdk/aws-ecs';
import * as cdk from '@aws-cdk/core';

export class LokiService {
  public static createLokiService(scope: cdk.Construct, cluster: ecs.Cluster): ecs.FargateService {
    const lokiTaskDefinition = new ecs.FargateTaskDefinition(scope, 'LokiTaskDef', {
      memoryLimitMiB: 1024,
      cpu: 512,
    });

    lokiTaskDefinition.addContainer('LokiContainer', {
      image: ecs.ContainerImage.fromRegistry('grafana/loki:latest'),
      logging: ecs.LogDrivers.awsLogs({ streamPrefix: 'loki' }),
    });

    return new ecs.FargateService(scope, 'LokiService', {
      cluster,
      taskDefinition: lokiTaskDefinition,
    });
  }
}