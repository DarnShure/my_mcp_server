import os 
from pathlib import Path
from typing import Dict, List, Tuple, Any
from pdfplumber.pdf import Page

from element import GithubTableFormattingStrategy, UriFormattingStrategy
from index.schema import TextNode, NodeRelationship, RelatedNodeInfo

class ExtractionStrategy:
    def extract(self, page:Page):
        raise NotImplementedError

class MdExtractionStrategy(ExtractionStrategy):
    def __init__(self, image_strategy = None, save_directory = None):
        self.savedir = save_directory
        self.image_strategy = image_strategy or ImageExtractionStrategy()

    def extract(self, page:Page) -> str:
        # Save image in given folder
        if self.savedir is not None: 
            #
            print(f'pdf: saving images to {self.savedir}')
            self.image_strategy.extract(page, self.savedir)
        text = page.extract_text()
        return text 
    # It would be great to use Pdf.extract(table_settings).save('/processes_sources')


class ImageExtractionStrategy(ExtractionStrategy):
    def __init__(self, formatting_strategy=None):
        self.formatting_strategy = formatting_strategy or UriFormattingStrategy()

    def extract(self, cur_page, md_document_directory, res=200) -> List:
        """Saves images to md_document_directory and returns a list of image paths"""
        images = cur_page.images
        buffer = []
        for image in images:
            image_element_text = self.formatting_strategy.format(image['name'])
            
            # Check for reducancy        
            for filename in os.listdir(md_document_directory):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    if filename.lower().split('.')[-1].endswith(image['name']):
                        continue
                
            bbox = [
                image['x0'], 
                cur_page.cropbox[3]-image['y1'], # top, where origin is top left
                image['x1'], 
                cur_page.cropbox[3]-image['y0']  # bot, " 
                ]
            
            # Ensure bbox is not larger than page.
            if bbox[2] > cur_page.cropbox[2]:
                bbox[2] = cur_page.cropbox[2]
            if bbox[3] > cur_page.cropbox[3]:
                bbox[3] = cur_page.cropbox[3]
            
            img_page = cur_page.crop(bbox=bbox)
            img_obj = img_page.to_image(resolution=res)
            
            # messy
            _ = image_element_text.split('(')[-1]
            image_path = _.split(')')[0]
            image_path = Path(md_document_directory, image_path)
            image_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

            img_obj.save(image_path)
            buffer.append(image_path)
        return buffer
             
class NodesFromPageStrategy(ExtractionStrategy):
    def extract(self, page: Page) -> List[Dict]:
        
        lines = page.get_textmap.to_string().split('\n')
        
        # Parameter
        text_node_line_size = 2

        nodes = [TextNode(text= '\n'.join(lines[i:i+text_node_line_size])) for i in range(0, len(lines), text_node_line_size)]
        

        out = []
        # Hooking up the nodes
        for i, n in enumerate(nodes):
            if i > 0:
                n.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(node_id=nodes[i-1].node_id)
            if i < len(nodes) - 1:
                n.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(node_id=nodes[i+1].node_id)            
            out.append(n)  
        return out


class Table():
    def __init__(self, raw_json : List[List[List]]):
        self.format_strategy = None
        self.rows = raw_json
        self.header = None
        self.text = self.get_text()
        self.nodes = self.as_nodes()

    def set_header(self, header):
        if len(header) != len(self.rows[1]):
            raise ValueError    
        else : self.header = header

    def get_text(self):
        return os.linesep.join(['<table_data>', self.format_strategy.format(self.rows), '</table_data>'])

    def as_nodes(self):
        if self.header == None:
            self.set_header(self.rows[0])
            raise Warning('Row 0 set as header')
        
        # Merge header and row
        nodes = [TextNode
                 (
            text=os.linesep.join(['<table_data>', self.header, self.format_strategy.format(row), '</table_data>'])
            ) for row in self.rows[1:]] 
        
        out = []
        # Hooking up the nodes
        for i, n in enumerate(nodes):
            if i > 0:
                n.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(node_id=nodes[i-1].node_id)
            if i < len(nodes) - 1:
                n.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(node_id=nodes[i+1].node_id)            
            out.append(n)  
        return out
            
        

class DerivedTable(Table):
    def __init__(self, prev_table : Table, raw_json : List[List[List]]):
        self.prev_table = prev_table
        self.set_header(prev_table.rows[0])
        super().__init__(raw_json)
        
    
