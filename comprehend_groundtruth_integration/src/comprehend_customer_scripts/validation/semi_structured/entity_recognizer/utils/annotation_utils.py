import json
import logging

from comprehend_customer_scripts.validation.semi_structured.entity_recognizer.annotation_model import AnnotationSchema


def is_valid_entities(annotation_json: dict, annotation_name: str, stats: dict = {}, fail_on_invalid: bool = True):
    """Validate if all entities are correctly referenced by their line and word blocks and there are no duplicates."""
    blocks_map = {block["Id"]: block for block in annotation_json["Blocks"]}
    block_reference_id_set = set()
    annotation_stats_valid = stats[annotation_name]["VALID"]
    for entity in annotation_json["Entities"]:
        if entity["Type"] not in annotation_stats_valid:
            annotation_stats_valid[entity["Type"]] = {"VALID": 0, "INVALID": 0}

        line_block_strings = [] 
        word_block_strings = []
        block_reference_ids = []
        for block_reference in entity["BlockReferences"]:
            block_reference_ids.append(block_reference["BlockId"])
            line_block = blocks_map.get(block_reference["BlockId"])
            if not line_block:
                log_content = f"Line block not found for line block id: {block_reference['BlockId']}"
                logging.error(log_content)
                continue
            line_block_strings.append(line_block["Text"][block_reference["BeginOffset"]:block_reference["EndOffset"]])

            for child_block_reference in block_reference["ChildBlocks"]:
                block_reference_ids.append(child_block_reference["ChildBlockId"])
                word_block = blocks_map.get(child_block_reference["ChildBlockId"])
                if not word_block:
                    log_content = f"Word block not found for word block id: {block_reference['BlockId']}"
                    logging.error(log_content)
                    continue
                word_block_strings.append(word_block["Text"][child_block_reference["BeginOffset"]:child_block_reference["EndOffset"]])
        block_reference_id = "-".join(block_reference_ids)
        is_duplicate_entity = block_reference_id in block_reference_id_set
        if is_duplicate_entity:
            log_content = f"Duplicate entity: {json.dumps(entity)}"
            logging.error(log_content)
            continue
        if " ".join(line_block_strings) != entity["Text"] or " ".join(word_block_strings) != entity["Text"]:
            log_content = f"For annotation: {annotation_name}, failed to validate entity: {json.dumps(entity)}, " \
                            f"using line_block_strings: {line_block_strings} and word_block_strings: {word_block_strings}"
            logging.error(log_content)
            annotation_stats_valid[entity["Type"]]["INVALID"] += 1

            if fail_on_invalid:
                return False
        block_reference_id_set.add(block_reference_id)

        annotation_stats_valid[entity["Type"]]["VALID"] += 1

    return True


def is_valid_annotation(annotation_content: str, annotation_name: str, stats: dict = {}, fail_on_invalid: bool = True):
    """Validate an annotation."""
    if annotation_name not in stats:
        stats[annotation_name] = {"VALID": {}, "INVALID_FORMAT": False}
    try:
        annotation_json = json.loads(annotation_content)
        AnnotationSchema().load(annotation_json)
    except Exception as e:
        logging.error(f"Failed to validate annotation schema {annotation_name} due to {e}.")
        stats[annotation_name]["INVALID_FORMAT"] = True

        if fail_on_invalid:
            return False
        return True

    return is_valid_entities(
        annotation_json=annotation_json, annotation_name=annotation_name, stats=stats, fail_on_invalid=fail_on_invalid
    )
