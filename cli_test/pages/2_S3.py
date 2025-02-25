import json
import pandas as pd
import streamlit as st
import boto3
import botocore
import botocore.exceptions
import  botocore.errorfactory

s3 = boto3.client('s3')

def list_buckets():
    response = s3.list_buckets()
    buckets = response['Buckets']

    buckets_with_tag = []

    for bucket in buckets:
        bucket_name = bucket['Name']
        try:
            tag_response = s3.get_bucket_tagging(Bucket=bucket_name)
            tags_checked = 0
            for tag in tag_response['TagSet']:
                if tags_checked == 2:
                    tags_checked = 0
                if tag['Key'] == 'MadeByCli' and tag['Value'] == 'yes':
                    tags_checked += 1
                if tag['Key'] == 'Owner' and tag['Value'] == 'fredricklitvin':
                    tags_checked += 1
                if tags_checked == 2:
                    bucket_dict = {
                        'Name': bucket_name
                    }
                    buckets_with_tag.append(bucket_dict)
        except botocore.exceptions.ClientError:
            continue
    return buckets_with_tag

def create_bucket(bucket_name = None, bucket_type = None):
    try:
        s3.create_bucket(
            Bucket=bucket_name
        )
    except botocore.exceptions.ParamValidationError:
        return "bad"
    except botocore.exceptions.ClientError:
        return "bad"
    if bucket_type == "Public":
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

def upload_file(bucket_name = None , file_bytes = None, key_name = None):
    try:
        s3.put_object(Body=file_bytes, Bucket=bucket_name , Key= key_name)
    except FileNotFoundError:
        return "bad file"
    except botocore.exceptions.ParamValidationError:
        return "bad key"
    except NameError:
        return "no file"



get_buckets = list_buckets()
list_button = st.button("list your buckets")
if list_button:
    if len(get_buckets) == 0:
        st.markdown("no buckets to show")
    else:
        df = pd.DataFrame(get_buckets)
        st.dataframe(df)


create_bucket_values = {
    "name": None,
    "type": None
}
st.title("create a new bucket")
with st.form(key="bucket_form"):
    create_bucket_values["name"] = st.text_input("Enter your name:")
    create_bucket_values["type"] = st.selectbox("Type", ["Private","Public"])
    checkbox_public = st.checkbox("Allow Public")
    submit_button = st.form_submit_button(label="Create Bucket")
    if submit_button:
        if create_bucket_values["type"] == "Public" and not checkbox_public:
            st.warning("Check the public box or change the type!")
        elif create_bucket(create_bucket_values["name"], create_bucket_values["type"]) == "bad":
            st.warning("Bad bucket name, no bucket was created")
        else:
            st.write("### info")
            for (key,value) in create_bucket_values.items():
                st.write(f"{key}: {value}")
            create_bucket(create_bucket_values["name"],create_bucket_values["type"])


push_file = {
    'chosen_bucket': None,
    'key_name': None,
    'uploaded_file': None
}
st.title("upload a file")
with st.form(key="file_form"):
    push_file['chosen_bucket'] = st.selectbox("Select Bucket", [bucket['Name'] for bucket in get_buckets])
    push_file['key_name'] = st.text_input("Choose key name:")
    push_file['uploaded_file'] = st.file_uploader("Choose a file")
    submit_button = st.form_submit_button(label="Upload File")
    if submit_button:
        if not all(push_file.values()):
            st.warning("please fill in all the fields")
        else:
            file_bytes = push_file['uploaded_file'].getvalue()
            file_response = upload_file(push_file['chosen_bucket'], file_bytes, push_file['key_name'])
            st.write(f"{push_file['uploaded_file'].name} was uploaded to {push_file['chosen_bucket']} as {push_file['key_name']}")