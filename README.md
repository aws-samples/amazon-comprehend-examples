## ComprehendCustomerScripts

##Introduction

This package contains scripts for our customers to experiment the features released by AWS Comprehend.

##Install dependencies:
1. Install AWS CLI
2. Install python3

##Documentation
To provide our customers a seamless integration between SageMaker GroundTruth and Comprehend's CreateEntityRecognizer API, this package contains a shell script (convertGroundtruthToComprehendERFormat.sh) that converts the output of SageMaker GroundTruth NER labeling job to a format which is compatible with Comprehend's EntityRecognizer API.

The script takes the following 3 inputs from the customer:
- S3Uri of the bucket where the output.manifest file (SageMaker Groundtruth labeling job output) is stored
- S3Uri of the bucket where the customer expects the dataset.csv (Comprehend's CreateEntityRecognizer API input) to be stored
- S3Uri of the bucket where the customer expects the annotations.csv (Comprehend's CreateEntityRecognizer API input) to be stored

The script performs the following tasks:
1) Download the output.manifest file from the S3Uri provided by the customer
2) Parse the output.manifest file and create dataset.csv and annotations.csv
3) Upload the dataset and annotations file in the S3 bucket provided by the customer

To run the script, execute the following command:
```
./convertGroundtruthToCompERFormat.sh <inputS3Uri> <outputDatasetS3Uri> <outputAnnotationsS3Uri>
```

##Example:
output.manifest.json:
```
{"source":"Bob was born on Jan 1 1990 and lived his whole life in Minneapolis.","EntityRecognizerPOC-1":{"annotations":{"entities":[{"endOffset":22,"startOffset":16,"label":"Date"},{"endOffset":3,"startOffset":0,"label":"Person"},{"endOffset":67,"startOffset":56,"label":"Location"}],"labels":[{"label":"Date"},{"label":"Location"},{"label":"Person"}]}},"EntityRecognizerPOC-1-metadata":{"entities":[{"confidence":0.08},{"confidence":0.08},{"confidence":0.09}],"job-name":"labeling-job/entityrecognizerpoc-1","type":"groundtruth/text-span","creation-date":"2020-04-17T23:27:41.344393","human-annotated":"yes"}}
{"source":"Bob was born on Jan 1 1990 and lived his whole life in Minneapolis.","EntityRecognizerPOC-1":{"annotations":{"entities":[{"endOffset":26,"startOffset":16,"label":"Date"},{"endOffset":67,"startOffset":56,"label":"Location"}],"labels":[{"label":"Date"},{"label":"Location"},{"label":"Person"}]}},"EntityRecognizerPOC-1-metadata":{"entities":[{"confidence":0.09},{"confidence":0.09}],"job-name":"labeling-job/entityrecognizerpoc-1","type":"groundtruth/text-span","creation-date":"2020-04-17T23:26:35.975508","human-annotated":"yes"}}
```
where each line is a JSON object.
The shell script takes the S3Uri of where this file is stored as the first argument.

The script will executes the AWS CLI command to download the file to the local.

The script will parse the outputS3Uri's provided, to fetch the expected dataset and annotation file name.
It will parse output.manifest file and generate dataset.csv and annotations.csv file based on the file names obtained from parsing the outputS3Uri.

dataset.csv:
```
Bob was born on Jan 1 1990 and lived his whole life in Minneapolis
Bob was born on Jan 1 1990 and lived his whole life in Minneapolis
```

annotations.csv
```
File,Line,Begin Offset,End Offset,Type
dataset.csv,0,0,3,Person
dataset.csv,0,16,22,Date
dataset.csv,0,56,67,Location
```

Eventually, the shell script will execute the AWS CLI command to upload dataset and annotations file to the S3Uri provided as the input.

##LICENSE
This library is licensed under the MIT-0 License. See the LICENSE file. 


