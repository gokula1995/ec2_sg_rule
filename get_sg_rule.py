#!/usr/env/python3
import boto3
import sys
import json



boto3.setup_default_session(profile_name=sys.argv[1])
client = boto3.client('ec2', region_name='us-east-1')
instance_list = []

def main():

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
                                        instance_list.append(eachinstance['InstanceId'])

    instance_unique_list = list( dict.fromkeys(instance_list) )
    print(instance_unique_list)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please provide the proper format as like below")
        print("Usage: python get_sg_rule.py <aws_profile>")
        sys.exit(1)
    main()
