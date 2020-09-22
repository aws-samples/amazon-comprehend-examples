from groundtruth_to_comprehend_format_converter import GroundTruthToComprehendFormatConverter
import csv
import json
import argparse
from urllib.parse import urlparse

ANNOTATION_CSV_HEADER = ['File', 'Line', 'Begin Offset', 'End Offset', 'Type']


class GroundTruthFormatConversionHandler:

    def __init__(self):
        self.convert_object = GroundTruthToComprehendFormatConverter()
        self.dataset_filename = ""
        self.annotation_filename = ""

    def validate_s3_input(self, args):
        dataset_output_S3Uri = args.dataset_output_S3Uri
        annotations_output_S3Uri = args.annotations_output_S3Uri

        dataset_url = urlparse(dataset_output_S3Uri)
        dataset_scheme = dataset_url.scheme
        self.dataset_filename = dataset_url.path.split("/")[-1]

        annotations_url = urlparse(annotations_output_S3Uri)
        annotation_scheme = annotations_url.scheme
        self.annotation_filename = annotations_url.path.split("/")[-1]

        print(self.dataset_filename)
        print(self.annotation_filename)

        if dataset_scheme != "s3" or annotation_scheme != "s3" or self.dataset_filename.split(".")[-1] != "csv" or self.annotation_filename.split(".")[-1] != "csv":
            raise Exception("Either of the output S3 location provided is incorrect!")
        
        # write header
        with open(self.annotation_filename, 'w', encoding='utf8') as annotation_file:
            datawriter = csv.writer(annotation_file, delimiter=',', lineterminator='\n')
            datawriter.writerow(ANNOTATION_CSV_HEADER)
    
    def read_augmented_manifest_file(self):
        with open('output.manifest', 'r', encoding='utf-8') as groundtruth_output_file:
            for index, jsonLine in enumerate(groundtruth_output_file):
                self.read_write_dataset_annotations(index, jsonLine)

    def read_write_dataset_annotations(self, index, jsonLine):
        with open(self.dataset_filename, 'a', encoding='utf8') as dataset, open(self.annotation_filename, 'a', encoding='utf8') as annotation_file:
            datawriter = csv.writer(annotation_file, delimiter=',', lineterminator='\n')
            source, annotations = self.convert_object.convert_to_dataset_annotations(index, jsonLine)
            # write the document in the dataset file
            source = json.dumps(source).strip('"')
            dataset.write('"' + source + '"')
            dataset.write("\n")
            
            # write the annotations of each document in the annotations file
            for entry in annotations:
                datawriter.writerow(entry)
                

def main():
    parser = argparse.ArgumentParser(description="Parsing the output S3Uri")
    parser.add_argument('dataset_output_S3Uri')
    parser.add_argument('annotations_output_S3Uri')
    args = parser.parse_args()
    handler = GroundTruthFormatConversionHandler()
    handler.validate_s3_input(args)
    handler.read_augmented_manifest_file()


if __name__ == "__main__":
    main()
