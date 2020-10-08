import json
import argparse
from urllib.parse import urlparse

from groundtruth_to_comprehend_clr_format_converter import GroundTruthToComprehendCLRFormatConverter


class GroundTruthToCLRFormatConversionHandler:

    def __init__(self):
        self.convert_object = GroundTruthToComprehendCLRFormatConverter()
        self.dataset_filename = ""

    def validate_s3_input(self, args):
        dataset_output_S3Uri = args.dataset_output_S3Uri

        dataset_url = urlparse(dataset_output_S3Uri)
        dataset_scheme = dataset_url.scheme
        self.dataset_filename = dataset_url.path.split("/")[-1]

        print(self.dataset_filename)

        if dataset_scheme != "s3" or self.dataset_filename.split(".")[-1] != "csv":
            raise Exception("Either of the output S3 lo cation provided is incorrect!")

    def read_write_multiclass_dataset(self):
        with open('output.manifest', 'r', encoding='utf-8') as groundtruth_output_file, \
                open(self.dataset_filename, 'a', encoding='utf8') as multiclass_dataset:
            for index, jsonLine in enumerate(groundtruth_output_file):
                class_name, source = self.convert_object.convert_to_multiclass_dataset(index, jsonLine)
                source = json.dumps(source).strip('"')
                multiclass_dataset.write(class_name + ',"' + source + '"')
                multiclass_dataset.write("\n")

    def read_write_multilabel_dataset(self, label_delimiter):
        with open('output.manifest', 'r', encoding='utf-8') as groundtruth_output_file, \
                open(self.dataset_filename, 'a', encoding='utf8') as multilabel_dataset:
            for index, jsonLine in enumerate(groundtruth_output_file):
                labels, source = self.convert_object.convert_to_multilabel_dataset(index, jsonLine, label_delimiter)
                source = json.dumps(source).strip('"')
                multilabel_dataset.write(labels + ',"' + source + '"')
                multilabel_dataset.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Parsing the output S3Uri")
    parser.add_argument('mode')
    parser.add_argument('dataset_output_S3Uri')
    parser.add_argument('label_delimiter')
    args = parser.parse_args()
    handler = GroundTruthToCLRFormatConversionHandler()
    handler.validate_s3_input(args)
    if args.mode == "MULTI_CLASS":
        handler.read_write_multiclass_dataset()
    elif args.mode == "MULTI_LABEL":
        handler.read_write_multilabel_dataset(args.label_delimiter)
    else:
        raise Exception("The value provided for mode is invalid. Valid values are MUTLI_CLASS|MULTI_LABEL")


if __name__ == "__main__":
    main()
