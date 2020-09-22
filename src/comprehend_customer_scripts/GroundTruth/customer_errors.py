from string import Template

CANNOT_PARSE_AUGMENTED_MANIFEST = Template('An augmented manifest file in your request is an invalid JSON lines file. '
                                           'Amazon Comprehend is unable to parse line ${line} in the file ${file_name}. '
                                           'Correct the file and try again.')

DOC_SIZE_EXCEEDED = Template('A document exceeds the maximum size in the file ${file} on line ${line}. '
                             'Each document can be up to ${size} bytes.')

WRONG_ANNOTATION = Template('An incorrect annotation is located in the file ${file_name} on line ${line}. The offset '
                            'begins at position ${begin_offset} and ends at position ${end_offset}. ${message}.')

INVALID_OFFSETS = Template('An offset exceeds the maximum length in the file ${doc} on line ${line_index}. The offset '
                           'begins at position ${begin_offset} and ends at position  ${end_offset}. An offset can be '
                           'up to ${line_size} in length.')

OVERLAPPING_ANNOTATIONS = Template('Overlapping annotations are located in the file ${doc} on line ${line}. '
                                   'Annotations must not overlap. The annotations are: ${annotations1} and ${annotations2}.')


INVALID_END_OFFSET = 'End Offset cannot be less than Begin Offset.'
