from urllib.parse import urlparse


def bucket_key_from_s3_uri(s3_path: str):
    """Get bucket and key from s3 URL."""
    o = urlparse(s3_path, allow_fragments=False)
    bucket = o.netloc
    key = o.path.lstrip('/')
    return bucket, key


def get_object_content(s3_client, ref: str):
    """Get UTF-8 content from an S3 object."""
    bucket, path = bucket_key_from_s3_uri(ref)
    return s3_client.get_object(Bucket=bucket, Key=path).get('Body').read().decode('utf-8')


def get_bucket_and_objects_in_folder(s3_client, ref: str, is_file=False):
    """Get bucket and objects in folder prefixed with given reference."""
    bucket, key = bucket_key_from_s3_uri(ref)
    if not is_file:
        key = key + ('' if key.endswith('/') else '/')
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=key)
    all_objs = []
    for page in pages:
        all_objs.extend(page.get('Contents', []))            
    return bucket, sorted([obj for obj in all_objs if not obj["Key"].endswith("/")], key=lambda obj: obj["Key"])


def s3_file_exists(s3_client, ref: str):
    bucket, objs = get_bucket_and_objects_in_folder(s3_client=s3_client, ref=ref, is_file=True)
    return len(objs) and f"s3://{bucket}/{objs[0]['Key']}" == ref
