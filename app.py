from aws_cdk import (
    Duration,    
    aws_iam as iam,    
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    Stack,
    App,
    CfnOutput
)
from constructs import Construct

class CdklambdaStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

               
        # Valid Bucket
        self.valid_bucket = s3.Bucket(self, 'valid-bucket',
                                      versioned=True,
                                      bucket_name='processed-docs-bucket',
                                      encryption=s3.BucketEncryption.S3_MANAGED,
                                      block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                                      enforce_ssl=True)
        

        python_lambda_kwargs = {
            'handler': 'imggen.lambda_handler',
            'runtime': lambda_.Runtime.PYTHON_3_9,
            'timeout': Duration.minutes(10),
            'memory_size': 8192
        }

        python_lambda_kwargs_textgen = {
            'handler': 'textgen.lambda_handler',
            'runtime': lambda_.Runtime.PYTHON_3_9,
            'timeout': Duration.minutes(10),
            'memory_size': 8192
        }

        # Create Lambda functions
        trigger_imggen = lambda_.Function(self, 'file-upload-trigger', **python_lambda_kwargs,
                                          code=lambda_.Code.from_asset('lambda1'),
                                          function_name="start-imggen")

        trigger_textgen = lambda_.Function(self, 'textgen-trigger', **python_lambda_kwargs_textgen,
                                            code=lambda_.Code.from_asset('lambda2'),
                                            function_name="start-textgen")       
        

        lambda_layer = lambda_.LayerVersion(
            self, "LambdaLayer",
            code=lambda_.Code.from_asset("python"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9]
        )

        trigger_imggen.add_to_role_policy(iam.PolicyStatement(
            actions=["lambda:GetLayerVersion"],
            resources=[lambda_layer.layer_version_arn]
        ))

        trigger_textgen.add_to_role_policy(iam.PolicyStatement(
            actions=["lambda:GetLayerVersion"],
            resources=[lambda_layer.layer_version_arn]
        ))

        trigger_imggen.add_layers(lambda_layer)
        trigger_textgen.add_layers(lambda_layer)

        # Create Lambda Rest APIs
        textapi = apigateway.RestApi(
            self, 'TextApi',
            description='example api gateway',
            deploy_options={
                "stage_name": 'dev'
            },
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_headers=[
                    'Content-Type',
                    'X-Amz-Date',
                    'Authorization',
                    'X-Api-Key',
                ],
                allow_methods=['OPTIONS', 'POST']
            )
        )

        # Create Lambda Rest APIs
        imgapi = apigateway.RestApi(
            self, 'ImgApi',
            description='example api gateway',
            deploy_options={
                "stage_name": 'dev'
            },
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_headers=[
                    'Content-Type',
                    'X-Amz-Date',
                    'Authorization',
                    'X-Api-Key',
                ],
                allow_methods=['OPTIONS', 'POST']
            )
        )

        # Lambda Integration for textapi
        integration_textgen = apigateway.LambdaIntegration(
            trigger_textgen, 
            proxy=False,
            integration_responses=[
                apigateway.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ]
        )
        

        # Add POST method with response headers and models
        textapi.root.add_method(
            "POST",
            integration_textgen,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True,
                    },
                    response_models={
                        'application/json': apigateway.Model.EMPTY_MODEL,
                    }
                )
            ]
        )

        # Lambda Integration for imgapi
        integration_imggen = apigateway.LambdaIntegration(
            trigger_imggen, 
            proxy=False,
            integration_responses=[
                apigateway.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ]
        )       

        # Add POST method with response headers and models
        imgapi.root.add_method(
            "POST",
            integration_imggen,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True,
                    },
                    response_models={
                        'application/json': apigateway.Model.EMPTY_MODEL,
                    }
                )
            ]
        )

        # Grant full access to S3 and Textract for both Lambda functions
        for trigger, api in [(trigger_imggen, imgapi), (trigger_textgen, textapi)]:
            trigger.add_to_role_policy(iam.PolicyStatement(
                actions=[
                    's3:GetObject',
                    's3:PutObject',
                    's3:ListBucket',
                    's3:DeleteObject',
                    'bedrock:ListFoundationModels',
                    'bedrock:GetFoundationModel',
                    'bedrock:InvokeModel',
                    'bedrock:InvokeModelWithResponseStream'
                ],
                resources=['*']
            ))

        # Print the invoke URL in the output for both APIs
        for api, name in [(textapi, 'TextApiInvokeUrl'), (imgapi, 'ImgApiInvokeUrl')]:
            CfnOutput(self, name, value=api.url)        

app = App()
CdklambdaStack(app, "CdkbedrockStack")
app.synth()
