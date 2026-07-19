from aws_cdk import (
    Stack,
    Duration,
    aws_cloudwatch as cloudwatch,
    aws_ssm as ssm,
)

from constructs import Construct


class MonitoringStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        endpoint_name: str,
        project_prefix: str,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        #########################################################
        # Invocation 5XX Alarm
        #########################################################

        invocation_5xx_alarm = cloudwatch.Alarm(
            self,
            "Invocation5XXAlarm",
            alarm_name=f"{project_prefix}-endpoint-5xx-errors",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="Invocation5XXErrors",
                dimensions_map={
                    "EndpointName": endpoint_name
                },
                statistic="Sum",
                period=Duration.minutes(1)
            ),
            threshold=1,
            evaluation_periods=1,
            datapoints_to_alarm=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD
        )

        #########################################################
        # Model Latency Alarm
        #########################################################

        latency_alarm = cloudwatch.Alarm(
            self,
            "ModelLatencyAlarm",
            alarm_name=f"{project_prefix}-endpoint-latency",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="ModelLatency",
                dimensions_map={
                    "EndpointName": endpoint_name
                },
                statistic="Average",
                period=Duration.minutes(1)
            ),
            threshold=3000,  # milliseconds
            evaluation_periods=3,
            datapoints_to_alarm=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        )

        #########################################################
        # Store Alarm Names in Parameter Store
        #########################################################

        ssm.StringParameter(
            self,
            "Invocation5XXAlarmName",
            parameter_name="/telco-churn/cloudwatch/alarm/invocation-5xx",
            string_value=invocation_5xx_alarm.alarm_name
        )

        ssm.StringParameter(
            self,
            "LatencyAlarmName",
            parameter_name="/telco-churn/cloudwatch/alarm/model-latency",
            string_value=latency_alarm.alarm_name
        )