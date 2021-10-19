import time, datetime, json, os, csv
import traceback
import boto3

learn_bucket = 'svc-verb-lms'
new_bucket_name = 'verb-datalake'
directory = 'repsites/learn'
failures = []

# Use this event for testing
# event = {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'us-west-2', 'eventTime': '2019-02-06T21:15:22.902Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AROAJJVBS7C2NXATARWQ4:sbcadm'}, 'requestParameters': {'sourceIPAddress': '166.70.69.43'}, 'responseElements': {'x-amz-request-id': 'F8ECAB9B0826B964', 'x-amz-id-2': 'mdUTLypRk+0FGjxMIa2Uogbv92oRmqUfzr+nqnnyxehQfIy6/6Xw4UmkfvgNWqErhgLhlvwuYYI='}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': '75506c03-4c25-47d3-bcaa-2ebb77f0490e', 'bucket': {'name': 'svc-verb-lms', 'ownerIdentity': {'principalId': 'AD1RZQGY8HV7I'}, 'arn': 'arn:aws:s3:::svc-verb-lms'}, 'object': {'key': '72/4CBF045E-2241-4559-A5D6-72A24D0A018F/v1/en/quizzes.json', 'size': 60673, 'eTag': 'd11f4bb08c1ec1b5b91207b2cefd45bf', 'sequencer': '005C5B4E6ACAB019B6'}}}]}
# event = {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'us-west-2', 'eventTime': '2019-02-06T21:15:22.902Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AROAJJVBS7C2NXATARWQ4:sbcadm'}, 'requestParameters': {'sourceIPAddress': '166.70.69.43'}, 'responseElements': {'x-amz-request-id': 'F8ECAB9B0826B964', 'x-amz-id-2': 'mdUTLypRk+0FGjxMIa2Uogbv92oRmqUfzr+nqnnyxehQfIy6/6Xw4UmkfvgNWqErhgLhlvwuYYI='}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': '75506c03-4c25-47d3-bcaa-2ebb77f0490e', 'bucket': {'name': 'svc-verb-lms', 'ownerIdentity': {'principalId': 'AD1RZQGY8HV7I'}, 'arn': 'arn:aws:s3:::svc-verb-lms'}, 'object': {'key': 'user_state/000163AA-D371-4D76-82C5-F1B5FBFA1606.json', 'size': 60673, 'eTag': 'd11f4bb08c1ec1b5b91207b2cefd45bf', 'sequencer': '005C5B4E6ACAB019B6'}}}]}


def logs(timestamp, job_name, job_completion_status, actions, error_level,
         error_message, start_time, file_name,
         success_message=None, validation_status=None):
    log = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "job_name": job_name,
        "repo_name": 'learn-data-transform',
        "file_name": file_name,
        "job_completion_status": job_completion_status,
        "priority_level": error_level,
        "actions_to_fix": list(actions),
        "error_message": error_message,
        "seconds_to_run_job": round(time.time() - start_time, 2),
        "subject": f"{job_name}: {job_completion_status}",
        "body": f"""{job_name}: {job_completion_status} \nPriority Level: {error_level}\nError message of: {error_message}"""

    }
    log["default"] = log["body"]

    return log


def send_logs(logs, sns_client):
    response = sns_client.publish(
        TargetArn='arn:aws:sns:us-east-1:845977697457:data-engineering-notifications',
        Message=logs,
        MessageStructure='json'
    )

def get_new_directory(key):
    if (key.find('.json') != -1):
        if (key.find('awards') != -1):
            new_directory = f'awards/{key}'
        elif (key.find('courses') != -1):
            new_directory = f'courses/{key}'
        elif (key.find('lessons') != -1):
            new_directory = f'lessons/{key}'
        elif (key.find('paths') != -1):
            new_directory = f'paths/{key}'
        elif (key.find('quizzes') != -1):
            new_directory = f'quizzes/{key}'
        elif (key.find('user_state') != -1):
            file_name = key.split('/').pop()
            new_directory = f'user_state/{file_name}'
        else:
            new_directory = f'other/{key}'
    else:
        new_directory = None

    return new_directory


def move_file(bucket, key, new_directory, s3_client):
    final_new_key = f'{directory}/{new_directory}'
    copy_source = f'/{bucket}/{key}'
    print(copy_source)
    response = s3_client.copy_object(
        Bucket=new_bucket_name,
        CopySource=copy_source,
        Key=final_new_key,
        ACL="bucket-owner-full-control"
    )

    print(response)


def load_all(s3_client, now, seconds_back):
    all_files = list_files(learn_bucket, s3_client)
    all_files = list(filter(lambda file: (now - file["LastModified"]).total_seconds() <= seconds_back, all_files))

    for file in all_files:
        new_directory = get_new_directory(file["Key"])
        print(new_directory)
        if new_directory is not None:
            try:
                move_file(learn_bucket, file["Key"], new_directory, s3_client)
            except Exception as e:
                failures.append({'Key': {file['Key']},
                                 'Exception': str(e)})



def list_files(bucket, s3_client):
    key_count = 1000
    continuation_token = None
    files = []
    while key_count == 1000:
        if continuation_token is None:
            objects = s3_client.list_objects_v2(
                Bucket=bucket
            )
        else:
            objects = s3_client.list_objects_v2(
                Bucket=bucket,
                ContinuationToken=continuation_token
            )
        files.append(objects["Contents"])
        key_count = objects["KeyCount"]
        if "NextContinuationToken" in objects:
            continuation_token = objects["NextContinuationToken"]

    files = flatten(files)
    return files


def flatten(list_of_lists):
    flat_list = []
    for sublist in list_of_lists:
        for item in sublist:
            flat_list.append(item)
    return flat_list


def load_individual(event, s3_client):
   for record in event["Records"]:
       # Parse record info
       key = record['s3']['object']['key']
       bucket = record['s3']['bucket']['name']

       new_directory = get_new_directory(key)
       print(new_directory)
       if new_directory is not None:
           move_file(bucket, key, new_directory, s3_client)


def handler(event, context, local=False):
    try:
        start_time = time.time()
        now = datetime.datetime.now(datetime.timezone.utc)
        hour = now.hour
        weekday = now.weekday()
        hours_back = int(os.getenv('HOURS_BACK', '1'))
        seconds_back = hours_back * 60 * 60

        # Change to None if Verb is already your default Profile
        if local:
            aws_profile='verb'
            boto3.setup_default_session(profile_name=aws_profile)


        s3_client = boto3.client('s3')
        sns_client = boto3.client('sns', region_name='us-east-1')

        if 'Records' not in event:
            load_all(s3_client, now, seconds_back)
        else:
            load_individual(event, s3_client)

        # Gather Logging info
        error_level = 5
        error_message = 'No errors'
        job_completion_status = 'Success'
        actions = failures


    except Exception as e:
        track = traceback.format_exc()
        print(track)

        error_level = 2
        error_message = str(e)
        job_completion_status = 'Failed'
        actions = failures
    finally:
        job_logs = logs(start_time, 'Transform Learn Data',
                        job_completion_status, actions, error_level, error_message,
                        start_time, os.path.basename(__file__))
        print(job_logs)
        if job_completion_status == 'Failed' and not local:
            send_logs(json.dumps(job_logs), sns_client)


if __name__ == '__main__':
    handler('all', 'context', local=True)
