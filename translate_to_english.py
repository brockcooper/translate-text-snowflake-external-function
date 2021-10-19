import json
import boto3

translate = boto3.client('translate')

def lambda_handler(event, context):
   translated = []

   body = json.loads(event["body"])
   status_code = 200
   for row in body["data"]:
       try:
           translated_text = translate.translate_text(
               Text = row[1],
               SourceLanguageCode = 'auto',
               TargetLanguageCode = 'en')["TranslatedText"]
       except Exception as e:
           print(e);
           translate_text = "ERROR"
           # status code of 400 implies an error
           status_code = 400
       translated.append([row[0], translated_text])
   json_compatible_string_to_return = json.dumps({"data" : translated})
   # return data according to Snowflake's specified result format
   return {
       'statusCode': status_code,
       'body': json_compatible_string_to_return
   }

if __name__ == '__main__':
    handler('event', 'context', local=True)