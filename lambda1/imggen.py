import json
import boto3
import http
import os
import logging
from botocore.exceptions import ClientError
from PIL import Image
import io
import base64
import random

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

region_name = os.getenv("region", "us-east-1")
s3_bucket = "processed-docs-bucket"
model_id = os.getenv("model_id", "stability.stable-diffusion-xl-v0")
style_preset = os.getenv("style_preset", "photographic")  # digital-art, cinematic

# Bedrock client used to interact with APIs around models
bedrock = boto3.client(service_name="bedrock", region_name=region_name)

# Bedrock Runtime client used to invoke and question the models
bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name=region_name)

# S3 client used to interact with S3 buckets
s3_client = boto3.client('s3')

def generate_signed_url(s3_bucket, s3_key, expiration=3600):
    s3_client = boto3.client('s3')
    url = s3_client.generate_presigned_url('get_object',
                                          Params={'Bucket': s3_bucket, 'Key': s3_key},
                                          ExpiresIn=expiration)
    return url

def generate_signed_url(s3_bucket, s3_key, expiration=3600):
    s3_client = boto3.client('s3')
    url = s3_client.generate_presigned_url('get_object',
                                          Params={'Bucket': s3_bucket, 'Key': s3_key},
                                          ExpiresIn=expiration)
    return url

def lambda_handler(event, context):
    accept = 'application/json'
    content_type = 'application/json'
    prompt = event["input"]

    negative_prompts = [
        "poorly rendered",
        "poor background details",
        "poorly drawn",
        "disfigured features",
    ]
    try:
        request = json.dumps({
            "text_prompts": (
                [{"text": prompt, "weight": 1.0}]
                + [{"text": negprompt, "weight": -1.0} for negprompt in negative_prompts]
            ),
            "cfg_scale": 5,
            "seed": 5450,
            "steps": 70,
            "style_preset": style_preset,
        })

        response = bedrock_runtime.invoke_model(body=request, modelId=model_id)
        # LOG.info(response)

        response_body = json.loads(response.get("body").read())
        LOG.info(f"Response body: {response_body}")

        base_64_img_str = response_body["artifacts"][0].get("base64")
        LOG.info(f"Base string is {base_64_img_str}")

        # Convert the base64 encoded data to an image
        generated_img = Image.open(io.BytesIO(base64.decodebytes(bytes(base_64_img_str, "utf-8"))))
        temp_path = "/tmp/generatedFilePath"
        temp_file_name = 'generatedImage' + '_' + str(random.randint(1, 100000000000000000)) + '.png'
        temp_file_path = temp_path + "/" + temp_file_name

        # Save the file temporarily in Lambda memory
        os.makedirs(temp_path, exist_ok=True)
        generated_img.save(temp_file_path)

        # Upload the generated image to S3 bucket
        s3_key = f"{temp_file_name}"
        s3_client.upload_file(temp_file_path, s3_bucket, s3_key)

        # Generate a signed URL for the S3 object
        expiration_time = 3600  # seconds
        print(expiration_time)  # Add this line to print the expiration time
        signed_url = generate_signed_url(s3_bucket, s3_key, expiration=expiration_time)

        return {
            "statusCode": http.HTTPStatus.OK,
            "body": json.dumps({"download_url": signed_url})
        }

    except ClientError as e:
        LOG.error(f"Exception raised while execution and the error is {e}")

        return {
            "statusCode": http.HTTPStatus.INTERNAL_SERVER_ERROR,
            "body": json.dumps({"error": "Internal Server Error", "details": e})
        }
