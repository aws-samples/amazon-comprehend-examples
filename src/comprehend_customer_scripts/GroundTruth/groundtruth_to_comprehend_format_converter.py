import json
from operator import itemgetter
from customer_errors import CANNOT_PARSE_AUGMENTED_MANIFEST, DOC_SIZE_EXCEEDED, WRONG_ANNOTATION, INVALID_END_OFFSET, \
    INVALID_OFFSETS, OVERLAPPING_ANNOTATIONS

SOURCE = 'source'
ANNOTATIONS = 'annotations'
ENTITIES = 'entities'
START_OFFSET = 'startOffset'
END_OFFSET = 'endOffset'
LABEL = 'label'
MAX_TRAIN_DOC_SIZE = 5000


class GroundTruthToComprehendFormatConverter:

    def __init__(self):
        self.input_file_name = "dataset.csv"
        self.groundtruth_manifest_file_name = "output.manifest"
        self.labeling_job_name = ""
        self.maximum_offset = 0

    def convert_to_dataset_annotations(self, index, jsonLine):
        # parse the jsonLine to generate the dataset entry
        jsonObj = self.parse_manifest_input(jsonLine)
        if SOURCE not in jsonObj:
            raise Exception(CANNOT_PARSE_AUGMENTED_MANIFEST.substitute(line=index,
                                                                       file_name=self.groundtruth_manifest_file_name))
        source = jsonObj[SOURCE]
        if len(source.encode('utf-8')) > MAX_TRAIN_DOC_SIZE:
            raise Exception(DOC_SIZE_EXCEEDED.substitute(file=self.groundtruth_manifest_file_name,
                                                         line=index,
                                                         size=MAX_TRAIN_DOC_SIZE))
        self.maximum_offset = len(source.encode('utf-8'))

        # parse the jsonLine to generate the annotations entry
        annotations = []
        
        self.labeling_job_name = self.get_labeling_job_name(index, jsonObj)
        number_of_labels = len(jsonObj[self.labeling_job_name][ANNOTATIONS][ENTITIES])
        labeling_job_info = jsonObj[self.labeling_job_name][ANNOTATIONS][ENTITIES]
        for ind in range(number_of_labels):
            begin_offset = int(labeling_job_info[ind][START_OFFSET])
            end_offset = int(labeling_job_info[ind][END_OFFSET])
            label = labeling_job_info[ind][LABEL]
            if end_offset < begin_offset:
                raise Exception(WRONG_ANNOTATION.substitute(file_name=self.groundtruth_manifest_file_name,
                                                            line=int(index),
                                                            begin_offset=begin_offset,
                                                            end_offset=end_offset,
                                                            message=INVALID_END_OFFSET))
            if (begin_offset >= self.maximum_offset) or (end_offset > self.maximum_offset):
                raise Exception(INVALID_OFFSETS.substitute(doc=self.groundtruth_manifest_file_name,
                                                           line_index=index,
                                                           begin_offset=begin_offset,
                                                           end_offset=end_offset,
                                                           line_size=self.maximum_offset))
            annotations.append((self.input_file_name, index, begin_offset, end_offset, label))
        
        self._check_for_overlapping_annotations(annotations)
           
        return source, annotations

    def parse_manifest_input(self, jsonLine):
        try:
            jsonObj = json.loads(jsonLine)
            return jsonObj
        except ValueError as e:
            print(f"Error decoding the string: {jsonLine}, {e}")
            raise

    def get_labeling_job_name(self, index, jsonObj):
        job_name = None
        for key, value in jsonObj.items():
            if self.is_json_serializable(value):
                if ANNOTATIONS in value:
                    job_name = key
        if job_name is None or ANNOTATIONS not in jsonObj[job_name].keys() or ENTITIES not in jsonObj[job_name][ANNOTATIONS].keys():
            raise Exception(CANNOT_PARSE_AUGMENTED_MANIFEST.substitute(line=index,
                                                                       file_name=self.groundtruth_manifest_file_name))
        return job_name

    def is_json_serializable(self, value):
        try:
            json.dumps(value)
            return True
        except ValueError as e:
            print(e)
            return False
    
    """
        Example: annotations = [(doc.txt,0,25,16,DATE), (doc.txt,0,0,3,PROGRAMMER), (doc.txt,0,55,66,LOCATION)]
        Sort the annotations based on the begin offset,
        annotations = [(doc.txt,0,0,3,PROGRAMMER), (doc.txt,0,25,16,DATE), (doc.txt,0,55,66,LOCATION)]
        Considering 2 annotations at a time, Compare the end offset of 1st annotation with begin offset of 2nd annotation and 
        raise an exception if they overlap
    """

    def _check_for_overlapping_annotations(self, annotations):
        annotations.sort(key=itemgetter(2))  # 2 represents the index of beginOffset in the tuple
        for i in range(1, len(annotations)):
            previous_end_offset = annotations[i - 1][3]  # 3 represents the index of the endOffset in the previous tuple
            current_begin_offset = annotations[i][2]  # 2 represents the index of the beginOffset in the current tuple
            if previous_end_offset > current_begin_offset:
                raise Exception(OVERLAPPING_ANNOTATIONS.substitute(doc=self.groundtruth_manifest_file_name,
                                                                   line=annotations[i][1],
                                                                   annotations1=annotations[i - 1][4], # represents entity types in the previous tuple that is overlapping
                                                                   annotations2=annotations[i][4]))  # represents other entity type in the current tuple that is overlapping
