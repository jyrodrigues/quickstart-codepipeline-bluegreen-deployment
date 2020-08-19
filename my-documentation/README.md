# quickstart-codepipeline-bluegreen-deployment
## Blue-Green Deployment on the AWS Cloud

This Quick Start automatically builds an architecture for blue-green deployment to an Amazon Web Services (AWS) Elastic
Beanstalk environment using AWS CodePipeline. The Quick Start creates a continuous integration/continuous delivery
pipeline for a cost-effective, fault-tolerant architecture. The deployment is automated by an AWS CloudFormation
template and takes about 15 minutes.

![Quick Start Blue-Green Architecture](
https://d1.awsstatic.com/partner-network/QuickStart/datasheets/blue-green-deployment-on-aws-architecture.64248863bedc7d6cc61f9370d66264837390a516.png)

You can deploy with or without Git to Amazon S3 integration.

This Quick Start also provides a sample Elastic Beanstalk environment for illustration and demonstration purposes only.

For architectural details, best practices, step-by-step instructions, and customization options, see the 
[deployment guide]( https://fwd.aws/ywkzA).

To post feedback, submit feature ideas, or report bugs, use the **Issues** section of this GitHub repo.
If you'd like to submit code for this Quick Start, please review the [AWS Quick Start Contributor's Kit](https://aws-quickstart.github.io/).




QuickStart Explanation
======================

To deploy this stack:

1. Login into https://console.aws.amazon.com/cloudformation;
2. Select the region on top right corner in the top bar (e.g. `US East (Ohio) us-east-2`);
3. Click on `Create stack` also on the top right (below the top bar) and select `With new resources (standard)`;
4. Leave `Prerequisite - Prepare template` as is (i.e. `Template is ready`);
5. On `Specify template` choose `Upload a template file` and upload `templates/bluegreen-deployment-master.template`
   from this repository.


# The main file: `templates/bluegreen-deployment-master.template`

This file consists of the following sections:

1. `AWSTemplateFormatVersion`: specify template version (i.e. `2010-09-09`);
2. `Description`: simple stack description;
3. `Metadata`: auxiliary text formatting and describing each GUI parameter and parameter group
4. `Conditions`: basically check if git2s3 integration is set and if it should create a new Beanstalk stack or use an
    existing one;
5. `Mappings`: just info for deploying a new PHP Beanstalk stack (the PHP stack is broken at the moment and we'll not
    use it);
6. `Parameters`: declaration and description of every parameter field available on the console GUI when creating this
    stack;
7. `Rules`: assert that there is a bucket url for Beanstalk source files (`BeanstalkSourceStageS3BucketKey`) otherwise
    errors and prevent stack creation;
8. `Resources`: sub-stacks definitions and descriptions (e.g. `GittoS3IntegrationStack`, `CopyFunctiontoS3BucketStack`).
    This is the most interesting section;
9. `Outputs`: values that will be output upon creation of this stack. Most of them are just references to
    variables/resources/sub-stacks outputs inside this template.
    N.B. `!GetAtt <resource-name>.Outputs.<output-name>` refers to output values from sub-stacks creations
    ([docs](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stack.html))

TODO: We won't.
We'll dive in what each section and value is and their purpose. After each explanation try and change those values 
and go through the process of creating a new stack (maybe without actually creating new stacks) just to get a felling of
what each value in this file does. For example we can change the `Metadata` section values and see them appearing in
`Step 2: Specify stack details`.

The `yaml` described on these templates make use of AWS CloudFormation specific syntax. Words starting with a `!` are
intrinsic functions which are explained on the [reference page
](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference.html).

Besides those, there are some values like `AWS::CloudFormation::Stack` which specify a type that can be better
understood [here](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html)
(for example the CloudFormation Stack has `Outputs` as noted on the list above which can be referenced via `!GetAtt`).

The similar `AWS::Region` value is a pseudo parameter, which refers to the previously set region on the top bar
([documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/pseudo-parameter-reference.html)).

Here we have a hierarchy with 3 nested stacks declared (and created) in the root stack itself
(`templates/bluegreen-deployment-master.template`). More about nested stacks in the [documentation
](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-nested-stacks.html).


# Nested stacks

### Copy function to S3 bucket: `templates/copyfunction-to-s3bucket.template`

TODO: for now this section is a sketch...

`!GetAtt '<resource-name>.Arn'` retrieves the "Amazon Resource Name" (ARN is a unique identifier inside AWS for
resources) for that resource, e.g. for a Lambda resource ([docs
](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html)).

`CustomResource`s:
- [documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cfn-customresource.html)
- [guide](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html)

TODO: Create a stack with just a lambda resource and output its `<lambda-resource-name>.Arn` to check that it's an URL
which can be called to trigger the function (or discover that cloudformation does more under the hood: translating the
ARN into the URL that triggers that function).


### Understanding how `S3CleanUpFunction` works

First some questions I had straight off the bat:

>
> 1. How does it know when to run the resource/lambda and when not to run? Is it based on the request type (i.e.
> `POST` vs. `DELETE`)?
> 
> *Yes!* It's based on the request type as stated on this page: [Custom resource request objects
> ](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref-requests.html) (scroll to `Custom
> resource provider request fields`). But it's not the usual request type (i.e. `POST`, `DELETE`); it's actually a
> custom request parameter named `RequestType` which CloudFormation automatically sets up with one of the following
> values: `Create`, `Update` or `Delete`. We can then parse this parameter to decide what to do inside the lambda
> function.
> 
> 2. How does CloudFormation knows when the lambda function finished execution?
> 
> CloudFormation creates a S3 bucket where the CustomResource will post/upload a SUCCESS/FAILED message. "To keep things
> simple" the CustomResource doesn't need to have credentials to change that bucket. This is done by providing a
> [presigned url](https://docs.aws.amazon.com/AmazonS3/latest/dev/PresignedUrlUploadObject.html) for that bucket to the
> lambda function.
> 
> 2. Where is this documented?
> 
> [Custom resource reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref.html)
> [Custom resource request types
> ](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref-requesttypes.html)
> There is also a section [AWS Lambda-backed custom resources
> ](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html).
> 
> 3. Is it possible to intercept a request from CloudFormation? 
> 
> Make a lambda function that just logs the request! ;) The one provided in this file already logs some info, just
> change that.
> 
> 4. Does CloudFormation instantiate *every* listed resource everytime a stack is created? I'd assume so, but is there a
>    config that allows us to specify which resources will run for each event: `create`, `update` and `delete`?
> 
> Reading the [Specification format
> ](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification-format.html)
> I don't think there is. It doesn't make sense to __not__ consider normal resources on some events. I think this kind
> of discrimination only applies for custom resources with which we trigger a function call in the middle of the stack
> creation (or deletion). Then it is more than satisfying that we only have the `RequestType` parameter as a means to
> differentiate which event we're dealing with.
>

Excerpt from the function source code:

```python
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

        #
        # LOOK HERE! <<<<<<<<<<<<<<<<<<<<<<<<<<<<
        #
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
```

About `cfnresponse` module in python code for `S3CleanUpFunction`, it has [some caveats
](https://stackoverflow.com/questions/49885243/aws-lambda-no-module-named-cfnresponse) (in this link there is also its
tiny source code).



### CodePipeline stack: `templates/codepipeline-stack.template`

**Looks like Codepipeline can be integrated directly with github!** (I.e. without using `git2s3` integration for
cloudformation). But unfortunately there is no way to grant access to a single repository: it's all or nothing. The
"official" workaround is to create another account on Github and give it access to selected repositories, then grant
CodePipeline access to this account only.
[Documentation](https://docs.aws.amazon.com/codepipeline/latest/userguide/integrations-action-type.html)

```yaml
Resources:
  BlueGreenCICDPipeline:
```

This resource has stages composed by actions, which can be in one of the following categories:
- Source
- Build
- Test
- Deploy
- Invoke
- Approval
[Documentation](https://docs.aws.amazon.com/codepipeline/latest/userguide/integrations-action-type.html)

1. The first stage has 3 `Source` actions, which will create references 
    - Beanstalk source stage bucket (*the only one polling for changes*, which will then trigger the pipeline after
      every source update);
    - Lambda for swapping environments;
    - Lambda for testing the (new) blue environment;

2. The second stage

Check the note under `Default settings for the PollForSourceChanges parameter`:
>
> Note
>
> If you create a CloudWatch Events rule or webhook, you must set the parameter
> to false to avoid triggering the pipeline more than once.
> 
From which I come to the conclusion that it *is* what triggers the pipeline!
[Documentation](https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#action-requirements)

So far
------

- Understood `templates/bluegreen-deployment-master.template` structure and nested stacks hierarchy;
- Understood `S3CleanUpFunction` inside `templates/copyfunction-to-s3bucket.template`


Next steps
----------

- Re-read what you have written the day before. Re-write what you don't understand or add stuff that's missing
- Fully understand `templates/copyfunction-to-s3bucket.template` (almost there)
- Fully understand `templates/codepipeline-stack.template`
- Fully understand `templates/elasticbeanstalk-sample.template`

- Have all this understanding documented: explaining AWS QuickStart
- Remake all stacks/templates to create a much simpler version that
    - Always has git2s3 integration
    - Always has a running elasticbeanstalk app
    - Doesn't care about sample elasticbeanstalk app
    - Explains in a much better manner what each parameter entry is (i.e. what it will be used for) (e.g. "this value
      will compose the URI with which CloudFormation can copy the source code and start the elasticbeanstalk app").

- *Add custom domain with HTTPS*
    - Add this to your documentation



[Amazon on Continuout Delivery (and Continuous Integration)](
https://d0.awsstatic.com/whitepapers/DevOps/practicing-continuous-integration-continuous-delivery-on-AWS.pdf)

[Amazon on Blue-Green deploys](https://d0.awsstatic.com/whitepapers/AWS_Blue_Green_Deployments.pdf)
























































