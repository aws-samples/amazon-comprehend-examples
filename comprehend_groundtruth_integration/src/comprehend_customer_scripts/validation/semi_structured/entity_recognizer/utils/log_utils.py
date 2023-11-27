import logging


def log_stats(stats: dict):
    dataset_level_stats = {"annotation_files_with_format_issues": [], "entity_stats": {}, "annotation_files_containing_invalid_entities": {}}
    annotation_file_level_stats = {}
    for annotation_name in stats.keys():
        if stats[annotation_name]["INVALID_FORMAT"]:
            dataset_level_stats["annotation_files_with_format_issues"].append(annotation_name)

        valid_annotation_stats = stats[annotation_name]["VALID"]
        for entity_type in valid_annotation_stats.keys():
            if annotation_name not in annotation_file_level_stats:
                annotation_file_level_stats[annotation_name] = {}
            if entity_type not in annotation_file_level_stats[annotation_name]:
                annotation_file_level_stats[annotation_name][entity_type] = {"VALID": 0, "INVALID": 0}
            annotation_file_level_stats[annotation_name][entity_type]["VALID"] = valid_annotation_stats[entity_type]["VALID"]
            annotation_file_level_stats[annotation_name][entity_type]["INVALID"] = valid_annotation_stats[entity_type]["INVALID"]

            dataset_level_entity_stats = dataset_level_stats["entity_stats"]
            if entity_type not in dataset_level_entity_stats:
                dataset_level_entity_stats[entity_type] = {"VALID": 0, "INVALID": 0}
            dataset_level_entity_stats[entity_type]["VALID"] += annotation_file_level_stats[annotation_name][entity_type]["VALID"]
            dataset_level_entity_stats[entity_type]["INVALID"] += annotation_file_level_stats[annotation_name][entity_type]["INVALID"]

            if annotation_file_level_stats[annotation_name][entity_type]["INVALID"]:
                annotation_files_containing_invalid_entities = dataset_level_stats["annotation_files_containing_invalid_entities"]
                if entity_type not in annotation_files_containing_invalid_entities:
                    annotation_files_containing_invalid_entities[entity_type] = {}
                if annotation_name not in annotation_files_containing_invalid_entities[entity_type]:
                    annotation_files_containing_invalid_entities[entity_type][annotation_name] = 0

                annotation_files_containing_invalid_entities[entity_type][annotation_name] += 1

    logging.info(f"DATASET AGGREGATE STATS")
    logging.info(f"annotation_files_with_format_issues: {list(dataset_level_stats['annotation_files_with_format_issues'])}")
    logging.info(f"annotation_files_containing_invalid_entities: {dataset_level_stats['annotation_files_containing_invalid_entities']}")
    logging.info(f"{dataset_level_stats['entity_stats']}\n")

    logging.info(f"ANNOTATION FILE AGGREGATE STATS")
    logging.info(f"{annotation_file_level_stats}\n")
