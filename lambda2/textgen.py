import json
import boto3
import http
import os
import logging
from botocore.exceptions import ClientError

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

region_name = os.getenv("region", "us-east-1")
model_id = os.getenv("model_id", "anthropic.claude-v2")
bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name=region_name)


def lambda_handler(event, context):
    accept = 'application/json'
    content_type = 'application/json'
    prompt = event.get("input")  # Using get() method to avoid KeyErrors
    print(prompt)

    if not prompt:
        return {
            "statusCode": http.HTTPStatus.BAD_REQUEST,
            "body": json.dumps({"error": "Input prompt is missing"})
        }

    body = json.dumps(
        {
            "prompt": prompt,
            "max_tokens_to_sample": 4096,
            "temperature": 0.5,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": ["\\n\\nHuman:"]
        }
    )
    try:
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=model_id,
            accept=accept,
            contentType=content_type,
        )

        response_body = json.loads(response.get("body").read())
        answer = response_body.get("completion")

        return {
            "statusCode": http.HTTPStatus.OK,
            "body": json.dumps({"Answer": answer}),
        }
    except ClientError as e:
        error_message = f"Exception raised while execution: {e}"
        LOG.error(error_message)
        
        return {
            "statusCode": http.HTTPStatus.INTERNAL_SERVER_ERROR,
            "body": json.dumps({"error": "Internal Server Error", "details": error_message})
        }
