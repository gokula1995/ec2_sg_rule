#!/usr/env/python3
import boto3
import sys
import json
import csv
from datetime import datetime



client = boto3.client('ec2', region_name='us-east-1')
instance_list = []

def write_data_csv_file(data, filename):
    with open('/tmp/'+filename+'.csv', 'w', newline='') as csvfile:
        fieldnames = ['InstanceId']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        writer.writerows(data)

def lambda_handler(event, context):

    # Retrieves all regions that work with EC2
    response = client.describe_regions()
    for region in response['Regions']:
        # ec2_client = session.client('ec2', region_name=region['RegionName'])
        ec2_client = boto3.client('ec2', region_name=region['RegionName'])
        ec2_response = ec2_client.get_paginator('describe_instances')
        for response in  ec2_response.paginate():
            for instances in response['Reservations']:
                for eachinstance in instances['Instances']:
                    for securitygroup in eachinstance['SecurityGroups']:
                        sg_response = ec2_client.describe_security_groups(GroupIds=[securitygroup['GroupId']])
                        for eachsecuritygroup in sg_response['SecurityGroups']:
                            for eachsecurityrule in eachsecuritygroup['IpPermissions']:
                                for everyip in eachsecurityrule['IpRanges']:   
                                    if everyip['CidrIp'] == "0.0.0.0/0":
                                        instance_list.append({ "InstanceId": eachinstance['InstanceId'] })

    print(instance_list)
    report_name = str(datetime.now())+"-report.csv"
    write_data_csv_file(instance_list, "list")
    
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file('/tmp/list.csv', 'phani-sg-files', report_name)
