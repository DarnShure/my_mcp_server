import subprocess
from pathlib import Path
import shutil
import os

# This is a script written by Geminin advanced to change docx to pdf.

def run_pdf_conversion(f: str, output_directory: str) -> str:
    # Check if the assumed dummy file exists before trying conversion
    if Path(f).exists():
        try:
            print(f"\n--- Attempting conversion of {f} ---")
            pdf_file_path = convert_docx_to_pdf_libreoffice(f, output_directory)

            if pdf_file_path:
                print(f"\nConversion successful! PDF saved at: {pdf_file_path}")
                return pdf_file_path
            else:
                print("\nConversion process completed, but PDF file was not found.")

        except FileNotFoundError as e:
            print(f"\nConversion failed: {e}")
        except subprocess.CalledProcessError:
            print("\nConversion failed because the LibreOffice command returned an error.")
        except Exception as e:
                print(f"\nAn unexpected error occurred during conversion: {e}")
    else:
        print(f"\nCannot run example: Input file '{f}' not found.")

def find_libreoffice_path():
    """Tries to find the LibreOffice executable path."""
    
    # Common command names
    for command in ["soffice", "libreoffice"]:
        if shutil.which(command):
            return command
        
    # Common installation paths (add more for your OS if needed)
    paths_to_check = []
    if os.name == 'nt': # Windows
        paths_to_check.extend([
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ])
    elif os.name == 'posix': # Linux/macOS
        paths_to_check.extend([
            "/usr/bin/soffice",
            "/usr/bin/libreoffice",
            "/Applications/LibreOffice.app/Contents/MacOS/soffice" # macOS specific
        ])

    for path in paths_to_check:
        if Path(path).exists():
            return str(path) # Return as string

    return None # Indicate not found

# TODO: automate font install to make conversion more pretty.

def convert_docx_to_pdf_libreoffice(docx_path_str: str, output_dir_str: str) -> str | None:
    """
    Converts a DOCX file to PDF using LibreOffice command line.

    Args:
        docx_path_str: The full path to the input DOCX file.
        output_dir_str: The directory where the PDF should be saved.

    Returns:
        The full path to the generated PDF file if successful, otherwise None.

    Raises:
        FileNotFoundError: If the input docx_path_str does not exist or
                           if the LibreOffice executable cannot be found.
        subprocess.CalledProcessError: If LibreOffice fails during conversion.
    """
    docx_path = Path(docx_path_str)
    output_dir = Path(output_dir_str)

    # 1. Validate input DOCX file
    if not docx_path.is_file():
        raise FileNotFoundError(f"Input DOCX file not found: {docx_path}")

    # 2. Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # 3. Find LibreOffice executable
    soffice_command = find_libreoffice_path()
    if not soffice_command:
        # Consider raising a specific exception or printing a clearer error
        raise FileNotFoundError(
            "LibreOffice ('soffice' or 'libreoffice') command not found. "
            "Please ensure LibreOffice is installed and in your system's PATH "
            "or update the find_libreoffice_path function."
        )

    # 4. Construct the command
    # Note: We pass the DOCX path itself, not just the filename,
    # and tell LibreOffice where to output the PDF.
    command = [
        soffice_command,
        '--headless',         # Run without GUI
        '--convert-to', 'pdf', # Specify output format
        '--outdir', str(output_dir), # Specify output directory
        str(docx_path)        # Specify the input file
    ]

    print(f"Running command: {' '.join(command)}") # For debugging

    # 5. Execute the command
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE, # Capture standard output
            stderr=subprocess.PIPE, # Capture standard error
            check=True,             # Raise exception on non-zero exit code
            text=True,              # Decode stdout/stderr as text
            encoding='utf-8'        # Explicitly set encoding
        )
        print("LibreOffice stdout:\n", result.stdout) # Optional: log output

        # 6. Determine expected output path and check
        pdf_filename = docx_path.stem + ".pdf"
        expected_pdf_path = output_dir / pdf_filename

        if expected_pdf_path.is_file():
            print(f"Successfully converted '{docx_path.name}' to '{expected_pdf_path}'")
            return str(expected_pdf_path)
        else:
            # This might happen if LibreOffice succeeded (exit code 0)
            # but didn't produce the expected file for some reason.
            print(f"Error: LibreOffice command seemed successful but output PDF not found at {expected_pdf_path}")
            print("LibreOffice stderr:\n", result.stderr)
            return None

    except FileNotFoundError:
        # This specific block catches if soffice_command itself wasn't found by subprocess
        # although find_libreoffice_path should prevent this usually.
         raise FileNotFoundError(
             f"LibreOffice command '{soffice_command}' not found or executable. "
             "Ensure it's correctly installed and in PATH."
         )
    except subprocess.CalledProcessError as e:
        print(f"Error during LibreOffice conversion (Exit Code: {e.returncode}):")
        print("Command:", ' '.join(e.cmd))
        print("stdout:\n", e.stdout)
        print("stderr:\n", e.stderr)
        # Propagate the exception so the caller knows it failed
        raise e
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e # Re-raise unexpected errors

