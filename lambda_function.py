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

    print (f'current_contact_flow_name: {contactFlow_name}')

    contactFlow_messages = message_table.query(
        IndexName = 'ContactFlowName-index',
        KeyConditionExpression = Key('ContactFlowName').eq(contactFlow_name)
    )

  
    messages = {}

    for message in contactFlow_messages['Items']:
        if message.get('MessageID'):
            if language == 'en':
                messages[message.get('MessageID')] = message.get('EnglishText', '')
            else:
                messages[message.get('MessageID')] = message.get('FrenchText', '')

    print (messages)

    return messages




