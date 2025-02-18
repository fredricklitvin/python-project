# req pip install boto3 and botocore
from posixpath import split
from time import sleep
import boto3
import botocore.exceptions
import  botocore.errorfactory
from botocore.exceptions import ClientError
import time
import json
import time
s3 = boto3.client('s3')
ec2 = boto3.resource('ec2')
route53 = boto3.client('route53')

#lists all the instances
def list_instances(by_id = False, instance_id = "", get_instances_var = False):
    instances = list(ec2.instances.filter(
        Filters=[
            {'Name': 'tag:Owner', 'Values': ['fredricklitvin']},
            {'Name': 'tag:MadeWithCli', 'Values': ['yes']},
            {'Name': 'instance-state-name', 'Values': ['running','stopped','Stopping']}
        ]
    )
    )
    if get_instances_var == True:
        return(instances)
    if by_id == True:
        for instance in instances:
            name_tag = ""
            if instance.tags:
                for tag in instance.tags:
                    if tag['Key'] == 'Name':
                        name_tag = tag['Value']
                        break
            if instance_id == instance.id:
                print(
                    "ID:" ,instance.id, "\n"
                    f"Name: {name_tag}\n" +
                    "Type:" , instance.instance_type ,"\n"
                    "State:", instance.state['Name'],"\n"

                 )
                print("-" * 30)
    else:
        for instance in instances:
            name_tag = ""
            if instance.tags:
                for tag in instance.tags:
                    if tag['Key'] == 'Name':
                        name_tag = tag['Value']
                        break
                print(
                    "ID:", instance.id, "\n"
                    f"Name: {name_tag}\n" +
                    "Type:", instance.instance_type, "\n"
                    "State:", instance.state['Name'], "\n"
                )
                print("-" * 30)
        return
#creates instances
def create_instances():
    finished_creating_instance = False
    while finished_creating_instance == False:
        ami_choice = input("choose ami:\n"
                           "Amazon Linux\n"
                           "Ubuntu\n").lower()
        instance_type = input("choose type:\n"
                           "t3.nano\n"
                           "t4g.nano\n").lower()
        if instance_type == "t3.nano":
            if ami_choice == "amazon linux":
                ami_choice = "ami-053a45fff0a704a47"
                finished_creating_instance = True
            elif ami_choice == "ubuntu":
                ami_choice = "ami-04b4f1a9cf54c11d0"
                finished_creating_instance = True
            else:
                print("wrong ami please start over :)")
        elif instance_type == "t4g.nano":
            if ami_choice == "amazon linux":
                ami_choice = "ami-0c518311db5640eff"
                finished_creating_instance = True
            elif ami_choice == "ubuntu":
                ami_choice = "ami-0a7a4e87939439934"
                finished_creating_instance = True
            else:
                print("wrong ami please start over :)")
        else:
            print("wrong type please start over :)")

    ec2.create_instances(
        MinCount=1,
        MaxCount=1,
        ImageId=ami_choice,
        InstanceType=instance_type,
        TagSpecifications = [
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Owner',
                    'Value': 'fredricklitvin'
                },
                {
                    'Key': 'MadeWithCli',
                    'Value': 'yes'
                },
                {
                    'Key': 'Name',
                    'Value': 'test_fredrick'
                }
        ]
      }
    ]
    )
    return
#stop, start, delete the instance
def stop_start_delete_instances(instance_id, instance_state):
    try:
        if instance_state == "stop":
            ec2.meta.client.stop_instances(
                InstanceIds=[
                    instance_id
                ]
            )
            time.sleep(3)
            list_instances(True, instance_id)
            return
        elif instance_state == "start":
            ec2.meta.client.start_instances(
                InstanceIds=[
                    instance_id
                ]
            )
            time.sleep(15)
            list_instances(True, instance_id)
            return
        elif instance_state == "delete":
            ec2.meta.client.terminate_instances(
                InstanceIds=[
                    instance_id
                ]
            )
            time.sleep(15)
            list_instances(True, instance_id)
            return
    except botocore.exceptions.ClientError as e:
        error_message = str(e)
        if "is not in a valid state" in error_message:
            print(f"Error: Instance {instance_id} is not in a valid state to be {instance_state}ed. Try again later.")
        else:
            print(f"Unexpected error: {error_message}")
        return False
#choose what option you want to do with your instances
def instances_management():
    instances = list_instances(False, "", True)
    while True:
        instance_choice = input("please choose what to do with your instances:\n"+
                                "1. list all\n"+
                                "2. create instances\n"+
                                "3. stop/start/delete instances\n")
        if instance_choice == "1":
            list_instances()
        elif instance_choice == "2":
            if  len(instances) < 2:
                create_instances()
            else:
                print("you already have more then 2 instances, sadly you cant create anymore\n")
        elif instance_choice == "3":
            list_instances()
            while True:
                instance_id = input("choose the instance id:\n"
                                    "or write exit to return:\n")
                if any(instance.id == instance_id for instance in instances):
                    break
                elif instance_id == "exit":
                    return
                else:
                    print("bad id try again")
            while True:
                instance_state = input("stop/start/delete the instance:\n"
                                       "or write exit to return\n").lower()
                print(instance_state)
                if instance_state == "stop" or instance_state == "start" or instance_state == "delete":
                    stop_start_delete_instances(instance_id, instance_state)
                    return
                elif instance_state == "exit":
                    return
                else:
                    print("please write start or stop again")
        else:
            print("please choose one of the options")
#list s3
def s3_list(get_bucket_list = False, take_bucket_name = False):
    tag_key = 'Owner'
    tag_value = 'fredricklitvin'

    # List all S3 buckets and filter based on the tag
    response = s3.list_buckets()
    buckets = response['Buckets']

    buckets_with_tag = []

    for bucket in buckets:
        bucket_name = bucket['Name']

        try:
            tags_response = s3.get_bucket_tagging(Bucket=bucket_name)

            for tag in tags_response.get('TagSet', []):
                if tag['Key'] == tag_key and tag['Value'] == tag_value:
                    buckets_with_tag.append(bucket_name)
                    break
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchTagSet':
                continue
            else:
                continue
    try:
        if get_bucket_list == True:
            return (buckets_with_tag)
        else:
            if take_bucket_name == True:
                return buckets_with_tag[0]
            else:
                print(buckets_with_tag[0])
                print("-" * 30)
    except IndexError:
        print("you made no bucker")
#alows uploading files to your s3
def s3_upload():
    try:
        bucket_name = s3_list(False,True)
        chosen_file_location = input("please choose the exact file location you want to add:\n")
        key_name = input("choose where the file will be stored:\n")
        s3.upload_file(chosen_file_location, bucket_name , key_name)
    except FileNotFoundError:
        print("file not found try again please")
        return
#create a new s3
#creates s3 buckets
def s3_create():
    if len(s3_list(True)) == 1:
        print("too many buckets go back ")
    else:
        bucket_name = input("choose your buckets name:\n")
        try:
            s3.create_bucket(
                Bucket=bucket_name
            )
        except botocore.exceptions.ParamValidationError:
            print("wrong name please try again\n")
            return
        except botocore.exceptions.ClientError:
            print("wrong name please try again\n")
            return
        if input("do you want it to be public? yes/no\n") == "yes":
            if input("ARE YOU SURE yes/no\n") == "yes":

                s3.put_public_access_block(
                    Bucket=bucket_name,
                    PublicAccessBlockConfiguration={
                        'BlockPublicAcls': False,
                        'IgnorePublicAcls': False,
                        'BlockPublicPolicy': False,
                        'RestrictPublicBuckets': False
                    }
                )
                public_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "PublicReadGetObject",
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{bucket_name}/*"
                        }
                    ]
                }

                s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(public_policy))
                print("bucket was made public")
        else:
            print("bucket was made private")
        s3.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={
                'TagSet': [
                    {
                        'Key': 'Owner',
                        'Value': 'fredricklitvin'
                    },
                    {
                        'Key': 'MadeByCli',
                        'Value': 'yes'
                    }
                ]
            },
        )
#choose what to do with the bucket (list,create,add)
def s3_management():
    while True:
        s3_choice = input("please choose what to do with your instances:\n" +
                                "1. list all\n" +
                                "2. create s3\n" +
                                "3. upload file\n")
        if s3_choice == "1":
            s3_list()
        elif s3_choice == "2":
            s3_create()
        elif s3_choice == "3":
            s3_upload()
        else:
            print("wrong choice try again")

def list_zones_route53(get_list_of_my_zones = False, get_names = False):
    routes= route53.list_hosted_zones()
    i = 0
    list_of_zones_id = []
    while i < len(routes['HostedZones']):
        route = routes['HostedZones'][i]['Id'].split("/")
        list_of_zones_id.append(route[-1])
        i+=1
    i = 0
    list_of_my_zones = []
    while i < len(list_of_zones_id):
        response = route53.list_tags_for_resource(
            ResourceType='hostedzone',
            ResourceId=list_of_zones_id[i]
        )
        try:
            if response['ResourceTagSet']['Tags'][0]['Value'] == 'yes' and response['ResourceTagSet']['Tags'][1]['Value'] == 'fredricklitvin' :
                list_of_my_zones.append(list_of_zones_id[i])
        except IndexError:
            i +=1
            continue
        i+=1
    if get_list_of_my_zones == True:
        return list_of_my_zones
    if get_names == True:
        list_of_names = []
        name_check = route53.get_hosted_zone(
            Id=list_of_my_zones[0]
        )
        return name_check['HostedZone']['Name']
def manage_dnf_records():
    zone_name = (list_zones_route53(False,True))
    zone_id = (list_zones_route53(True,False)[0])
    chosen_action = input("choose create/delete/upsert:\n").lower()
    if chosen_action == "create":
        chosen_name = input("choose the name for the record\n")
        choosen_ip = input("choose the ip for the record (try 192.0.2.(1-254)\n")
        response = route53.change_resource_record_sets(
            ChangeBatch={
                'Changes': [
                    {
                        'Action': chosen_action.upper(),
                        'ResourceRecordSet': {
                            'Name':f"{chosen_name}.{zone_name}",
                            'ResourceRecords': [
                                {
                                    'Value': choosen_ip,
                                },
                            ],
                            'TTL': 60,
                            'Type': 'A',
                        },
                    },
                ],
            },
            HostedZoneId=zone_id,
        )
        print(response)
    elif chosen_action == "delete" or chosen_action == "upsert":
        list_record =route53.list_resource_record_sets(
            HostedZoneId=zone_id
        )
        i=2
        while i < len(list_record['ResourceRecordSets']):
            print(i-1,")",list_record['ResourceRecordSets'][2]['Name'],list_record['ResourceRecordSets'][2]['ResourceRecords'][0]['Value'],"\n")
            i+=1
        choosen_record = int(input("choose one of those by their number\n"))
        choosen_record = choosen_record + 1
        if chosen_action == "delete":
            response_delete = route53.change_resource_record_sets(
                ChangeBatch={
                    'Changes': [
                        {
                            'Action': chosen_action.upper(),
                            'ResourceRecordSet': {
                                'Name': list_record['ResourceRecordSets'][choosen_record]['Name'],
                                'ResourceRecords': [
                                    {
                                        'Value': list_record['ResourceRecordSets'][choosen_record]['ResourceRecords'][0]['Value'],
                                    },
                                ],
                                'TTL': 60,
                                'Type': 'A',
                            },
                        },
                    ],
                },
                HostedZoneId=zone_id,
            )
            print("deleted", list_record['ResourceRecordSets'][choosen_record]['Name'])
        else:
            changed_ip = input("write the ip you want to change to:\n")
            response_change = route53.change_resource_record_sets(
                ChangeBatch={
                    'Changes': [
                        {
                            'Action': chosen_action.upper(),
                            'ResourceRecordSet': {
                                'Name': list_record['ResourceRecordSets'][choosen_record]['Name'],
                                'ResourceRecords': [
                                    {
                                        'Value': changed_ip,
                                    },
                                ],
                                'TTL': 60,
                                'Type': 'A',
                            },
                        },
                    ],
                },
                HostedZoneId=zone_id,
            )
            print("changed", list_record['ResourceRecordSets'][choosen_record]['Name'])

#create a new route
def create_zone_route53():
        if len(list_zones_route53(True)) == 1:
            print("you got too many routes ")
        else:
            try:
                route53_name = input("choose the name for your zone:\n")
                response = route53.create_hosted_zone(
                    Name=route53_name,
                    CallerReference=f"{route53_name}-{int(time.time())}"
                   )
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'InvalidDomainName':
                    print("wrong name for the zone")
                    return
                else:
                    print("we got an error please try again with a diffrent name")
                    return
            route53_hostzone_id = response['HostedZone']['Id']
            route53_hostzone_id_split = route53_hostzone_id.split('/')
            route53_id = route53_hostzone_id_split[-1]
            route53.change_tags_for_resource(
                ResourceId=route53_id,
                ResourceType='hostedzone',
                AddTags=[
                    {
                        'Key': 'Owner',
                        'Value': 'fredricklitvin',
                    },
                    {
                        'Key': 'MadeWithCli',
                        'Value': 'yes',
                    }
                ]
            )
            print(f"created new zone: {response['HostedZone']['Name']}")


#choose what to manage with route53
def route53_management():
    while True:
        route53_choice = input("please choose what to do with your service:\n" +
                          "1. Create Zone\n" +
                          "2. Manage DNS Record\n")
        if route53_choice == "1":
            create_zone_route53()
        elif route53_choice == "2":
            manage_dnf_records()
        else:
            print("wrong choice try again")




#start of the code program for the user
while True:
    dev_choice = input("please choose what service to work on:\n"+
                        "1. instances\n"
                        "2. s3\n"
                        "3. area53\n"
                        "4. exit\n")
    if dev_choice =="1":
        instances_management()
    elif dev_choice =="2":
        s3_management()
    elif dev_choice =="3":
        route53_management()
    elif dev_choice =="4":
        break
    else:
        print("wrong choice try again please:\n")
