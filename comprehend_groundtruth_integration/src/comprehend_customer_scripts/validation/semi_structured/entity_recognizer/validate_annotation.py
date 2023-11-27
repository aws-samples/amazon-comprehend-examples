import argparse
import boto3
import logging
import os

from comprehend_customer_scripts.validation.semi_structured.entity_recognizer.utils.annotation_utils import is_valid_annotation
from comprehend_customer_scripts.validation.semi_structured.entity_recognizer.utils.log_utils import log_stats
from comprehend_customer_scripts.validation.semi_structured.entity_recognizer.utils.s3_utils import get_object_content


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotation-s3-ref", required=False, type=str, help="S3 reference to annotation file. Usage: --annotation-s3-ref s3://bucket/path/to/annotation.json")
    parser.add_argument("--annotation-local-ref", required=False, type=str, help="Local reference to annotation file. Usage: --annotation-local-ref /local/path/to/annotation.json")
    args = parser.parse_args()

    annotation_s3_ref = args.annotation_s3_ref
    annotation_local_ref = args.annotation_local_ref

    s3_client = boto3.client("s3")
    if annotation_s3_ref is not None:
        annotation_s3_ref = annotation_s3_ref.rstrip("/")
        annotation_content = get_object_content(s3_client=s3_client, ref=annotation_s3_ref)
        annotation_name = os.path.basename(annotation_s3_ref)
    elif annotation_local_ref is not None:
        annotation_local_ref = annotation_local_ref.rstrip(os.sep)
        with open(annotation_local_ref, "r", encoding="utf-8", errors="strict") as manifest_file:
            annotation_content = manifest_file.read()
        annotation_name = os.path.basename(annotation_local_ref)
    else:
        logging.error(f"Must provide either annotation-s3-ref or annotation-local-ref.")
        return

    stats = {}
    if not is_valid_annotation(
        annotation_content=annotation_content,
        annotation_name=annotation_name,
        stats=stats
    ):
        logging.error("Validation failed.")
        return

    log_stats(stats=stats)


if __name__ == "__main__":
    main()
