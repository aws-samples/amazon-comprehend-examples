import json


class GroundTruthToComprehendFormatConverter:

    def __init__(self):
        self.input_file_name = "dataset.csv"
        self.labeling_job_name = ""

    def convert_to_dataset(self, jsonLine):
        jsonObj = self.parse_manifest_input(jsonLine)
        return jsonObj['source']

    def convert_to_annotations(self, index, jsonLine):
        annotations = []
        jsonObj = self.parse_manifest_input(jsonLine)
        self.labeling_job_name = self.get_labeling_job_name(jsonObj)
        number_of_labels = len(jsonObj[self.labeling_job_name]['annotations']['entities'])
        labeling_job_info = jsonObj[self.labeling_job_name]['annotations']['entities']
        for ind in range(number_of_labels):
            annotations.append((self.input_file_name, index, labeling_job_info[ind]['startOffset'],
                                labeling_job_info[ind]['endOffset'],
                                labeling_job_info[ind]['label'].upper()))
            
        return annotations

    def parse_manifest_input(self, jsonLine):
        try:
            jsonObj = json.loads(jsonLine)
            return jsonObj
        except ValueError as e:
            print(f"Error decoding the string: {jsonLine}, {e}")
            raise

    def get_labeling_job_name(self, jsonObj):
        for key, value in jsonObj.items():
            if self.is_json_serializable(value):
                if "annotations" in value:
                    job_name = key
        return job_name

    def is_json_serializable(self, value):
        try:
            json.dumps(value)
            return True
        except ValueError as e:
            print(e)
            return False
