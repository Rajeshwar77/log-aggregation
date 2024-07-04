import * as ecs from '@aws-cdk/aws-ecs';
import * as cdk from '@aws-cdk/core';

export class GrafanaService {
  public static createGrafanaService(scope: cdk.Construct, cluster: ecs.Cluster): ecs.FargateService {
    const grafanaTaskDefinition = new ecs.FargateTaskDefinition(scope, 'GrafanaTaskDef', {
      memoryLimitMiB: 2048,
      cpu: 1024,
    });

    const grafanaContainer = grafanaTaskDefinition.addContainer('GrafanaContainer', {
      image: ecs.ContainerImage.fromRegistry('grafana/grafana:latest'),
      logging: ecs.LogDrivers.awsLogs({ streamPrefix: 'grafana' }),
    });

    grafanaContainer.addPortMappings({
      containerPort: 3000,
    });

    return new ecs.FargateService(scope, 'GrafanaService', {
      cluster,
      taskDefinition: grafanaTaskDefinition,
    });
  }
}