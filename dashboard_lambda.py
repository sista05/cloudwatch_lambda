import boto3
import sys
import json
import collections.abc

cloudwatch = boto3.client("cloudwatch")
ec2 = boto3.resource("ec2")

x, y = [0, 0]
width, height = [12, 6]

cpu_widget = {
    "type": "metric",
    "x": x,
    "y": y,
    "width": width,
    "height": height,
    "properties": {
        "view": "timeSeries",
        "stacked": False,
        "period": 60,
        "stat": "Average",
        "region": "ap-northeast-1",
        "title": "CPUUtilization",
    },
}

memory_widget = {
    "type": "metric",
    "x": x + 12,
    "y": y,
    "width": width,
    "height": height,
    "properties": {
        "view": "timeSeries",
        "stacked": False,
        "period": 60,
        "stat": "Average",
        "region": "ap-northeast-1",
        "title": "mem_used_percent",
    },
}

network_widget = {
    "type": "metric",
    "x": x,
    "y": y,
    "width": width,
    "height": height,
    "properties": {
        "view": "timeSeries",
        "stacked": False,
        "period": 60,
        "stat": "Average",
        "region": "ap-northeast-1",
        "title": "NetworkIn/Out",
    },
}

diskspace_widget = {
    "type": "metric",
    "x": x + 12,
    "y": y,
    "width": width,
    "height": height,
    "properties": {
        "view": "timeSeries",
        "stacked": False,
        "period": 60,
        "stat": "Average",
        "region": "ap-northeast-1",
        "title": "disk_used_percent",
    },
}

ebsread_widget = {
    "type": "metric",
    "x": x,
    "y": y,
    "width": width,
    "height": height,
    "properties": {
        "view": "timeSeries",
        "stacked": False,
        "period": 60,
        "stat": "Average",
        "region": "ap-northeast-1",
        "title": "EBSReadBytes",
    },
}

ebswrite_widget = {
    "type": "metric",
    "x": x + 12,
    "y": y,
    "width": width,
    "height": height,
    "properties": {
        "view": "timeSeries",
        "stacked": False,
        "period": 60,
        "stat": "Average",
        "region": "ap-northeast-1",
        "title": "EBSWriteBytes",
    },
}


def update(metrics, widget):
    """Update value of a netsted dictionary of varyinf depth."""
    for key, value in metrics.items():
        if isinstance(value, collections.abc.Mapping):
            widget[key] = update(widget.get(key, {}), value)
        else:
            widget[key] = value
    return widget


def add_metrics_to_widget(metrics, widget, widgets):
    update({"properties": {"metrics": metrics}}, widget)
    widgets.append(widget)
    print(f"add widget {widget['properties']['title']}")
    return widgets


def set_dashboard_names(dashboard_name, env):
    if env == "dev" or "stg" or "prd":
        dashboard_name = env + "_SampleGroup"
    else:
        sys.exit(
            'Please enter a valid environment(dev, stg, prd)'
        )
    return dashboard_name


def create_or_update_dashboard(dashboard_name, widgets):
    dashboard_body = json.dumps({"widgets": widgets})
    cloudwatch.put_dashboard(DashboardName=dashboard_name,
                             DashboardBody=dashboard_body)
    print(f"add dashboard {dashboard_name}")

def delete_dashboard(dashboard_name):
    for dashboard in cloudwatch.list_dashboards(
            DashboardNamePrefix=dashboard_name)["DashboardEntries"]:
        cloudwatch.delete_dashboards(
            DashboardNames=[dashboard["DashboardName"]])
        print(f"delete dashboard {dashboard['DashboardName']}")

def lambda_handler(event, context):
    dashboard_name = ""
    widgets = []
    metrics_cpu = []
    metrics_memory = []
    metrics_network = []
    metrics_ebsread = []
    metrics_ebswrite = []
    metrics_diskspace = []
    asname_element = event["detail"]["AutoScalingGroupName"].split("-")
    dashboard_name = set_dashboard_names(dashboard_name, asname_element[0])
    instances = ec2.instances.filter(Filters=[
        {
            "Name": "tag:env",
            "Values": [asname_element[0]]
        },
        {
            "Name": "tag:group",
            "Values": ["sample-group"]
        },
    ])
    """Merge each instance metrics in one widget"""
    for instance in instances:
        metrics_cpu.append(
            ["AWS/EC2", "CPUUtilization", "InstanceId", instance.instance_id])
        metrics_memory.append([
            "CWAgent", "mem_used_percent", "InstanceId", instance.instance_id
        ])
        metrics_diskspace.append([
            "CWAgent",
            "disk_used_percent",
            "path",
            "/",
            "InstanceId",
            instance.instance_id,
            "fstype",
            "xfs",
        ])
        metrics_network.append(
            ["AWS/EC2", "NetworkIn", "InstanceId", instance.instance_id])
        metrics_network.append(
            ["AWS/EC2", "NetworkOut", "InstanceId", instance.instance_id])
        metrics_ebswrite.append(
            ["AWS/EC2", "EBSWriteBytes", "InstanceId", instance.instance_id])
        metrics_ebsread.append(
            ["AWS/EC2", "EBSReadBytes", "InstanceId", instance.instance_id])

    if event["detail-type"] == "EC2 Instance Launch Successful":
        add_metrics_to_widget(metrics_ebswrite, ebswrite_widget, widgets)
        add_metrics_to_widget(metrics_ebsread, ebsread_widget, widgets)
        add_metrics_to_widget(metrics_diskspace, diskspace_widget, widgets)
        add_metrics_to_widget(metrics_network, network_widget, widgets)
        add_metrics_to_widget(metrics_memory, memory_widget, widgets)
        add_metrics_to_widget(metrics_cpu, cpu_widget, widgets)
        create_or_update_dashboard(dashboard_name, widgets)
    if event["detail-type"] == "EC2 Instance Terminate Successful":
        delete_dashboard(dashboard_name)
