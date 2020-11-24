import json

from customer_errors import CANNOT_PARSE_AUGMENTED_MANIFEST, DOCUMENT_TOO_BIG, LABEL_TOO_BIG, EMPTY_LABEL_UNSUPPORTED, \
    EMPTY_LABEL_FOUND


SOURCE = 'source'
CLASS_NAME = 'class-name'
CLASS_MAP = 'class-map'
ATTRIBUTE_NAME_PARAMETER = 'attributeNames'
FAILURE_REASON = 'failure-reason'
BYTES_TO_MIB = 1024 * 1024

default_limits = {
    'MAX_LABEL_SIZE_IN_CHARS': 5000,
    'MAX_DOCUMENT_SIZE_MB': 10
}


class GroundTruthToComprehendCLRFormatConverter:

    def __init__(self):
        self.groundtruth_manifest_file_name = "output.manifest"
        self.labeling_job_name = ""
        self.label_delimiter = ""

    def _parse_manifest_input(self, index, input):
        try:
            if input is not None:
                return json.loads(input)
        except ValueError:
            raise Exception(CANNOT_PARSE_AUGMENTED_MANIFEST.substitute(line=index,
                                                                       file_name=self.groundtruth_manifest_file_name))

    # Raise CustomerError if the document size > 10MB
    def _check_document_size(self, source, index, limits):
        document_size_mb = len(source.encode('utf-8')) / BYTES_TO_MIB
        if document_size_mb > limits['MAX_DOCUMENT_SIZE_MB']:
            raise Exception(DOCUMENT_TOO_BIG.substitute(
                size=limits['MAX_DOCUMENT_SIZE_MB'],
                line=index,
                file=self.groundtruth_manifest_file_name,
            ))

    def get_labeling_job_name(self, index, jsonLine_input):
        job_name = None
        for key, value in jsonLine_input.items():
            if "-metadata" in key:
                job_name = key

        if job_name is None:
            raise Exception(CANNOT_PARSE_AUGMENTED_MANIFEST.substitute(line=index,
                                                                       file_name=self.groundtruth_manifest_file_name))
        return job_name

    # Raise CustomerError if the class/label size is >5000 characters
    def _check_label_size(self, label, index, limits):
        if len(label) > limits['MAX_LABEL_SIZE_IN_CHARS']:
            raise Exception(LABEL_TOO_BIG.substitute(size=limits['MAX_LABEL_SIZE_IN_CHARS'],
                                                     line=index,
                                                     file=self.groundtruth_manifest_file_name))

    """
    Convert dict of labels into a string where each label is joined using the label_delimiter
    Example: "label1|label2|label3"
    """

    def _get_labels(self, class_map):
        return ''.join([value + self.label_delimiter for value in class_map.values()])[:-1]

    def convert_to_multiclass_dataset(self, index, jsonLine):

        jsonLine_object = self._parse_manifest_input(index, jsonLine)
        if jsonLine_object is not None:
            if SOURCE not in jsonLine_object.keys():
                raise Exception(CANNOT_PARSE_AUGMENTED_MANIFEST.substitute(line=index,
                                                                           file_name=self.groundtruth_manifest_file_name))
            source = jsonLine_object[SOURCE]
            self._check_document_size(source, index, limits=default_limits)

            self.labeling_job_name = self.get_labeling_job_name(index, jsonLine_object)
            if CLASS_NAME not in jsonLine_object[self.labeling_job_name].keys():
                raise Exception(CANNOT_PARSE_AUGMENTED_MANIFEST.substitute(line=index,
                                                                           file_name=self.groundtruth_manifest_file_name))

            class_name = jsonLine_object[self.labeling_job_name][CLASS_NAME]
            if not class_name:
                raise Exception(EMPTY_LABEL_UNSUPPORTED.substitute(filename=self.groundtruth_manifest_file_name))
            self._check_label_size(class_name, index, limits=default_limits)

        return class_name, source

    def convert_to_multilabel_dataset(self, index, jsonLine, label_delimiter):
        self.label_delimiter = label_delimiter

        jsonLine_object = self._parse_manifest_input(index, jsonLine)
        if jsonLine_object is not None:
            if SOURCE not in jsonLine_object.keys():
                raise Exception(CANNOT_PARSE_AUGMENTED_MANIFEST.substitute(line=index,
                                                                           file_name=self.groundtruth_manifest_file_name))
            source = jsonLine_object[SOURCE]
            self._check_document_size(source, index, limits=default_limits)

            self.labeling_job_name = self.get_labeling_job_name(index, jsonLine_object)

            if CLASS_MAP not in jsonLine_object[self.labeling_job_name].keys():
                raise Exception(CANNOT_PARSE_AUGMENTED_MANIFEST.substitute(line=index,
                                                                           file_name=self.groundtruth_manifest_file_name))
            class_map = jsonLine_object[self.labeling_job_name][CLASS_MAP]

            # Raise CustomerError when no label found for the document
            if len(class_map) == 0:
                raise Exception(EMPTY_LABEL_UNSUPPORTED.substitute(filename=self.groundtruth_manifest_file_name))

            # Raise CustomerError if label size is more than 5000 characters
            for label in class_map.values():
                self._check_label_size(label, index, limits=default_limits)

            labels = self._get_labels(class_map)

            # Raise Customer error when empty label found in the list of labels
            label_list = labels.split(self.label_delimiter)
            for label in label_list:
                if len(label) == 0:
                    raise Exception(EMPTY_LABEL_FOUND.substitute(line=index,
                                                                 file=self.groundtruth_manifest_file_name))

        return labels, source
