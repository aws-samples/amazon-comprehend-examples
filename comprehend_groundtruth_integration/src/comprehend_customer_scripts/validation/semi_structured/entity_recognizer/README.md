## Install dependencies

1. Install Python modules
  - `boto3`
  - `marshmallow`

## Documentation

### Prerequisite
1. `cd amazon-comprehend-examples/comprehend_groundtruth_integration/src`

### Scripts

1. Includes a script to validate a Comprehend custom Entity Recognizer training manifest for semi-structured. The following will be detailed:
    1. The source reference is given and exists in S3.
    2. The annotation reference is given and exists in S3.
    3. The annotation file schema is valid and all entities can be referenced in the annotation file's data.
        a. Annotation files contain a "Blocks" key which contains a list of https://docs.aws.amazon.com/comprehend/latest/APIReference/API_Block.html.
        b. Annotation files contain a "Blocks" key which contains a list of https://docs.aws.amazon.com/comprehend/latest/APIReference/API_Entity.html.
    4. All entities and their counts will be logged.
        a. Valid entity counts will be logged.
        b. Invalid entity counts will be logged. An invalid entity consists of an entity which cannot be located within the annotation file's Blocks.
    5. There will be no failure on validation unless `--fail-on-invalid` is also passed in the script call.
    6. Local directories for documents/source files and annotations can be used with `--document-local-ref` and `--annotations-local-ref`, respectively, to avoid S3 calls.

    ### Example script calls and outputs

    S3 manifest example call:
    ```
    python -m comprehend_customer_scripts.validation.semi_structured.entity_recognizer.validate_manifest --manifest-s3-ref s3://bucket/path/to/output.manifest
    ```

    Local manifest example call:
    ```
    python -m comprehend_customer_scripts.validation.semi_structured.entity_recognizer.validate_manifest --manifest-local-ref /local/path/to/output.manifest
    ```

    Example output:
    ```
    INFO: root: DATASET AGGREGATE STATS
    INFO: root: annotation_files_with_format_issues: []
    INFO: root: annotation_files_containing_invalid_entities: {
        "OFFERING_PRICE": {
            "sreg-0063475c-b633-43a5-8709-f19e47a6b38c-1-e3374cd4-ann.json": 2,
            ...
        },
        ...
    }
    INFO: root: {
        'OFFERING_PRICE': {
            'VALID': 721,
            'INVALID': 0
        },
        'OFFERED_SHARES': {
            'VALID': 378,
            'INVALID': 0
        },
        'COMMISSION_UNDERWRITER': {
            'VALID': 88,
            'INVALID': 0
        },
        'COMMISSION_OTHER': {
            'VALID': 74,
            'INVALID': 0
        },
        'PROCEEDS': {
            'VALID': 64,
            'INVALID': 0
        }
    }
    INFO: root: ANNOTATION FILE AGGREGATESTATS INFO: root: {
        'sreg-0063475c-b633-43a5-8709-f19e47a6b38c-1-e3374cd4-ann.json': {
            'OFFERING_PRICE': {
                'VALID': 4,
                'INVALID': 0
            },
            'OFFERED_SHARES': {
                'VALID': 2,
                'INVALID': 0
            }
        },
        ...
    }
    ```
    ### Failure examples

    1. Failure validation example output in the case of an INVALID entity:
        ```
        {
            ...,
            "sreg-0063475c-b633-43a5-8709-f19e47a6b38c-1-e3374cd4-ann.json": {
                "INVALID": 1,
                "VALID": 0,
            },
            ...
        }
        ```
        The entity's Text "$4.10" does not match the text "$4.20" tracked in the referenced Block(s).

        Entity:
        ```
        {
            "BlockReferences": [
                {
                    "BlockId": "089cda72-86ff-494a-8a29-ed0ab39e925b",
                    "ChildBlocks": [
                        {
                            "BeginOffset": 0,
                            "EndOffset": 5,
                            "ChildBlockId": "f4dba2cf-ad51-430e-9a38-8f9554d1b094"
                        }
                    ],
                    "BeginOffset": 0,
                    "EndOffset": 5
                }
            ],
            "Text": "$4.10",
            "Type": "OFFERING_PRICE",
            "Score": 1,
            "Properties": {
                "OFFERING_PRICE-SUBTYPE": "PER_SHARE"
            }
        }
        ```

        Blocks:
        ``````
        {
            "BlockType": "LINE",
            "Id": "089cda72-86ff-494a-8a29-ed0ab39e925b",
            "Text": "$4.20",
            "Geometry": {
                "BoundingBox": {
                    "Width": 0.03611570969223976,
                    "Top": 0.15035110712051392,
                    "Left": 0.5531672835350037,
                    "Height": 0.010543919168412685
                },
                "Polygon": [
                    {
                        "X": 0.5531672835350037,
                        "Y": 0.15035110712051392
                    },
                    {
                        "X": 0.5892829932272434,
                        "Y": 0.15035110712051392
                    },
                    {
                        "X": 0.5892829932272434,
                        "Y": 0.1608950262889266
                    },
                    {
                        "X": 0.5531672835350037,
                        "Y": 0.1608950262889266
                    }
                ]
            },
            "Relationships": [
                {
                    "Ids": [
                        "f4dba2cf-ad51-430e-9a38-8f9554d1b094"
                    ],
                    "Type": "CHILD"
                }
            ],
            "Page": 1
        },
        {
            "BlockType": "WORD",
            "Id": "f4dba2cf-ad51-430e-9a38-8f9554d1b094",
            "Text": "$4.20",
            "Geometry": {
                "BoundingBox": {
                    "Width": 0.03611570969223976,
                    "Top": 0.15035110712051392,
                    "Left": 0.5531672835350037,
                    "Height": 0.010543919168412685
                },
                "Polygon": [
                    {
                        "X": 0.5531672835350037,
                        "Y": 0.15035110712051392
                    },
                    {
                        "X": 0.5892829932272434,
                        "Y": 0.15035110712051392
                    },
                    {
                        "X": 0.5892829932272434,
                        "Y": 0.1608950262889266
                    },
                    {
                        "X": 0.5531672835350037,
                        "Y": 0.1608950262889266
                    }
                ]
            },
            "Relationships": [],
            "Page": 1
        }
        ```
    2. If `--fail-on-invalid` argument is passed in script call, failure validation example output in the case of the `Version` attribute not existing within an annotation file:
        ```
        ERROR:root:Failed to validate annotation schema s3://bucket/folder/annotations/annotation.json due to {'Version': ['Missing data for required field.']}.
        ERROR:root:Failed validation at line 8: {"source-ref": "s3://bucket/folder/pdfs/source.pdf", "page": "1", "metadata": {"pages": "1", "use-textract-only": true, "labels": ["COMMISSION_OTHER", "COMMISSION_UNDERWRITER", "OFFERING_PRICE", "OFFERED_SHARES", "PROCEEDS"]}, "primary-annotation-ref": null, "secondary-annotation-ref": null, "semi-structured-job": {"annotation-ref": "s3://bucket/folder/annotations/annotation.json"}, "semi-structured-job-metadata": {"type": "groundtruth/custom", "job-name": "semi-structured-job", "human-annotated": "yes", "creation-date": "2021-08-23T22:41:12.546000"}}
        ```

2. Includes a script to validate a Comprehend custom Entity Recognizer annotation for semi-structured data. It checks that the schema is valid and all entities can be referenced in the annotation file's data.

    All entities and their counts will be logged in a successful validation.

    ### Example script calls and outputs

    S3 annotation example call:
    ```
    python -m comprehend_customer_scripts.validation.semi_structured.entity_recognizer.validate_annotation --annotation-s3-ref s3://bucket/path/to/annotation.json
    ```

    Local annotation example call:
    ```
    python -m comprehend_customer_scripts.validation.semi_structured.entity_recognizer.validate_annotation --annotation-local-ref /Users/dnlen/Desktop/untitled_folder/blog/annotations/sreg-0e12539d-bd1a-4048-8055-d3f9e478d4a5-1-2e456931-ann.json
    ```

    Failure validation example output in the case of the `Version` attribute not existing within the annotation file:
    ```
    ERROR:root:Failed to validate annotation schema sreg-41d55a2f-cf4a-43d1-8905-4f441c9caccb-1-99b6261c-ann_issue.json due to {'Version': ['Missing data for required field.']}.
    ERROR:root:Validation failed.
    ```
