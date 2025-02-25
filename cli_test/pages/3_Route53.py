import json
import pandas as pd
import streamlit as st
import boto3
import botocore
import botocore.exceptions
import  botocore.errorfactory
import time

route53 = boto3.client('route53')

def list_zones():
    routes = route53.list_hosted_zones()
    i = 0
    list_of_zones = []
    while i < len(routes['HostedZones']):
        route_id = routes['HostedZones'][i]['Id'].split("/")
        rout_name = routes['HostedZones'][i]['Name']
        zone_info = {
            'Name': rout_name,
            'Id': route_id[-1]
        }
        list_of_zones.append(zone_info)
        i += 1

    i = 0
    list_of_my_zones = []
    while i < len(list_of_zones):
        response = route53.list_tags_for_resource(
            ResourceType='hostedzone',
            ResourceId=list_of_zones[i]['Id']
        )
        try:
            if response['ResourceTagSet']['Tags'][0]['Value'] == 'yes' and response['ResourceTagSet']['Tags'][1][
                'Value'] == 'fredricklitvin':
                list_of_my_zones.append(list_of_zones[i])
        except IndexError:
            i += 1
            continue
        i += 1
    return list_of_my_zones

def create_zone(zone_name = None):
    try:
        response = route53.create_hosted_zone(
            Name=zone_name,
            CallerReference=f"{zone_name}-{int(time.time())}"
        )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'InvalidDomainName':
            return "bad name"
    route53_hostzone_id = response['HostedZone']['Id'].split('/')
    # route53_hostzone_id_split = route53_hostzone_id.split('/')
    route53_id = route53_hostzone_id[-1]
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

def manage_records(job = None , zone_id = None, record_ip = None, record_type = None , record_name = None):
    try:
        route53.change_resource_record_sets(
            ChangeBatch={
                'Changes': [
                    {
                        'Action': job,
                        'ResourceRecordSet': {
                            'Name': record_name,
                            'ResourceRecords': [
                                {
                                    'Value': record_ip,
                                },
                            ],
                            'TTL': 60,
                            'Type': record_type,
                        },
                    },
                ],
            },
            HostedZoneId=zone_id,
        )
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "InvalidChangeBatch":
            return "name taken"

def get_record():
    get_zones_for_record = list_zones()
    list_of_records = []
    for zone in get_zones_for_record:
        get_zone_id = zone['Id']
        response = route53.list_resource_record_sets(
            HostedZoneId=get_zone_id)
        i = 2
        while i < len(response['ResourceRecordSets']):
            the_records = {
                'Name': response['ResourceRecordSets'][i]['Name'],
                'Type': response['ResourceRecordSets'][i]['Type'],
                "Ip": response['ResourceRecordSets'][i]['ResourceRecords'][0]['Value'],
                "Zone_id": zone['Id']

            }
            list_of_records.append(the_records)
            i += 1
    return list_of_records


records_list = get_record()
get_zones = list_zones()

list_button = st.button("list your records")
if list_button:
    if len(records_list) == 0:
        st.markdown("no records to show")
    else:
        df = pd.DataFrame(records_list)
        st.dataframe(df)

list_button = st.button("list your zones")
if list_button:
    if len(get_zones) == 0:
        st.markdown("no zones to show")
    else:
        df = pd.DataFrame(get_zones)
        st.dataframe(df)

zone_name = None
st.title("Create a zone")
with st.form(key="zone_form"):
    zone_name = st.text_input("Choose zone name:")
    submit_button = st.form_submit_button(label="Create zone")
    if submit_button:
        if not zone_name:
            st.warning("please fill in all the fields")
        else:
            if create_zone(zone_name) == "bad name":
                st.warning("bad name for the zone try again")
            else:
                st.write(f"{zone_name} was created")

st.title("Create a record")
base_ip = '192.0.2.'
record_vars = {
    'Name': None,
    'Ip': None,
    'Type': None
}
with st.form(key="create_record_form"):
    zone_id = st.selectbox("Choose your zone id:", [zone['Id'] for zone in get_zones])
    record_vars['Name'] = st.text_input("Choose record name:")
    chosen_ip = st.slider("Choose the last part of the IP:", min_value=1, max_value=254, value=100)
    record_vars['Ip'] = f"{base_ip}{chosen_ip}"
    record_vars['Type'] = st.selectbox("Type", ['A'])
    submit_button = st.form_submit_button(label="Create record")
    if submit_button:
        if not all(record_vars.values()):
            st.warning("please fill in all the fields")
        else:
            for zone in get_zones:
                if zone['Id'] == zone_id:
                    record_vars['Name'] = f"{record_vars['Name']}.{zone['Name']}"
            if manage_records('CREATE', zone_id, record_vars['Ip'], record_vars['Type'] , record_vars['Name'] ) == "name taken":
                st.warning("name taken try a new one")
            else:
                st.write(f"created a new record {record_vars['Name']}")

st.title("Delete a record")
with st.form(key="delete_record_form"):
    chosen_record_to_delete = st.selectbox("Choose record name:", [record['Name'] for record in records_list])
    submit_button = st.form_submit_button(label="delete record")
    if submit_button:
        if not chosen_record_to_delete:
            st.warning("please fill in all the fields")
        else:
            for i in range(len(records_list)):
                if records_list[i]['Name'] == chosen_record_to_delete:
                    manage_records('DELETE', records_list[i]['Zone_id'],records_list[i]['Ip'],records_list[i]['Type'],records_list[i]['Name'])
            st.write(f"deleted record {chosen_record_to_delete}")

st.title("Change a record")
with st.form(key="Change_record_form"):
    chosen_record_to_change = st.selectbox("Choose record name:", [record['Name'] for record in records_list])
    chosen_ip = st.slider("Choose the last part of the IP:", min_value=1, max_value=254, value=100)
    fixed_ip = f"{base_ip}{chosen_ip}"
    record_type = st.selectbox("Type", ['A'])
    submit_button = st.form_submit_button(label="Change record")
    if submit_button:
        if not chosen_record_to_change and fixed_ip and record_type :
            st.warning("please fill in all the fields")
        else:
            for i in range(len(records_list)):
                if records_list[i]['Name'] == chosen_record_to_change:
                    manage_records('UPSERT', records_list[i]['Zone_id'], fixed_ip, record_type,chosen_record_to_change)
                    st.write(f"changed record {chosen_record_to_change}")