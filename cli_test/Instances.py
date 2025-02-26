import pandas as pd
import streamlit as st
import boto3
import botocore
import botocore.exceptions
import botocore.errorfactory


ec2 = boto3.resource('ec2')





def list_instances():
    list_of_instances = []
    instances = list(ec2.instances.filter(
        Filters=[
            {'Name': 'tag:Owner', 'Values': ['fredricklitvin']},
            {'Name': 'tag:MadeWithCli', 'Values': ['yes']},
            {'Name': 'instance-state-name', 'Values': ['running', 'stopped', 'stopping','Pending']}
        ]
    )
    )
    for instance in instances:
        name_tag = ""
        if instance.tags:
            for tag in instance.tags:
                if tag['Key'] == 'Name':
                    name_tag = tag['Value']
                    break
            dict_of_instance = {
                "id": instance.id,
                "name": name_tag,
                "type": instance.instance_type,
                "state": instance.state['Name']
                }
            list_of_instances.append(dict_of_instance)
    return list_of_instances

def create_instance(name = "", type= "", ami = ""):
    ec2.create_instances(
        MinCount=1,
        MaxCount=1,
        ImageId=ami,
        InstanceType=type,
        TagSpecifications=[
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
                        'Value': name
                    }
                ]
            }
        ]
    )

def modify_instance(id = "", state = ""):
    try:
        if state == "stop":
            ec2.meta.client.stop_instances(
                InstanceIds=[
                    id
                ]
            )
        elif state == "start":
            ec2.meta.client.start_instances(
                InstanceIds=[
                    id
                ]
            )
        elif state == "delete":
            ec2.meta.client.terminate_instances(
                InstanceIds=[
                    id
                ]
            )
    except botocore.exceptions.ClientError as e:
        error_message = str(e)
        if "is not in a valid state" in error_message:
            print(f"Error: Instance {id} is not in a valid state to be {state}ed. Try again later.")
        else:
            print(f"Unexpected error: {error_message}")
        return False


get_instances = list_instances()
list_button = st.button("list your instances")
if list_button:
    if len(get_instances) == 0:
        st.markdown("no instances to show")
    else:
        df = pd.DataFrame(get_instances)
        st.dataframe(df)


create_instance_values = {
    "name": None,
    "type": None,
    "ami": None
}

max_instances = 2
st.title("create a new instance")
with st.form(key="instance_form"):
    create_instance_values["name"] = st.text_input("Enter your name:")
    create_instance_values["type"] = st.selectbox("Type", ["t3.nano","t4g.nano"])
    pre_ami = st.selectbox("Ami", ["Amazon Linux", "Ubuntu"])
    if pre_ami == "Amazon Linux" and create_instance_values["type"] == "t3.nano":
            create_instance_values["ami"] = "ami-053a45fff0a704a47"
    elif pre_ami == "Amazon Linux" and create_instance_values["type"] == "t4g.nano":
            create_instance_values["ami"] = "ami-0c518311db5640eff"
    elif pre_ami == "Ubuntu" and create_instance_values["type"] == "t3.nano":
            create_instance_values["ami"] = "ami-04b4f1a9cf54c11d0"
    elif pre_ami == "Ubuntu" and create_instance_values["type"] == "t4g.nano":
            create_instance_values["ami"] = "ami-0a7a4e87939439934"
    submit_button = st.form_submit_button(label="Create instance")
    if submit_button:
        if len(get_instances) == max_instances:
            st.warning("too many instances")
        elif not all(create_instance_values.values()):
            st.warning("please fill in all the fields")
        else:
            st.write("### info")
            for (key,value) in create_instance_values.items():
                st.write(f"{key}: {value}")
            create_instance(create_instance_values["name"],create_instance_values["type"],create_instance_values["ami"],)

modify_instance_values = {
    "id": None,
    "state": None
}
st.title("change your instance state")
with st.form(key="instance_state_form"):
    modify_instance_values["id"] = st.selectbox("Select Instance", [instance["id"] for instance in get_instances])
    modify_instance_values["state"] = st.selectbox("state", ["start","stop","delete"])
    submit_button = st.form_submit_button(label="change instance")
    if submit_button:
        if not all(modify_instance_values.values()):
            st.warning("please fill in all the fields")
        else:
            st.write("### info")
            for (key,value) in modify_instance_values.items():
                st.write(f"{key}: {value}")
            modify_instance(modify_instance_values["id"],modify_instance_values["state"])

