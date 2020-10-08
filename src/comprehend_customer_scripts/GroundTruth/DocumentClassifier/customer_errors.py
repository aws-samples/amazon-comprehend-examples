from string import Template

CANNOT_PARSE_AUGMENTED_MANIFEST = Template('An augmented manifest file in your request is an invalid JSON file. '
                                           'Amazon Comprehend is unable to parse line ${line} in the file ${file_name}. '
                                           'Correct the file and try again.')

DOCUMENT_TOO_BIG = Template(
    'The maximum size of an individual document is ${size}MB. The document '
    'on line: ${line} of file: ${file} was greater than the maximum size.')

EMPTY_LABEL_FOUND = Template(
    'Empty label found on line: ${line} of file: ${file}. This could be because '
    'of 1) a leading label delimiter 2) a trailing label delimiter 3) consecutive '
    'label delimiters in the labels list column or 4) an empty string.')

EMPTY_LABEL_UNSUPPORTED = \
    Template('Labels cannot be empty. The training file ${filename} contained '
             'at least one empty label.')

LABEL_TOO_BIG = Template(
    'The maximum size of an individual label is ${size} characters. The label '
    'on line: ${line} of file: ${file} was greater than the maximum size.')
