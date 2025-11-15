import os
import pdfplumber
from pathlib import Path


def convert_pdf_to_markdown(pdf_path, output_dir="data/MD"):
    """
    Convert a PDF to Markdown format, preserving tables.
    
    Args:
        pdf_path (str or Path): Path to the PDF file
        output_dir (str): Directory to save the markdown file
    
    Returns:
        str: Path to the generated markdown file, or None if conversion failed
    """
    pdf_path = Path(pdf_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output filename
    md_filename = pdf_path.stem + ".md"
    md_path = Path(output_dir) / md_filename
    
    # Skip if already converted
    if md_path.exists():
        return str(md_path)
    
    try:
        markdown_content = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Add page header
                markdown_content.append(f"\n---\n## Page {page_num}\n")
                
                # Extract text
                text = page.extract_text()
                if text:
                    markdown_content.append(text)
                
                # Extract tables
                tables = page.extract_tables()
                if tables:
                    for table_num, table in enumerate(tables, 1):
                        markdown_content.append(f"\n### Table {table_num}\n")
                        # Convert table to markdown format
                        md_table = table_to_markdown(table)
                        markdown_content.append(md_table)
        
        # Write to file
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_content))
        
        return str(md_path)
    
    except Exception as e:
        print(f"Error converting {pdf_path}: {e}")
        return None


def table_to_markdown(table):
    """
    Convert a table (list of lists) to markdown format.
    
    Args:
        table (list): List of rows, where each row is a list of cells
    
    Returns:
        str: Markdown formatted table
    """
    if not table or len(table) == 0:
        return ""
    
    # Clean cells (replace None with empty string)
    cleaned_table = [[str(cell) if cell is not None else "" for cell in row] for row in table]
    
    # Ensure all rows have the same number of columns
    max_cols = max(len(row) for row in cleaned_table)
    cleaned_table = [row + [""] * (max_cols - len(row)) for row in cleaned_table]
    
    if len(cleaned_table) < 1:
        return ""
    
    # Build markdown table
    md_lines = []
    
    # Header row
    header = "| " + " | ".join(cleaned_table[0]) + " |"
    md_lines.append(header)
    
    # Separator
    separator = "| " + " | ".join(["---"] * max_cols) + " |"
    md_lines.append(separator)
    
    # Data rows
    for row in cleaned_table[1:]:
        row_md = "| " + " | ".join(row) + " |"
        md_lines.append(row_md)
    
    return "\n".join(md_lines)


def convert_pdf_folder(pdf_folder, output_dir="data/MD"):
    """
    Convert all PDFs in a folder to markdown, skipping already converted files.
    
    Args:
        pdf_folder (str): Path to folder containing PDFs
        output_dir (str): Directory to save markdown files
    
    Returns:
        dict: Mapping of PDF filename to markdown path
    """
    pdf_folder = Path(pdf_folder)
    conversions = {}
    
    for pdf_path in pdf_folder.glob("*.pdf"):
        md_path = convert_pdf_to_markdown(pdf_path, output_dir)
        if md_path:
            conversions[pdf_path.name] = md_path
    
    return conversions


# Example usage for integration with run_task.py
if __name__ == "__main__":
    # Test conversion
    pdf_folder = "data/PDF_test"
    output_dir = "data/MD"
    
    print(f"Converting PDFs from {pdf_folder} to {output_dir}")
    conversions = convert_pdf_folder(pdf_folder, output_dir)
    
    print(f"\nConverted {len(conversions)} PDFs:")
    for pdf, md in conversions.items():
        print(f"  {pdf} -> {md}")