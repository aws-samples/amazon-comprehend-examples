#!/bin/bash

if [[ "$#" -lt 3 ]]; then
    echo "USAGE: $0 <inputS3Uri> <outputDatasetS3Uri> <outputAnnotationsS3Uri>"
    echo " <inputS3Bucket>: Provide the S3Uri where the SageMaker GroundTruth output file is located"
    echo " <outputDatasetS3Uri>: Provide the complete S3Uri where the dataset file should be uploaded"
    echo " <outputAnnotationsS3Uri>: Provide the complete S3Uri, where the annotation file should be upload"
    echo " example: ./convertGroundtruthToCompERFormat.sh s3://input-bucket/EntityRecognizer/manifests/output/output.manifest s3://output-bucket/ER/dataset.csv s3://output-bucket/ER/annotations.csv"
    exit 1
fi

echo "Provided inputS3Uri=$1, outputDatasetS3Uri=$2, outputAnnotationsS3Uri=$3"

INPUT_S3_URI=$1
DATASET_OUTPUT_S3_URI=$2
ANNOTATIONS_OUTPUT_S3_URI=$3

printf "\nDownloading the output.manifest file from the S3 location: [%s]\n" $1

aws s3 cp ${INPUT_S3_URI} "output.manifest" || exit 1

printf "\nTransforming the output.manifest file to csv format\n"

array=()
while read line ; do
  array+=($line)
done < <(python3 groundtruth_format_conversion_handler.py ${DATASET_OUTPUT_S3_URI} ${ANNOTATIONS_OUTPUT_S3_URI})

printf "\nUploading the files to the destination S3 location: \n"
aws s3 cp ${array[0]} ${DATASET_OUTPUT_S3_URI} || exit 1
aws s3 cp ${array[1]} ${ANNOTATIONS_OUTPUT_S3_URI} || exit 1