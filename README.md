# cloudwatch_lambda
Create CloudWatch Metrics monitor by AutoScaling

[![Language](http://img.shields.io/badge/language-Python3.6-brightgreen.svg?style=flat
)](https://www.python.org/)
[![License](http://img.shields.io/badge/license-MIT-lightgrey.svg?style=flat
)](http://mit-license.org)
[![Twitter](https://img.shields.io/badge/twitter-@sista05-blue.svg?style=flat)](http://twitter.com/sista05)

##  🚨alarm_lambda

Automatically set or delete CW alarm when EC2 targeted for autoscale is Launch or Terminate.

### Alarts information

- Notify alert when metric is OK | ALARM | INSUFFICIENT_DATA
- Alert name is ${instance name}-${instance ID}-${monitored metric name}

Please set it by CloudWatch Event AutoScaling.

| Metrics |Namespace|Statistic|
----|----|----
|StatusCheckFailed_System| AWS/EC2|Sum|
|StatusCheckFailed_Instance| AWS/EC2|Sum|
|CPUUtilization| AWS/EC2|Agerage|
|DiskSpaceUtilization| System/Linux|Maximum|
|MemoryUtilization|System/Linux |Maximum|
|BurstBalance| AWS/EBS|Average|

### IAM Policy

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "cloudwatch:PutMetricAlarm",
                "cloudwatch:DeleteAlarms",
                "cloudwatch:DescribeAlarms"
            ],
            "Resource": "*"
        }
    ]
}
```


## 📈dashboard_lambda
Automatically create or update dashboard for instance monitoring.
Please change it arbitrarily and use.

|Widget Name| Metrics |Namespace|
----|----|----|
|CPUUtilization|CPUUtilization| AWS/EC2|
|mem_used_percent|mem_used_percent| AWS/EC2|
|disk_used_percent|disk_used_percent|CWAgent|
|NetworkIn/Out|NetworkIn| CWAgent|
|NetworkIn/Out|NetworkOut|CWAgent |
|EBSWriteBytes|EBSWriteBytes| AWS/EBS|
|EBSReadBytes|EBSReadBytes| AWS/EBS|

### Environment variable

Next implementation.

|Key| Value |
----|----|
|ENV|dev\|stg\|prd|

### Dashboard image
![screenshot.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/244490/912e968a-ef67-d2b9-a625-0aef7b60341f.png)

### IAM Policy

 ```
 {
     "Version": "2012-10-17",
     "Statement": [
         {
             "Effect": "Allow",
             "Action": [
                 "logs:CreateLogGroup",
                 "logs:CreateLogStream",
                 "logs:PutLogEvents"
             ],
             "Resource": "arn:aws:logs:*:*:*"
         },
         {
             "Effect": "Allow",
             "Action": [
                 "ec2:DescribeInstances",
                 "ec2:DescribeRegions",
                 "cloudwatch:PutMetricAlarm",
                 "cloudwatch:DeleteAlarms",
                 "cloudwatch:DescribeAlarms",
                 "cloudwatch:ListDashboards",
                 "cloudwatch:DeleteDashboards",
                 "cloudwatch:PutDashboard"
             ],
             "Resource": "*"
         }
     ]
 }
 ```
