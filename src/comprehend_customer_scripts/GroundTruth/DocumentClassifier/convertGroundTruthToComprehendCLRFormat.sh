#!/bin/bash

if [[ "$#" -lt 3 ]]; then
    echo "USAGE: $0 <mode> <inputS3Uri> <outputDatasetS3Uri> <optional: label_delimiter>"
    echo " <mode>: Provide mode of DocumentClassifier, Valid values: MULTI_CLASS|MULTI_LABEL"
    echo " <inputS3Bucket>: Provide the S3Uri where the SageMaker GroundTruth output file is located"
    echo " <outputDatasetS3Uri>: Provide the complete S3Uri where the dataset file should be uploaded"
    echo " <label_delimiter>: Provide a delimiter for multilabel job. Default value='|' "
    echo " example: ./convertGroundtruthToCompCLRFormat.sh MULTI_CLASS s3://input-bucket/DocumentClassifier/manifests/output/output.manifest s3://output-bucket/CLR/dataset.csv"
    echo " example: ./convertGroundtruthToCompCLRFormat.sh MULTI_LABEL s3://input-bucket/DocumentClassifier/manifests/output/output.manifest s3://output-bucket/CLR/dataset.csv"
    echo " example: ./convertGroundtruthToCompCLRFormat.sh MULTI_LABEL s3://input-bucket/DocumentClassifier/manifests/output/output.manifest s3://output-bucket/CLR/dataset.csv $"
    exit 1
fi

echo "Provided mode=$1, inputS3Uri=$2, outputDatasetS3Uri=$3, label_delimiter=$4"

MODE=$1
INPUT_S3_URI=$2
DATASET_OUTPUT_S3_URI=$3
LABEL_DELIMITER=$4

if [[ -z ${LABEL_DELIMITER} ]]; then
    LABEL_DELIMITER="|"
fi

printf "\nDownloading the output.manifest file from the S3 location: [%s]\n" $2

aws s3 cp ${INPUT_S3_URI} "output.manifest" || exit 1

printf "\nTransforming the output.manifest file to csv format\n"

array=()
while read line ; do
  array+=($line)
done < <(python3 groundtruth_format_conversion_handler.py ${MODE} ${DATASET_OUTPUT_S3_URI} ${LABEL_DELIMITER})

printf "\nUploading the files to the destination S3 location: \n"
aws s3 cp ${array[0]} ${DATASET_OUTPUT_S3_URI} || exit 1
