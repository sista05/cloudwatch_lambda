import boto3
import os

cloudWatch = boto3.client('cloudwatch')
ec2 = boto3.resource('ec2')
alarm_topic = os.environ['ALARM_TOPIC']

failed_system = {
    "OKActions": [alarm_topic],
    "AlarmActions": [alarm_topic],
    "InsufficientDataActions": [alarm_topic],
    "MetricName": "StatusCheckFailed_System",
    "Namespace": "AWS/EC2",
    "Statistic": "Sum",
    "Period": 300,
    "EvaluationPeriods": 1,
    "Threshold": 0,
    "ComparisonOperator": "GreaterThanThreshold",
    "TreatMissingData": "missing"
}

failed_instance = {
    "OKActions": [alarm_topic],
    "AlarmActions": [alarm_topic],
    "InsufficientDataActions": [alarm_topic],
    "MetricName": "StatusCheckFailed_Instance",
    "Namespace": "AWS/EC2",
    "Statistic": "Sum",
    "Period": 300,
    "EvaluationPeriods": 1,
    "Threshold": 0,
    "ComparisonOperator": "GreaterThanThreshold",
    "TreatMissingData": "missing"
}

cpu_util = {
    "OKActions": [alarm_topic],
    "AlarmActions": [alarm_topic],
    "InsufficientDataActions": [alarm_topic],
    "MetricName": "CPUUtilization",
    "Namespace": "AWS/EC2",
    "Statistic": "Average",
    "Period": 300,
    "EvaluationPeriods": 1,
    "Threshold": 80,
    "ComparisonOperator": "GreaterThanOrEqualToThreshold",
    "TreatMissingData": "missing"
}

disk_used_percent = {
    "OKActions": [alarm_topic],
    "AlarmActions": [alarm_topic],
    "InsufficientDataActions": [alarm_topic],
    "MetricName": "disk_used_percent",
    "Namespace": "CWAgent",
    "Statistic": "Maximum",
    "Period": 300,
    "EvaluationPeriods": 1,
    "Threshold": 80,
    "ComparisonOperator": "GreaterThanOrEqualToThreshold",
    "TreatMissingData": "missing"
}

mem_used_percent = {
    "OKActions": [alarm_topic],
    "AlarmActions": [alarm_topic],
    "InsufficientDataActions": [alarm_topic],
    "MetricName": "mem_used_percent",
    "Namespace": "CWAgent",
    "Statistic": "Maximum",
    "Period": 300,
    "EvaluationPeriods": 1,
    "Threshold": 80,
    "ComparisonOperator": "GreaterThanOrEqualToThreshold",
    "TreatMissingData": "missing"
}

burst_balance = {
    "OKActions": [alarm_topic],
    "AlarmActions": [alarm_topic],
    "InsufficientDataActions": [alarm_topic],
    "MetricName": "BurstBalance",
    "Namespace": "AWS/EBS",
    "Statistic": "Average",
    "Period": 300,
    "EvaluationPeriods": 1,
    "Threshold": 20,
    "ComparisonOperator": "LessThanOrEqualToThreshold",
    "TreatMissingData": "missing"
}


def put_alarm(instance_name, instance_id, vol_id, **kwargs):
    """set alarm"""
    kwargs["AlarmName"] = instance_name + "-" + \
        instance_id + "-" + kwargs["MetricName"]

    if(kwargs["MetricName"] == 'disk_used_percent'):
        kwargs["Dimensions"] = [
            {"Name": "InstanceId", "Value": instance_id},
            {'Name': 'fstype', 'Value': 'xfs'},
            {'Name': 'path', 'Value': '/'}
        ]
    elif(kwargs["MetricName"] == 'burst_balance'):
        kwargs["Dimensions"] = [{"Name": "VolumeId", "Value": vol_id}]
    else:
        kwargs["Dimensions"] = [{"Name": "InstanceId", "Value": instance_id}]

    cloudWatch.put_metric_alarm(**kwargs)
    print(f"put alarm {kwargs['AlarmName']}")

def delete_alarm(instance_name, instance_id):

    alarms = []
    prefix_name = instance_name + "-" + instance_id
    for alarm in cloudWatch.describe_alarms(AlarmNamePrefix=prefix_name)['MetricAlarms']:
        alarms.append(alarm['AlarmName'])

    cloudWatch.delete_alarms(AlarmNames=alarms)
    [print(f"delete alarm {alarm}") for alarm in alarms]

def lambda_handler(event, context):

    instance_id = event['detail']['EC2InstanceId']
    instance_name = event['detail']['AutoScalingGroupName']

    if(event['detail-type'] == 'EC2 Instance Launch Successful'):
        vol_id = ec2.Instance(instance_id).block_device_mappings[0]['Ebs']['VolumeId']

        # In case launching EC2 at ScaleOut.
        put_alarm(instance_name, instance_id, vol_id, **failed_system)
        put_alarm(instance_name, instance_id, vol_id, **failed_instance)
        put_alarm(instance_name, instance_id, vol_id, **cpu_util)
        put_alarm(instance_name, instance_id, vol_id, **disk_used_percent)
        put_alarm(instance_name, instance_id, vol_id, **mem_used_percent)
        put_alarm(instance_name, instance_id, vol_id, **burst_balance)

    if(event['detail-type'] == 'EC2 Instance Terminate Successful'):
        # In case Terminate EC2 at ScaleIn.
        delete_alarm(instance_name, instance_id)
