from pathlib import Path
import pdfplumber
from typing import Dict, List, Tuple, Any

from text import TopDownSerializeStrategy
from utils import create_unique_directory
from extract import MdExtractionStrategy, NodesFromPageStrategy

    

# --- Update Pdf to use SerializationStrategy ---
class Pdf():

    # This class uses the strategy pattern to combine functionality into the Pdf abstraction.
    def __init__(self, path, chunking=None, serialization=None, extraction=None, uri=None):
        self.serialization = serialization or TopDownSerializeStrategy()
        self.chunking_strategy = NodesFromPageStrategy()
        self.path = Path(path)
        self._doc = pdfplumber.open(self.path)
        self.text = self.as_md()
        self.nodes = self.as_nodes()
    
    def as_nodes(self, pdfplumber_tbl_settings=None) -> List:
        out_buffer = []
        with pdfplumber.open(self.path) as pdf:
            [out_buffer.append(
                self.chunking_strategy(
                    self.serialization.serialize(p, pdfplumber_tbl_settings)) 
                for p in pdf.pages)]
            
        return out_buffer

    def as_md(self, save_directory='processed_sources', tbl_settings=None) -> Dict:
        
        # Todo: decouple saving from extraction
        self.md_directory = create_unique_directory(Path(save_directory, self.path.stem))
        doc = MdExtractionStrategy(save_directory = self.md_directory)  # Creates folder and saves images to {save_directory}/images/...
        text = '\n'.join(
            [doc.extract(self.serialization.serialize(p, tbl_settings)) 
             for p in self._doc.pages])

        
        with open(self.md_directory / Path(f'{self.path.stem}.md'), 'w') as file:
            return file.write(text)
    
        return text


# # Example usage
# project_folder = '/media/disk0/darren/testing/chatbot_api/experiment/darren/chunking_study'
# list_of_files = ['/primary_sources/0_新進同仁入職指南.pdf',
#                  '/processed_sources/1_關於神通資訊科技股份有限公司.pdf',
#                  '/primary_sources/精準定位 MTAN001-A.pdf']
# path = Path(f'{project_folder}{list_of_files[3]}')
# pdf = Pdf(path)
# nodes = pdf.as_nodes(extraction_config={"vertical":"lines_strict"})
# print('\n---\n'.join([n.text for n in nodes]))
# savdir= path.parents[1] / 'processed_sources' /  Path(path.stem)
# text = pdf.as_md(savdir)
