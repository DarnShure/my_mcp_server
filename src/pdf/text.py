from typing import Dict, List
from pathlib import Path
from pdfplumber.pdf import Page
from pdfplumber.page import FilteredPage

from element import GithubTableFormattingStrategy, UriFormattingStrategy


# --- Strategy Pattern for Serialization ---
class SerializationStrategy:
    def serialize(page:Page) -> Page :
        raise NotImplementedError

class TopDownSerializeStrategy(SerializationStrategy):
    """This class holds logic to linearize a Page object using pdfplumber and 
    pdfminer.
    
    It extends the functionality of pdf_plumber, making use of self.tuples 
    as a sorted list of all text elements from the top of the page to the bottom.
    """

    def __init__(self, table_formatter=None, uri_formatter=None):
        self.table_formatting_strategy = table_formatter or GithubTableFormattingStrategy()
        self.uri_formatting_strategy = uri_formatter or UriFormattingStrategy()

    def merge_elements_into_tuples(self, cd:str, ld:str, tuples:List[Dict],
                                    elements:List[Dict]) -> List[Dict]:
        
        """   
        Intro: This function reorders lists of tuples based on their verical positon on a page.
        It operates of the pdfminer level, using T_object abstraction to write bounding boxes.

        Args:
        cd : character direction: 'ltr' or 'rtl;
        ld : line direction : 'ttb' or 'btt';
        tuples : e.g. [('t' , {x0 : '600', ...}) , ...];
        elements : List : e.g. [{'content' : '', 'object' : Table}, ...]
            Notes : List order matters. elements[0] should be at highest on the page.
        
        
        - bottom = page_height - y0
        - top = page_height - y1 
        - (y0,x0) is at the bottom of the page
        """

        # Naive implementation: iterate through all object.
        element_pop_index_list = []
        try:
            tuples_size = len(tuples)
            if tuples_size == 0: return [(e['content'], e['object']) for e in elements]
        except:
            return [(e['content'], e['object']) for e in elements]
             
        if cd == 'ltr' and ld == 'ttb':

            # for all tables that occur before the first text
            for j, element in enumerate(elements): 

                # Lower-bound occurs before the top of the first word.
                _element_bot = element.get('object').get('bottom') or element.get('object').get('bot')
                if _element_bot <  tuples[0][1]['top']: 
                    tuples.insert(j, (element['content'], element['object']))
                    element_pop_index_list.append(j)

            # Clear all elements that have already been inserted in tuples.
            [elements.pop(x) for x in element_pop_index_list] 
            if len(elements) == 0: return tuples
        
            # Note: We use '\n' as the filter to indentify whitespace,
            # so we can insert all tables that occur between the given charcters,
            # so double-column text with not be serialized in the right order.
            def pass_whitespace(tuple_before, whitespace_tuple ,tuple_after, index):
                if (whitespace_tuple[0] == '\n' and whitespace_tuple[1] == None): 
                    
                    try:
                        # (0,0) is a bottom left of the page, but (bot, top) orients (0,0) to the top left of the page
                        top = 0 if index == 0 else self.page_height - tuple_before[1]['y0']  
                        bot = self.page_height if index-tuples_size-1 == 0 else self.page_height - tuple_after[1]['y1'] 
                        
                        x0 = None # TODO: Implement for double column
                        x1 = None
                        calculated_whitespace = {'index': index, 'top': top, 'bot': bot, 'x0': x0, 'x1': x1}

                    except Exception as e:
                        print(e) 
                    return calculated_whitespace
            
            # Fliter over a sliding window.
            whitespace = map(pass_whitespace, tuples[:-2], tuples[1:-1],
                             tuples[2:], range(1,len(tuples)-1))

            for w in [x for x in list(whitespace) if x]:
                    
                # Compare tuples
                e = elements[0]  # We only look at the first element because the list of elements is already sorted.
                e_bbox_top = e['object'].get('top')
                e_bbox_bot = e['object'].get('bot') or e['object'].get('bottom')
                if e_bbox_top == None or e_bbox_bot == None: raise AttributeError

                # insert custom tuple for element if the bbox of the 
                # element comes after the previous word, and before
                # the following word.
                if e_bbox_top > w['bot'] and e_bbox_bot < w['top']:  # Note this condition will make it so that this only works w
                    new_element_tuple = ('\n' + e['content'] + '\n', None)
                    tuples.insert(w['index'] , new_element_tuple)
                    elements.pop(0)

                # Add any remaining tables to the end.
                for element in elements:
                    tuples.append(('\n' + element['content'] + '\n', None))
                return tuples
    
    def serialize(self, page:Page, table_settings=None) -> FilteredPage:

        """
        Serialization Algorithm Overview:

        - filter the page to exclude any tuples from the detected tables.
        - add all elements that come before (i.e. located about) the first char
        - for each tuple in the filtered page:
            compare bounding boxes of adjacent tuples with the box first box of the element.
                if the element is the whitespace, insert it between the two tuples.
        - add all elements that come after the first char

        main abstraction: bbox (x0, top, x1, bot) 
            | where origin of top and bottom are top left of the page.
        """

        elements = {
            'tables' : [
                {
                'content' : self.table_formatting_strategy.format(y.extract()),
                'object' : {'x0': y.bbox[0], 'x1': y.bbox[2], 'top': y.bbox[1], 'bot': y.bbox[3]}  # bbox : (x0, top , x1, bottom)
                } for y in page.find_tables(table_settings=table_settings)],

            'images' : [
                {
                    'content' : self.uri_formatting_strategy.format(x['name']), # URI
                    'object' : x
                } for x in page.images] # for propeties, see pdfplumber docs
                 # https://github.com/jsvine/pdfplumber?tab=readme-ov-file#objects     
                                    
                    }
        self.page_height = page.height
        
        # Filter page from of tables; 
        # see page.outside_bbox(bounding_box, relative=False, strict=True)
        bboxes = [element['object'] for element in elements['tables'] if element!=None]
        def not_within_bboxes(obj):
            def obj_in_bbox(_bbox):
                v_mid = (obj["top"] + obj["bottom"]) / 2
                h_mid = (obj["x0"] + obj["x1"]) / 2
                x0, x1, top, bottom = _bbox.get('x0'), _bbox.get('x1'), _bbox.get('top'), (_bbox.get('bottom') or _bbox.get('bot') )
                return (h_mid) >= x0 and (h_mid) < x1 and (v_mid >= top) and (v_mid < bottom)
            return not any(obj_in_bbox(__bbox) for __bbox in bboxes)
        filtered_page = page.filter(not_within_bboxes)

        # Note: result is written implictly; pass-by-reference
        tm = filtered_page.get_textmap() 
        for k in elements.keys():

            # modify existing textmap
            tm.tuples = self.merge_elements_into_tuples(
                tm.char_dir_render,
                tm.line_dir_render,
                tm.tuples,
                elements[k])

        # refresh string representation
        tm.as_string = tm.to_string()
        return filtered_page
    
    
# Assume page.objects is sorted

# Naive: go through all bounding boxes and compare them with others in the list

    def filter_rects(self, _objects):
        for i, rect in enumerate(_objects): 
            print(rect[i].__dict__.get('bbox')[1] == rect[i].__dict__.get('bbox')[1] and rect[i].__dict__.get('bbox')[3] == rect[i].__dict__.get('bbox')[3])

    