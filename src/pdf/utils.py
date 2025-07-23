from pdfplumber.pdf import Page
import os

def create_unique_directory(dir_path):
    """
    Creates a directory. If it already exists, appends '-1' to the name until a unique name is found.

    Args:
        dir_path: The desired directory path.
    
# Example usage:
directory_name = "my_directory"
create_unique_directory(directory_name)
    """
    original_dir_path = dir_path
    counter = 1
    while os.path.exists(dir_path):
       dir_path = f"{original_dir_path}-{counter}"
       counter += 1
    os.makedirs(dir_path)

    # Optional
    print(f"Directory created: {dir_path}")
    return dir_path

# Geometry
def calculate_rect_areas(x):
    x['area'] = (x['x1']-x['x0']) * (x['y1']-x['y0']) 
    return x['area']

def is_b_inside_a(a, b)-> bool:

    if a['y1'] < b['y1']:
        return False
    if a['y0'] > b['y0']:
        return False
    if a['x0'] > b['x0']:
        return False
    if a['x1'] < b['x1']:
        return False
    return True
