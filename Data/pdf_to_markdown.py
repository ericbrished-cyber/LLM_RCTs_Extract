import os
import pdfplumber

def pdf_to_markdown(pdf_folder, markdown_folder):
    """
    Converts all PDF files in a folder to plain text and saves them as Markdown files.
    
    Args:
        pdf_folder (str): Path to the folder containing PDF files.
        markdown_folder (str): Path to the folder where Markdown files will be saved.
    """
    # Ensure the output folder exists
    os.makedirs(markdown_folder, exist_ok=True)

    # Loop through all files in the PDF folder
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith(".pdf"):  # Process only PDF files
            pdf_path = os.path.join(pdf_folder, pdf_file)
            markdown_file_name = os.path.splitext(pdf_file)[0] + ".md"
            markdown_path = os.path.join(markdown_folder, markdown_file_name)
            
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                
                # Save the extracted text to a Markdown file
                with open(markdown_path, "w", encoding="utf-8") as markdown_file:
                    markdown_file.write(text)
                
                print(f"Converted {pdf_file} to {markdown_file_name}")
            except Exception as e:
                print(f"Error processing PDF {pdf_file}: {e}")

pdf_to_markdown(pdf_folder="./PDF", markdown_folder="./Markdown")