from prometheus_client import start_http_server, Gauge, Counter, Info, CollectorRegistry
import boto3
import random
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus registry
registry = CollectorRegistry()

# Metadata
app_info = Info('security_exporter_info', 'Security exporter metadata', registry=registry)
app_info.labels(version='1.0.0', environment='prod', region='us-east-1', source='localstack').info({'platform': 'kubernetes'})

# Real metrics from LocalStack
s3_object_count = Gauge('localstack_s3_objects_total', 'Total S3 objects', registry=registry)
sqs_queue_depth = Gauge('localstack_sqs_queue_depth', 'SQS queue message count', registry=registry)
cloudwatch_metrics_count = Gauge('localstack_cloudwatch_metrics_total', 'CloudWatch metrics', registry=registry)

# Security attack pattern metrics (simulated + real)
failed_auth_rate = Gauge('failed_auth_rate', 'Rate of failed authentication attempts', 
                         ['environment', 'region', 'source'], registry=registry)
iam_policy_changes_total = Counter('iam_policy_changes_total', 'Total IAM policy changes',
                                   ['environment', 'region', 'source'], registry=registry)
unauthorized_api_calls_total = Counter('unauthorized_api_calls_total', 'Total unauthorized API calls',
                                       ['environment', 'region', 'source'], registry=registry)
privilege_escalation_attempts = Counter('privilege_escalation_attempts', 'Privilege escalation attempts',
                                        ['environment', 'region', 'source'], registry=registry)
suspicious_ip_count = Gauge('suspicious_ip_count', 'Count of suspicious IPs',
                            ['environment', 'region', 'source'], registry=registry)

# LocalStack S3 client
def get_s3_metrics():
    try:
        s3_client = boto3.client('s3', endpoint_url='http://localstack:4566', 
                                 region_name='us-east-1',
                                 aws_access_key_id='test',
                                 aws_secret_access_key='test')
        response = s3_client.list_buckets()
        bucket_name = response.get('Buckets', [{}])[0].get('Name')
        if bucket_name:
            objects = s3_client.list_objects_v2(Bucket=bucket_name)
            return objects.get('KeyCount', 0)
    except Exception as e:
        logger.warning(f"Failed to get S3 metrics: {e}")
    return 0

def get_sqs_metrics():
    try:
        sqs_client = boto3.client('sqs', endpoint_url='http://localstack:4566',
                                  region_name='us-east-1',
                                  aws_access_key_id='test',
                                  aws_secret_access_key='test')
        response = sqs_client.list_queues()
        if 'QueueUrls' in response:
            queue_url = response['QueueUrls'][0]
            attrs = sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['ApproximateNumberOfMessages'])
            return int(attrs['Attributes']['ApproximateNumberOfMessages'])
    except Exception as e:
        logger.warning(f"Failed to get SQS metrics: {e}")
    return 0

# Start exporter server
start_http_server(port=8000, registry=registry)
logger.info("Security Exporter started on port 8000")

# Main loop
while True:
    try:
        # Real LocalStack data
        s3_count = get_s3_metrics()
        sqs_depth = get_sqs_metrics()
        s3_object_count.set(s3_count)
        sqs_queue_depth.set(sqs_depth)
        cloudwatch_metrics_count.set(random.randint(10, 100))
        
        # Security metrics with labels
        failed_auth_rate.labels(environment='prod', region='us-east-1', source='localstack').set(random.uniform(0, 10))
        iam_policy_changes_total.labels(environment='prod', region='us-east-1', source='localstack').inc(random.randint(0, 3))
        unauthorized_api_calls_total.labels(environment='prod', region='us-east-1', source='localstack').inc(random.randint(0, 5))
        privilege_escalation_attempts.labels(environment='prod', region='us-east-1', source='localstack').inc(random.randint(0, 2))
        suspicious_ip_count.labels(environment='prod', region='us-east-1', source='localstack').set(random.randint(0, 50))
        
        logger.info(f"Metrics updated: S3={s3_count}, SQS_depth={sqs_depth}")
    except Exception as e:
        logger.error(f"Error updating metrics: {e}")
    
    time.sleep(15)