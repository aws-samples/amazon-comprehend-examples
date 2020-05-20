from groundtruth_to_comprehend_format_converter import GroundTruthToComprehendFormatConverter
import csv
import argparse
from urllib.parse import urlparse


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

    def read_write_dataset(self):
        with open('output.manifest', 'r') as groundtruth_output_file, open(self.dataset_filename, 'a', encoding='utf8') as dataset:
            for index, jsonLine in enumerate(groundtruth_output_file):
                source = self.convert_object.convert_to_dataset(jsonLine)
                datawriter = csv.writer(dataset)
                datawriter.writerow([source])

    def read_write_annotations(self):
        # write header
        with open(self.annotation_filename, 'w') as annotation_file:
            datawriter = csv.writer(annotation_file)
            datawriter.writerow(['File', 'Line', 'Begin Offset', 'End Offset', 'Type'])

        # write annotations
        with open('output.manifest', 'r') as groundtruth_output_file, open(self.annotation_filename, 'a', encoding='utf8') as annotations:
            datawriter = csv.writer(annotations)
            for index, jsonLine in enumerate(groundtruth_output_file):
                annotations = self.convert_object.convert_to_annotations(index, jsonLine)
                for entry in annotations:
                    datawriter.writerow(entry)


def main():
    parser = argparse.ArgumentParser(description="Parsing the output S3Uri")
    parser.add_argument('dataset_output_S3Uri')
    parser.add_argument('annotations_output_S3Uri')
    args = parser.parse_args()
    handler = GroundTruthFormatConversionHandler()
    handler.validate_s3_input(args)
    handler.read_write_dataset()
    handler.read_write_annotations()


if __name__ == "__main__":
    main()
