import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
message_table = dynamodb.Table('ccaas-customerMessages')




def lambda_handler(event, context):

    contactFlow_name = 'async-chat-entry-QA'

    contactFlow_messages = message_table.query(
        IndexName = 'ContactFlowName-index',
        KeyConditionExpression = key('ContactFlowName').eq(contactFlow_name)
    )

    for message in contactFlow_messages['Items']:
        print(message)

    return 


