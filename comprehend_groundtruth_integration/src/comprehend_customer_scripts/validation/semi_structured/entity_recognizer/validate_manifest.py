import argparse
import boto3
import json
import logging
import os
import time
import traceback

from comprehend_customer_scripts.validation.semi_structured.entity_recognizer.utils.annotation_utils import is_valid_annotation
from comprehend_customer_scripts.validation.semi_structured.entity_recognizer.utils.log_utils import log_stats
from comprehend_customer_scripts.validation.semi_structured.entity_recognizer.utils.s3_utils import get_object_content, s3_file_exists


def is_valid_annotation_ref(s3_client, ref: str, stats: dict = {}, fail_on_invalid: bool = True, is_local: bool = False):
    """Validate an annotation S3 reference."""
    if is_local:
        with open(ref, "r", encoding="utf-8", errors="strict") as annotation_file:
            annotation_content = annotation_file.read()
    else:
        annotation_content = get_object_content(s3_client=s3_client, ref=ref)
    return is_valid_annotation(
        annotation_content=annotation_content,
        annotation_name=os.path.basename(ref),
        stats=stats,
        fail_on_invalid=fail_on_invalid,
    )


def file_exists(s3_client, ref: str, is_local: bool):
    if is_local:
        return os.path.exists(ref)
    else:
        return s3_file_exists(s3_client=s3_client, ref=ref)


def is_valid_manifest_line(
    s3_client, line: str, stats: dict = {}, fail_on_invalid: bool = True, documents_local_ref=None, annotations_local_ref=None
):
    """Validate a single line in the custom EntityRecognizer manifest file."""
    is_local = bool(documents_local_ref and annotations_local_ref)
    try:
        obj = json.loads(line)
        source_ref = obj.get("source-ref")
        for key in obj.keys():
            if obj.get(key) and type(obj.get(key)) == dict and obj.get(key).get("annotation-ref"):
                annotation_ref = obj.get(key).get("annotation-ref")
                break
        if not annotation_ref:
            logging.info(f"No annotation-ref found in: {line}. Skipping.")
            if fail_on_invalid:
                return False
            return True
        if "source-ref" not in obj:
            logging.info(f"No source-ref found in: {line}. Skipping.")
            if fail_on_invalid:
                return False
            return True

        if is_local:
            source_ref = os.path.join(documents_local_ref, os.path.basename(source_ref))
            logging.info(f"Local source path: {source_ref}")
            annotation_ref = os.path.join(annotations_local_ref, os.path.basename(annotation_ref))
            logging.info(f"Local annotation path: {annotation_ref}")

        return source_ref and annotation_ref and \
            file_exists(s3_client=s3_client, ref=source_ref, is_local=is_local) and \
            file_exists(s3_client=s3_client, ref=annotation_ref, is_local=is_local) and \
            is_valid_annotation_ref(s3_client=s3_client, ref=annotation_ref, stats=stats, fail_on_invalid=fail_on_invalid, is_local=is_local)
    except Exception as e:
        logging.error(f"Failed to validate manifest line due to {e}.")
        traceback.print_tb(e.__traceback__)

    if fail_on_invalid:
        return False
    else:
        return True


def main():
    start_time = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-s3-ref", required=False, type=str, help="S3 reference to manifest file. Usage: --manifest-s3-ref s3://bucket/path/to/output.manifest")
    parser.add_argument("--manifest-local-ref", required=False, type=str, help="Local reference to manifest file. Usage: --manifest-local-ref /local/path/to/output.manifest")
    parser.add_argument("--documents-local-ref", required=False, type=str, help="Local reference to document files. Usage: --documents-local-ref /local/path/to/documents")
    parser.add_argument("--annotations-local-ref", required=False, type=str, help="Local reference to annotation files. Usage: --annotations-local-ref /local/path/to/annotations")
    parser.add_argument("--fail-on-invalid", action='store_true', help="Fail validation on invalid manifest line or annotation file. Usage: --fail-on-invalid")
    
    args = parser.parse_args()

    manifest_s3_ref = args.manifest_s3_ref
    manifest_local_ref = args.manifest_local_ref
    documents_local_ref = args.documents_local_ref
    annotations_local_ref = args.annotations_local_ref
    fail_on_invalid = bool(args.fail_on_invalid)

    s3_client = boto3.client("s3")
    if manifest_s3_ref is not None:
        manifest_s3_ref = manifest_s3_ref.rstrip("/")
        manifest_content = get_object_content(s3_client=s3_client, ref=manifest_s3_ref)
    elif manifest_local_ref is not None:
        manifest_local_ref = manifest_local_ref.rstrip(os.sep)
        with open(manifest_local_ref, "r", encoding="utf-8", errors="strict") as manifest_file:
            manifest_content = manifest_file.read()
    else:
        logging.error(f"Must provide either manifest-s3-ref or manifest-local-ref.")
        return

    """
    {
        "<annotation_file_name>": {
            "VALID": {
                "<entity_type>": {
                    "VALID": <int>,
                    "INVALID": <int>
                }
            },
            "INVALID_FORMAT": <boolean>
        }
    }
    """
    stats = {}
    for i, manifest_line in enumerate(manifest_content.splitlines()):
        if not is_valid_manifest_line(
            s3_client=s3_client, line=manifest_line, stats=stats, fail_on_invalid=fail_on_invalid,
            documents_local_ref=documents_local_ref, annotations_local_ref=annotations_local_ref
        ):
            logging.error(f"Failed validation at line {i + 1}: {manifest_line}")
            return
    log_stats(stats=stats)
    logging.info(f"Processing took {time.time() - start_time} seconds")


if __name__ == "__main__":
    main()
