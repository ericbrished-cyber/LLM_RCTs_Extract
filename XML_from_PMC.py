import os
from pathlib import Path
from Bio import Entrez
from Bio.Entrez import efetch
import time

# Set your email (required by NCBI)
Entrez.email = "isak@truedson.se"  # CHANGE THIS TO YOUR EMAIL


def download_pmc_xml(pmcid, output_dir="data/XML"):
    """
    Download full-text XML from PubMed Central for a given PMCID.
    
    Args:
        pmcid (int or str): The PMCID (without 'PMC' prefix)
        output_dir (str): Directory to save XML files
    
    Returns:
        str: Path to downloaded XML file, or None if failed
    """
    # Ensure pmcid is string without PMC prefix
    pmcid_str = str(pmcid).replace("PMC", "")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    xml_path = output_dir / f"PMC{pmcid_str}.xml"
    
    # Skip if already downloaded
    if xml_path.exists():
        print(f"PMC{pmcid_str}: Already exists, skipping")
        return str(xml_path)
    
    try:
        print(f"PMC{pmcid_str}: Downloading...", end=" ")
        
        # Fetch XML from PMC
        handle = efetch(db="pmc", id=pmcid_str, retmode="xml")
        xml_content = handle.read().decode("utf-8") # type: ignore
        handle.close()
        
        # Write to file
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        
        print("✓ Success")
        return str(xml_path)
    
    except Exception as e:
        print(f"✗ Failed: {e}")
        return None


def download_pmc_xmls(pmcids, output_dir="data/XML", delay=0.5):
    """
    Download multiple PMC XML files.
    
    Args:
        pmcids (list): List of PMCIDs
        output_dir (str): Directory to save XML files
        delay (float): Delay between requests in seconds (be nice to NCBI servers)
    
    Returns:
        dict: Mapping of PMCID to download status
    """
    results = {}
    
    print(f"Downloading {len(pmcids)} XML files to {output_dir}\n")
    
    for i, pmcid in enumerate(pmcids, 1):
        print(f"[{i}/{len(pmcids)}] ", end="")
        xml_path = download_pmc_xml(pmcid, output_dir)
        results[pmcid] = xml_path
        
        # Be polite to NCBI servers - add delay between requests
        if i < len(pmcids):
            time.sleep(delay)
    
    # Summary
    successful = sum(1 for path in results.values() if path is not None)
    print(f"\n{'='*50}")
    print(f"Downloaded: {successful}/{len(pmcids)} files")
    print(f"Location: {os.path.abspath(output_dir)}")
    
    return results


def download_from_pdf_folder(pdf_folder="data/PDF_test", output_dir="data/XML"):
    """
    Download XML files for all PDFs in a folder based on their filenames.
    Assumes PDF filenames contain PMCIDs.
    
    Args:
        pdf_folder (str): Path to folder containing PDFs
        output_dir (str): Directory to save XML files
    
    Returns:
        dict: Mapping of PMCID to download status
    """
    import re
    
    pdf_folder = Path(pdf_folder)
    pmcids = []
    
    # Extract PMCIDs from PDF filenames
    PMCID_RE = re.compile(r'(?:PMCID)?(\d{6,8})', re.IGNORECASE)
    
    for pdf_path in pdf_folder.glob("*.pdf"):
        match = PMCID_RE.search(pdf_path.stem)
        if match:
            pmcids.append(match.group(1))
    
    if not pmcids:
        print(f"No PMCIDs found in {pdf_folder}")
        return {}
    
    print(f"Found {len(pmcids)} PMCIDs from PDF filenames")
    return download_pmc_xmls(pmcids, output_dir)


# Example usage
if __name__ == "__main__":
    # Option 1: Download specific PMCIDs
    # download_pmc_xmls(pmcids, output_dir="data/XML")
    
    # Option 2: Download based on PDFs in folder
    download_from_pdf_folder("data/PDF_test", "data/XML_fulltext")