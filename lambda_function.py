import json
import boto3
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
message_table = dynamodb.Table('ccaas-customerMessages')
connect = boto3.client('connect')
connect_instance_id = os.environ.get('Amazon_Connect_Instance_ID')


def lambda_handler(event, context):
    print (f'received_event:', event)
    contactFlow_name = event["Details"]["Parameters"].get('flowname')
     
    attrs = event['Details']['ContactData']['Attributes']
    language = attrs.get('language', 'en').lower()
    
    contact_id = event['Details']['ContactData'].get('ContactId')
    


    print (f'current_contact_flow_name: {contactFlow_name}')

    contactFlow_messages = message_table.query(
        IndexName = 'ContactFlowName-index',
        KeyConditionExpression = Key('ContactFlowName').eq(contactFlow_name)
    )

    clear_existing_m_attributes(connect_instance_id, contact_id, attrs)

  
    messages = {}

    for message in contactFlow_messages['Items']:
        if message.get('MessageID'):
            if language == 'en':
                messages[f"m_{message.get('MessageID')}"] = message.get('EnglishText', '')
            else:
                messages[f"m_{message.get('MessageID')}"]  = message.get('FrenchText', '')

    print (messages)
    
    if messages:
        connect.update_contact_attributes(
        InstanceId=connect_instance_id,
        InitialContactId=contact_id,
        Attributes=messages
        )   
    
    return  {
        "statusCode": 200
    }


def clear_existing_m_attributes(instanceID, contactID, attributes):

    m_attributes = {}

    for item in attributes:
        if item.startswith('m_'):
            m_attributes[item] = ''

    if m_attributes:
        connect.update_contact_attributes(
        InstanceId=instanceID,
        InitialContactId=contactID,
        Attributes=m_attributes
        )

    return {
        "statusCode": 200
    }


