# ComprehendCustomerScripts

## Introduction

This package contains scripts for our customers to experiment the features released by AWS Comprehend.

## Install dependencies:
1. Install AWS CLI
2. Install python3

## Documentation
To provide our customers a seamless integration between SageMaker GroundTruth and Comprehend's Custom API's, this package contains the following: 1) a shell script (convertGroundtruthToComprehendERFormat.sh) that converts the output of SageMaker GroundTruth NER labeling job to a format which is compatible with Comprehend's EntityRecognizer API. 2) a shell script (convertGroundtruthToComprehendCLRFormat.sh) that converts the output of SageMaker GroundTruth MultiClass and MultiLabel labeling job to a format which is compatible with Comprehend's DocumentClassifier API.

### EntityRecognizer
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

## Example:
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

### DocumentClassifier:
The convertGroundtruthToComprehendCLRFormat.sh script takes the following 3 inputs from the customer:
- Mode of the training job. Valid values are MULTI_CLASS and MULTI_LABEL
- S3Uri of the bucket where the output.manifest file (SageMaker Groundtruth labeling job output) is stored
- S3Uri of the bucket where the customer expects the dataset.csv (Comprehend's CreateDocumentClassifier API input) to be stored
- LabelDelimiter in case of MultiLabel job. This is an optional field, which is needed only for MULTI_LABEL mode jobs, default value = "|"

The script performs the following tasks:
1) Download the output.manifest file from the S3Uri provided by the customer
2) Parse the output.manifest file and create dataset.csv
3) Upload the dataset file to the S3 bucket provided by the customer

To run the script, execute the following command:
```
./convertGroundtruthToCompCLRFormat.sh <mode> <inputS3Uri> <outputDatasetS3Uri> <label_delimiter>
```

#### Multi_Class Example:

output.manifest

```
{"source":"Whatever you decide to do make sure it makes you #happy.","cutomDocClassification-multi-class":0,"cutomDocClassification-multi-class-metadata":{"confidence":0,"job-name":"labeling-job/cutomdocclassification-multi-class","class-name":"joy","human-annotated":"yes","creation-date":"2020-08-18T05:14:21.122782","type":"groundtruth/text-classification"}}
```
 
dataset.csv:

```
joy,Whatever you decide to do make sure it makes you #happy.
```

#### Multi_Label Example:

output.manifest
```
{"source":"Whatever you decide to do make sure it makes you #happy.","cutomDocClassification":[5,1],"cutomDocClassification-metadata":{"job-name":"labeling-job/cutomdocclassification","class-map":{"1":"optimism","5":"joy"},"human-annotated":"yes","creation-date":"2020-08-14T12:09:02.115245","confidence-map":{"1":0.49,"5":0.91},"type":"groundtruth/text-classification-multilabel"}}
```

dataset.csv
```
optimism|joy,Whatever you decide to do make sure it makes you #happy.
```

Each line in the output.manifest file is a JSON object.
The shell script takes the mode of the classifier job as the first argument. It also takes S3Uri of where this manifest file is stored as the second argument.

The script will executes the AWS CLI command to download the file to the local.

It will parse output.manifest file and generate dataset.csv file based on the file names obtained from parsing the outputS3Uri.

# Resources
Amazon Comprehend Document Search- Using Amazon Comprehend, Amazon Elasticsearch with Kibana, Amazon S3, Amazon Cognito to search over large number of documents such as pdf files.https://github.com/aws-samples/amazon-comprehend-doc-search

Amazon Textract Comprehend Image Search with Elasticsearch https://github.com/aws-samples/amazon-textract-comprehend-OCRimage-search-and-analyze

Easily setup human review of your NLP based Entity Recognition workflows with Amazon SageMaker Ground Truth, Amazon Comprehend AutoML and Amazon Augmented AI (A2I) - https://github.com/aws-samples/augmentedai-comprehendner-groundtruth

Deriving conversational insights from invoices with Amazon Textract, Amazon Comprehend, and Amazon Lex - https://github.com/aws-samples/aws-textract-comprehend-lex-chatbot

Active learning workflow for Amazon Comprehend Custom Classification models with Amazon Augmented AI https://github.com/aws-samples/amazon-comprehend-active-learning-framework

Easily setup built-in human review loops for NLP based entity recognition workflows using Amazon SageMaker Ground Truth, Amazon Comprehend and Amazon Augmented AI https://github.com/aws-samples/augmentedai-comprehendner-groundtruth

Amazon Transcribe Comprehend Podcast- A demo application that transcribes and indexes podcast episodes so the listeners can explore and discover episodes of interest and podcast owners can do analytics on the content over time. This solution leverages Amazon Transcribe, Amazon Comprehend, Amazon Elasticsearch, AWS Step Functions and AWS Lambda.https://github.com/aws-samples/amazon-transcribe-comprehend-podcast

Notebooks and recipes for creating custom entity recognizer for Amazon comprehend https://github.com/aws-samples/amazon-comprehend-custom-entity
Document Analysis Solution using Amazon Textract, Amazon Comprehend and Amazon A2I https://github.com/aws-samples/amazon-textract-comprehend-a2i
nlp-analysis-demo - The purpose of this demo is to build a stack that uses Amazon Comprehend and Amazon Textract to analyze unstructured data and generate insights and trends https://github.com/aws-samples/nlp-textract-comprehend-demo


# Workshops

workshop-textract-comprehend-es https://github.com/aws-samples/workshop-textract-comprehend-es



# LICENSE
This library is licensed under the MIT-0 License. See the LICENSE file. 


