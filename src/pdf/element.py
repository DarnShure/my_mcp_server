from typing import Dict, Any, List
from pathlib import Path
import os

# This module is responsible for postprocessing json tables [List[List]] into a string.

# --- Formatting Strategy Pattern ---
class ElementFormattingStrategy:
    def format(self, table: List[List]) -> str:
        raise NotImplementedError

class GithubTableFormattingStrategy(ElementFormattingStrategy):
    def flatten_cells(self, row: List[str]) -> List[str]:
        return [string_cell.replace('\n', '\\n') if string_cell is not None else ' ' for string_cell in row]

    def process_row(self, row: List[str]) -> str:
        return '\n|' + ' | '.join(row) + '|'

    def format(self, table: List[List]) -> str:
        text = ""
        for index, row in enumerate(table):
            row = self.flatten_cells(row)
            if index < 1:
                text = self.process_row(row)
                text += self.process_row(['--'] * len(row))
            else:
                if index > len(table) - 1: 
                    
                    # add extra white after the last row of the table
                    text += self.process_row(row) + '/n'
                text += self.process_row(row)
        return text

class UriFormattingStrategy(ElementFormattingStrategy):
    def format(self, image_name : Path) -> str:   

        # add images folder to name
        return f"![{image_name}]({Path('images', image_name).with_suffix('.png')})"
        
# For organizing cells with many rect objects within them.        
class TableCell():
    def __init__(self, t_objects: List[Any]):
        self.table_objects = t_objects

    def format(self):
        return self.table_objects[0]

class MyPage():
    def __init__(self, objects: List[Any]):
        self.object = objects
    
    

if __name__ == '__main__':
    pass