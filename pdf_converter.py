import os
from pathlib import Path
import pymupdf4llm


def convert_pdf_to_markdown(pdf_path, output_dir="data/Markdown"):
    """
    Convert a PDF to Markdown using pymupdf4llm for superior layout analysis.
    
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
        # Use pymupdf4llm with table formatting options
        markdown_text = pymupdf4llm.to_markdown(
            str(pdf_path),
            page_chunks=False,  # Don't split into page chunks
            write_images=False,  # Don't extract images
        )
        
        # Write to file
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        
        return str(md_path)
    
    except Exception as e:
        print(f"Error converting {pdf_path}: {e}")
        return None


def convert_pdf_folder(pdf_folder, output_dir="data/Markdown"):
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

# Example usage
if __name__ == "__main__":
    # Test conversion
    pdf_folder = "data/PDF_test"
    output_dir = "data/Markdown"
    
    print(f"Converting PDFs from {pdf_folder} to {output_dir}")
    conversions = convert_pdf_folder(pdf_folder, output_dir)
    
    print(f"\nConverted {len(conversions)} PDFs:")
    for pdf, md in conversions.items():
        print(f"  {pdf} -> {md}")