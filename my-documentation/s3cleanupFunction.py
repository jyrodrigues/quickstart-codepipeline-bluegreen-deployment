import json
import logging
import threading
import boto3
import cfnresponse
client = boto3.client('s3')


def delete_NonVersionedobjects(bucket):
    print("Collecting data from" + bucket)
    paginator =     client.get_paginator('list_objects_v2')
    result = paginator.paginate(Bucket=bucket)
    objects = []
    for page in result:
        try:
            for k in page['Contents']:
                objects.append({'Key': k['Key']})
                print("deleting objects")
                client.delete_objects(Bucket=bucket, Delete={'Objects':objects})
                objects = []
        except:
            pass
            print("bucket is already empty")

def delete_versionedobjects(bucket):
    print("Collecting data from" + bucket)
    paginator = client.get_paginator('list_object_versions')
    result = paginator.paginate(Bucket=bucket)
    objects = []
    for page in result:
        try:
            for k in page['Versions']:
                objects.append({'Key':k['Key'],'VersionId': k['VersionId']})
            try:
                for k in page['DeleteMarkers']:
                    version = k['VersionId']
                    key = k['Key']
                    objects.append({'Key': key,'VersionId': version})
            except:
                pass
            print("deleting objects")
            client.delete_objects(Bucket=bucket, Delete={'Objects':objects})
           # objects = []
        except:
            pass
    print("bucket already empty")



def timeout(event, context):
    logging.error('Execution is about to time out, sending failureresponse to CloudFormation')
    cfnresponse.send(event, context, cfnresponse.FAILED, {}, None)


def handler(event, context):
    # make sure we send a failure to CloudFormation if the function is going to timeout
    timer = threading.Timer((context.get_remaining_time_in_millis() / 1000.00) - 0.5, timeout, args=[event, context])
    timer.start()

    print('Received event: %s' % json.dumps(event))
    status = cfnresponse.SUCCESS
    try:
        dest_bucket = event['ResourceProperties']['DestBucket']
        if event['RequestType'] == 'Delete':
            CheckifVersioned = client.get_bucket_versioning(Bucket=dest_bucket)
            print CheckifVersioned
            if 'Status' in CheckifVersioned:
                print CheckifVersioned['Status']
                print ("This is a versioned Bucket")
                delete_versionedobjects(dest_bucket)
            else:
                print "This is not a versioned bucket"
                delete_NonVersionedobjects(dest_bucket)
        else:
            print("Nothing to do")
    except Exception as e:
        logging.error('Exception: %s' % e, exc_info=True)
        status = cfnresponse.FAILED
    finally:
        timer.cancel()
        cfnresponse.send(event, context, status, {}, None)

