"""
Helper utility for visualizing custom annotations on PDF files
"""

import os
import csv

class PDFHelper:
    @staticmethod
    def add_annotations_to_file(annotations, input_filepath, output_filepath):
        """
        annotations: json annotations
        input_filepath: location of original pdf file to annotate
        output_filepath: location to write new pdf file with annotations
        """
        # First, add bounding box coordinates to the entities (groups word-level bounding boxes)
        page_entities_map = PDFHelper.enhanceEntitiesWithBoundingBoxInfo(annotations)

        # Second, add the annotation information to the document
        doc = PDFHelper.addLabelsToDoc(input_filepath, page_entities_map)
        doc.save(output_filepath, deflate=True)
        return output_filepath
        
    @staticmethod
    def enhanceEntitiesWithBoundingBoxInfo(PDF_ANNOTATIONS):
        
        
        def generateBoundingBoxCoordinates(block_ref):
            '''Function to get bounding box coordinates of an entity. If entity has more than one child blocks, it combines them together.'''
            if "ChildBlocks" in block_ref:
                for index, child_block_ref in enumerate(block_ref["ChildBlocks"]):
                    block = blocks[block_ref["ChildBlocks"][index]["ChildBlockId"]]
                    if index==0:
                        top = block["Geometry"]["BoundingBox"]["Top"]
                        left = block["Geometry"]["BoundingBox"]["Left"]
                        right = block["Geometry"]["BoundingBox"]["Left"] + block["Geometry"]["BoundingBox"]["Width"]
                        bottom = block["Geometry"]["BoundingBox"]["Top"] + block["Geometry"]["BoundingBox"]["Height"]
                    else:
                        if block["Geometry"]["BoundingBox"]["Top"]<top:
                            top = block["Geometry"]["BoundingBox"]["Top"]
                        if block["Geometry"]["BoundingBox"]["Left"]<left:
                            left = block["Geometry"]["BoundingBox"]["Left"]
                        if block["Geometry"]["BoundingBox"]["Left"] + block["Geometry"]["BoundingBox"]["Width"]>right:
                            right = block["Geometry"]["BoundingBox"]["Left"] + block["Geometry"]["BoundingBox"]["Width"]
                        if block["Geometry"]["BoundingBox"]["Top"] + block["Geometry"]["BoundingBox"]["Height"]>bottom:
                            bottom = block["Geometry"]["BoundingBox"]["Top"] + block["Geometry"]["BoundingBox"]["Height"]
                return {
                    "Top": top,
                    "Left": left,
                    "Width": right - left,
                    "Height": bottom - top
                }
            else:
                block = blocks[block_ref["BlockId"]]
                return block["Geometry"]["BoundingBox"]
        
        blocks = {block["Id"]: block for block in PDF_ANNOTATIONS["Blocks"]}
        entities = PDF_ANNOTATIONS["Entities"]

        for entity in entities:
            entity["BoundingBox"] = generateBoundingBoxCoordinates(entity["BlockReferences"][0])
            entity["Page"] = blocks[entity["BlockReferences"][0]["BlockId"]]["Page"]

        #Create map of entities in each page
        page_entities_map = {}
        for entity in entities:
            page_entities_map.setdefault(entity["Page"], []).append(entity)

        return page_entities_map

    
    @staticmethod
    def addLabelsToDoc(PDF_FILE_LOCAL_URL, page_entities_map):

        RGB_COLORS = [[1, 112.0/255, 166.0/255], [252.0/255, 122.0/255, 87.0/255], [0, 139.0/255, 248.0/255], 
                      [199.0/255, 62.0/255, 29.0/255], [102.0/255, 16.0/255, 242.0/255]]

        import fitz
        print(fitz.__doc__)
        if fitz.VersionBind.split(".") < ["1", "17", "0"]:
            print("PyMuPDF v1.17.0+ is needed.")

        doc = fitz.open(PDF_FILE_LOCAL_URL)
        num_pages = doc.page_count

        entity_type_color_map = {}
        for i in range(num_pages):
            page = doc.load_page(i)
            page.set_rotation(0)
            page_width = page.bound().width
            page_height = page.bound().height
            for entity in page_entities_map[i+1]:
                # Assign color to entity type
                if entity["Type"] not in entity_type_color_map:
                    entity_type_color_map[entity["Type"]] = RGB_COLORS[0]
                    del RGB_COLORS[0]
                entity_type_color = entity_type_color_map[entity["Type"]]

                # Box annotation over entity text
                box_rect = fitz.Rect(page_width * entity["BoundingBox"]["Left"], page_height * entity["BoundingBox"]["Top"], 
                                     page_width * (entity["BoundingBox"]["Left"] + entity["BoundingBox"]["Width"]), 
                                     page_height * (entity["BoundingBox"]["Top"] + entity["BoundingBox"]["Height"]))
                rect_annot = page.add_rect_annot(box_rect)
                rect_annot.set_border(width=0.5)
                rect_annot.set_colors(stroke=entity_type_color)
                rect_annot.update()

                text_rect = fitz.Rect(page_width * entity["BoundingBox"]["Left"] - 15, 
                page_height * entity["BoundingBox"]["Top"] - 20, 
                page_width * (entity["BoundingBox"]["Left"] + entity["BoundingBox"]["Width"] + 20), 
                page_height * (entity["BoundingBox"]["Top"] + entity["BoundingBox"]["Height"]))
                text_annot = page.add_freetext_annot(text_rect, text=entity["Type"], text_color=entity_type_color, fontsize=20)
                
                text_annot.update(border_color=[])

        return doc
