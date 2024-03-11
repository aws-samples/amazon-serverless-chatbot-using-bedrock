# Serverless Chatbot


![bedrockorig](https://github.com/paulkannan/serverlesschatbot/assets/46925641/0672ac26-baf4-4232-b6ce-b2b7c0ea0f2c)


Overview

This architecture is designed to provide a serverless, efficient, and automated solution to interact with Amazon Bedrock. Users can interact with the chatbot deployed at Amplify frontend which in turn will invoke API endpoints and Lambda to interact with Bedrock. The chatbot can support following functions:

- Have conversations on a variety of topics
- Provide information from web searches
- Make recommendations and give opinions
- Schedule meetings and set reminders
- Translate text between languages
- Define words and concepts
- Summarize long passages of text
- Proofread text for grammar and spelling errors
- Solve basic math problems
- Tell jokes and play word games
- Provide companionship through conversation
- Text to image generation

How to Use:

Deploy the Stack: Use the AWS CDK to deploy the stack, which creates all the defined resources.

Invoke APIs: Obtain the generated invoke URLs from the CDK outputs for both the text and image processing APIs and paste it in api endpoints in script.js . 
                        
            // API endpoint for image processing
            const imageApiEndpoint = " ";
            // Original API endpoint
            const defaultApiEndpoint = " ";


In the webapp folder, Compress index.html, script.js, images and style.css into index.zip. 
Open AWS Amplify console and do the following:
  - Select host web app
  - Select Deploy without Git provider
  - Type in your app name and environment name (Dev, Prod, UAT)
  - zip the webapp folder as index.zip in your local machine
  - Select choose files and upload index.zip
  - The app will get deployed and you can find domain URL under Hosting Environments of your App
  - Click the URL and you can view the app screen below     
![image](https://github.com/paulkannan/serverlesschatbot/assets/46925641/f870dbab-b529-4ea7-9c00-3e3b927c8a54)

Submit Data: 
Use HTTP POST requests to submit text or image data to the respective API endpoint.
The APIs trigger the corresponding Lambda functions (trigger_imggen or trigger_textgen).

Processing:  Lambda functions process the submitted data, utilizing the specified runtime and associated dependencies from the Lambda layer.

Storage: Processed data is stored in the versioned S3 bucket (valid_bucket).

Access Control: The S3 bucket has strict access controls, and Lambda functions have specific permissions for secure data processing.

Monitoring and Logging: Leverage AWS CloudWatch for monitoring Lambda function performance and logging.

Customization: Modify Lambda function code, layer contents, or API configurations based on specific processing needs.

The cdk.json file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project. The initialization process also creates a virtualenv within this project, stored under the .venv directory. To create the virtualenv it assumes that there is a python3 (or python for Windows) executable in your path with access to the venv package. If for any reason the automatic creation of the virtualenv fails, you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```
After installing dependcies, Users should download boto3 and PIL python libraries and upload it as a custom layer for imggen.py lambda function. Same applicable for textgen.py as well

```
$ zip -r python.zip python
```
At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```
Yyou can bootstrap the stack.

```
$ cdk bootstrap
```
You can now deploy the CDK Stack

```
$ cdk deploy
```
To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

```
Useful commands
cdk ls list all stacks in the app
cdk synth emits the synthesized CloudFormation template
cdk deploy deploy this stack to your default AWS account/region
cdk diff compare deployed stack with current state
cdk docs open CDK documentation
To clean up the resources created
```

To clean up the resources created

```
$ cdk destroy
```

