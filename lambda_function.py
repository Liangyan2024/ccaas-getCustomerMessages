import json
import boto3
import os
import re
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
message_table = dynamodb.Table('ccaas-customerMessages')
connect = boto3.client('connect')
connect_instance_id = os.environ.get('Amazon_Connect_Instance_ID')


def lambda_handler(event, context):
    try:
        contactFlow_name = event["Details"]["Parameters"].get('flowname')
        attrs = event['Details']['ContactData']['Attributes']
        language = attrs.get('language', 'en').lower()[:2]
        contact_id = event['Details']['ContactData'].get('ContactId')

        clear_existing_m_attributes(connect_instance_id, contact_id, attrs)

        contactFlow_messages = message_table.query(
            IndexName='ContactFlowName-index',
            KeyConditionExpression=Key('ContactFlowName').eq(contactFlow_name)
        )

        messages = {}
        for message in contactFlow_messages['Items']:
            msg_id = message.get('MessageID')
            if msg_id:
                key = f"m_{msg_id}"
                text = message.get('EnglishText', '') if language == 'en' else message.get('FrenchText', '')
                pattern = r"\$\.Attributes\.(\w+)"
                key_list = []
                key_list = re.findall(pattern, text)
                if key_list:
                    for key_item in key_list:
                        key_value = attrs.get (key_item, 'Missing_Value')
                        if key_value and key_value != 'Missing_Value':
                            text = text.replace(f"$.Attributes.{key_item}",key_value)
                    messages[key] = text
                

        if messages:
            connect.update_contact_attributes(
                InstanceId=connect_instance_id,
                InitialContactId=contact_id,
                Attributes=messages
            )

        return {
            "statusCode": 200
        }

    except Exception as e:
        print(f"Lambda failed with error: {e}")
        return {
            "statusCode": 500,
            "error": str(e)
        }


def clear_existing_m_attributes(instanceID, contactID, attributes):
    m_attributes = {k: '' for k in attributes if k.startswith('m_')}

    if m_attributes:
        connect.update_contact_attributes(
            InstanceId=instanceID,
            InitialContactId=contactID,
            Attributes=m_attributes
        )

    return {
        "statusCode": 200
    }


