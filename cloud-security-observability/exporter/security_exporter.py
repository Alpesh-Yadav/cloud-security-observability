import time
import random
import logging

from prometheus_client import start_http_server, Gauge
import boto3
import botocore

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

ENDPOINT_URL = 'http://localhost:4566'
LABEL_KEYS = ['environment', 'region', 'source']
LABEL_VALUES = {'environment': 'prod', 'region': 'us-east-1', 'source': 'localstack'}

s3_object_count = Gauge('security_exporter_s3_object_count',
                        'Number of objects in S3 bucket', LABEL_KEYS)
sqs_queue_depth = Gauge('security_exporter_sqs_queue_depth',
                        'Number of visible messages in SQS queue', LABEL_KEYS)
cloudwatch_metric_count = Gauge('security_exporter_cloudwatch_metric_count',
                                'Count of CloudWatch metrics available from LocalStack', LABEL_KEYS)
failed_auth_rate = Gauge('security_exporter_failed_auth_rate',
                         'Simulated failed authentication rate', LABEL_KEYS)
iam_policy_changes_total = Gauge(
    'security_exporter_iam_policy_changes_total', 'Simulated total IAM policy changes', LABEL_KEYS)
unauthorized_api_calls_total = Gauge(
    'security_exporter_unauthorized_api_calls_total', 'Simulated unauthorized API calls total', LABEL_KEYS)
privilege_escalation_attempts = Gauge(
    'security_exporter_privilege_escalation_attempts', 'Simulated privilege escalation attempts', LABEL_KEYS)
suspicious_ip_count = Gauge('security_exporter_suspicious_ip_count',
                            'Simulated suspicious IP count', LABEL_KEYS)


def label_values():
    return [LABEL_VALUES[k] for k in LABEL_KEYS]


def get_localstack_client(service_name):
    return boto3.client(
        service_name,
        endpoint_url=ENDPOINT_URL,
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test',
    )


def update_localstack_metrics():
    s3 = get_localstack_client('s3')
    sqs = get_localstack_client('sqs')
    cw = get_localstack_client('cloudwatch')

    objects = s3.list_objects_v2(Bucket='security-logs-bucket')
    s3_object_count.labels(*label_values()).set(objects.get('KeyCount', 0))

    queue_url = sqs.get_queue_url(QueueName='alert-queue')['QueueUrl']
    attrs = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=[
                                     'ApproximateNumberOfMessagesVisible'])
    sqs_queue_depth.labels(
        *label_values()).set(int(attrs['Attributes'].get('ApproximateNumberOfMessagesVisible', 0)))

    metrics = cw.list_metrics(Namespace='AWS/SQS')
    cloudwatch_metric_count.labels(*label_values()).set(len(metrics.get('Metrics', [])))


def update_simulated_metrics():
    s3_object_count.labels(*label_values()).set(random.randint(0, 10))
    sqs_queue_depth.labels(*label_values()).set(random.randint(0, 15))
    cloudwatch_metric_count.labels(*label_values()).set(random.randint(0, 5))
    failed_auth_rate.labels(*label_values()).set(random.uniform(0.1, 3.5))
    iam_policy_changes_total.labels(*label_values()).set(random.randint(0, 6))
    unauthorized_api_calls_total.labels(*label_values()).set(random.randint(0, 8))
    privilege_escalation_attempts.labels(*label_values()).set(random.randint(0, 4))
    suspicious_ip_count.labels(*label_values()).set(random.randint(0, 12))


def update_attack_metrics():
    failed_auth_rate.labels(*label_values()).set(random.uniform(0.1, 3.5))
    iam_policy_changes_total.labels(*label_values()).set(random.randint(0, 6))
    unauthorized_api_calls_total.labels(*label_values()).set(random.randint(0, 8))
    privilege_escalation_attempts.labels(*label_values()).set(random.randint(0, 4))
    suspicious_ip_count.labels(*label_values()).set(random.randint(0, 12))


def main():
    start_http_server(8000)
    logger.info('Exporter listening on port 8000')
    while True:
        try:
            update_localstack_metrics()
            update_attack_metrics()
        except botocore.exceptions.BotoCoreError as exc:
            logger.warning('LocalStack unavailable, fallback to simulated metrics: %s', exc)
            update_simulated_metrics()
        except Exception as exc:
            logger.warning('Error fetching LocalStack data, fallback to simulated metrics: %s', exc)
            update_simulated_metrics()
        time.sleep(15)


if __name__ == '__main__':
    main()
