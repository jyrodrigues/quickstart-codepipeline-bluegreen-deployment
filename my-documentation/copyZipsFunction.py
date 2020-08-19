import json
import logging
import threading
import boto3
import cfnresponse


def copy_objects(source_bucket, dest_bucket, prefix, objects):
    s3 = boto3.client(''s3'')
    for o in objects:
        key = prefix + o
        copy_source = {
            ''Bucket'': source_bucket,
            ''Key'': key
        }
        s3.copy_object(CopySource=copy_source, Bucket=dest_bucket, Key=key)


def delete_objects(bucket):
    client = boto3.client(''s3'')
    print("Collecting data from" + bucket)
    paginator = client.get_paginator(''list_object_versions'')
    result = paginator.paginate(Bucket=bucket)
    objects = []
    for page in result:
        try:
            for k in page[''Versions'']:
                objects.append({''Key'':k[''Key''],''VersionId'': k[''VersionId'']})
            try:
                for k in page[''DeleteMarkers'']:
                    version = k[''VersionId'']
                    key = k[''Key'']
                    objects.append({''Key'': key,''VersionId'': version})
            except:
                pass
            print("deleting objects")
            client.delete_objects(Bucket=bucket,     Delete={''Objects'': objects})
           # objects = []
        except:
            pass
    print("bucket already empty")



def timeout(event, context):
    logging.error(''Execution is about to time out, sending failure response to CloudFormation'')
    cfnresponse.send(event, context, cfnresponse.FAILED, {}, None)


def handler(event, context):
    # make sure we send a failure to CloudFormation if the function is going to timeout
    timer = threading.Timer((context.get_remaining_time_in_millis() / 1000.00) - 0.5, timeout, args=[event, context])
    timer.start()

    print(''Received event: %s'' % json.dumps(event))
    status = cfnresponse.SUCCESS
    try:
        source_bucket = event[''ResourceProperties''][''SourceBucket'']
        dest_bucket = event[''ResourceProperties''][''DestBucket'']
        prefix = event[''ResourceProperties''][''Prefix'']
        objects = event[''ResourceProperties''][''Objects'']
        if event[''RequestType''] == ''Delete'':
            delete_objects(dest_bucket)
        else:
            copy_objects(source_bucket, dest_bucket, prefix, objects)
    except Exception as e:
        logging.error(''Exception: %s'' % e, exc_info=True)
        status = cfnresponse.FAILED
    finally:
        timer.cancel()
        cfnresponse.send(event, context, status, {}, None)

