import json
import boto3
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
message_table = dynamodb.Table('ccaas-customerMessages')
connect = boto3.client('connect')
connect_instance_id = os.environ.get('Amazon_Connect_Instance_ID')


def lambda_handler(event, context):

    contactFlow_ID = event['Details']['ContactData']['Attributes'].get('ContactFlowID')

    print (f'current_contact_flow_ID: {contactFlow_ID}')

    contactFlow_messages = message_table.query(
        IndexName = 'ContactFlowID-index',
        KeyConditionExpression = Key('ContactFlowName').eq(contactFlow_name)
    )

  
    messages = {}

    for message in contactFlow_messages['Items']:
        if message.get('MessageID'):
            messages[message.get('MessageID')] = {'en_message': message.get('EnglishText', ''), 'fr_message': message.get('FrenchText', '')}

    print (messages)

    return 


