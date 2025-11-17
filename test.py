"""
Test suite for extraction pipeline capabilities.
Run individual tests or all tests to verify system functionality.
"""

import os
import sys
from pathlib import Path
import json
from utils import (
    list_pmcids,
    get_xml,
    get_fulltext,
    get_icos,
    get_prompt_static,
    get_prompt_with_icos,
    get_fewshotexamples_static
)
from pdf_converter import convert_pdf_to_markdown
from XML_from_PMC import download_pmc_xml


def test_list_pmcids():
    """Test: Can we list PMCIDs from PDF folder?"""
    print("\n" + "="*60)
    print("TEST: List PMCIDs from PDF folder")
    print("="*60)
    
    pdf_folder = "data/PDF_test"
    pmcids = list_pmcids(pdf_folder)
    
    print(f"✓ Found {len(pmcids)} PMCIDs: {pmcids[:5]}..." if len(pmcids) > 5 else f"✓ Found {len(pmcids)} PMCIDs: {pmcids}")
    
    if len(pmcids) == 0:
        print("⚠ WARNING: No PMCIDs found. Check PDF filenames.")
        return False
    
    return True


def test_xml_download():
    """Test: Can we download XML from PMC?"""
    print("\n" + "="*60)
    print("TEST: Download XML from PMC")
    print("="*60)
    
    test_pmcid = "4493951"  # Use a known PMC article
    output_dir = "data/XML_test"
    
    print(f"Testing with PMCID: {test_pmcid}")
    xml_path = download_pmc_xml(test_pmcid, output_dir=output_dir)
    
    if xml_path and os.path.exists(xml_path):
        file_size = os.path.getsize(xml_path) / 1024  # KB
        print(f"✓ Downloaded XML: {xml_path}")
        print(f"✓ File size: {file_size:.1f} KB")
        
        # Check if it's valid XML
        with open(xml_path, 'r', encoding='utf-8') as f:
            content = f.read(100)
            if content.startswith('<?xml') or content.startswith('<'):
                print("✓ Valid XML format")
                return True
            else:
                print("✗ Invalid XML format")
                return False
    else:
        print(f"✗ Failed to download XML for PMCID {test_pmcid}")
        return False


def test_pdf_conversion():
    """Test: Can we convert PDF to Markdown?"""
    print("\n" + "="*60)
    print("TEST: Convert PDF to Markdown")
    print("="*60)
    
    pdf_folder = "data/PDF_test"
    pdf_files = list(Path(pdf_folder).glob("*.pdf"))
    
    if not pdf_files:
        print("⚠ WARNING: No PDFs found in test folder")
        return False
    
    test_pdf = pdf_files[0]
    output_dir = "data/Markdown_test"
    
    print(f"Testing with: {test_pdf.name}")
    md_path = convert_pdf_to_markdown(test_pdf, output_dir=output_dir)
    
    if md_path and os.path.exists(md_path):
        file_size = os.path.getsize(md_path) / 1024  # KB
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            word_count = len(content.split())
        
        print(f"✓ Converted to Markdown: {md_path}")
        print(f"✓ File size: {file_size:.1f} KB")
        print(f"✓ Word count: {word_count:,}")
        print(f"✓ Preview: {content[:200]}...")
        return True
    else:
        print(f"✗ Failed to convert PDF: {test_pdf}")
        return False


def test_icos_retrieval():
    """Test: Can we retrieve ICOs from annotations?"""
    print("\n" + "="*60)
    print("TEST: Retrieve ICOs from annotations")
    print("="*60)
    
    pdf_folder = "data/PDF_test"
    pmcids = list_pmcids(pdf_folder)
    
    if not pmcids:
        print("⚠ WARNING: No PMCIDs to test")
        return False
    
    test_pmcid = pmcids[0]
    icos = get_icos(test_pmcid)
    
    print(f"Testing with PMCID: {test_pmcid}")
    print(f"✓ Found {len(icos)} ICO entries")
    
    if icos:
        for entry_id, (intervention, comparator, outcome) in list(icos.items())[:3]:
            print(f"  - {intervention} vs {comparator} for {outcome}")
        if len(icos) > 3:
            print(f"  ... and {len(icos) - 3} more")
        return True
    else:
        print(f"⚠ No ICOs found for PMCID {test_pmcid}")
        return False


def test_prompt_generation():
    """Test: Can we generate prompts correctly?"""
    print("\n" + "="*60)
    print("TEST: Prompt generation")
    print("="*60)
    
    # Test static prompt
    print("\n1. Testing static prompt...")
    static_prompt = get_prompt_static()
    print(f"✓ Static prompt loaded: {len(static_prompt)} characters")
    print(f"✓ Preview: {static_prompt[:150]}...")
    
    # Test ICO-guided prompt
    print("\n2. Testing ICO-guided prompt...")
    pdf_folder = "data/PDF_test"
    pmcids = list_pmcids(pdf_folder)
    
    if pmcids:
        test_pmcid = pmcids[0]
        icos = get_icos(test_pmcid)
        if icos:
            ico_prompt = get_prompt_with_icos(test_pmcid)
            print(f"✓ ICO prompt generated for PMCID {test_pmcid}: {len(ico_prompt)} characters")
            print(f"✓ Found {len(icos)} ICOs")
            print(f"✓ Preview:\n{ico_prompt[:300]}...")
        else:
            print(f"⚠ No ICOs found for PMCID {test_pmcid}")
    else:
        print("⚠ No PMCIDs available for testing")
    
    return True


def test_examples_loading():
    """Test: Can we load few-shot examples?"""
    print("\n" + "="*60)
    print("TEST: Load few-shot examples")
    print("="*60)
    
    # Test PDF examples
    print("\n1. Testing PDF examples...")
    try:
        pdf_examples = get_fewshotexamples_static(xml=False)
        print(f"✓ Loaded {len(pdf_examples)} PDF examples")
        if pdf_examples:
            print(f"✓ First example length: {len(pdf_examples[0].text)} characters")
    except FileNotFoundError as e:
        print(f"⚠ PDF examples not found: {e}")
    
    # Test XML examples
    print("\n2. Testing XML examples...")
    try:
        xml_examples = get_fewshotexamples_static(xml=True)
        print(f"✓ Loaded {len(xml_examples)} XML examples")
        if xml_examples:
            print(f"✓ First example length: {len(xml_examples[0].text)} characters")
    except FileNotFoundError as e:
        print(f"⚠ XML examples not found: {e}")
    
    return True


def test_file_access():
    """Test: Can we read XML and Markdown files?"""
    print("\n" + "="*60)
    print("TEST: File access (XML and Markdown)")
    print("="*60)
    
    pdf_folder = "data/PDF_test"
    pmcids = list_pmcids(pdf_folder)
    
    if not pmcids:
        print("⚠ WARNING: No PMCIDs to test")
        return False
    
    test_pmcid = pmcids[0]
    
    # Test XML access
    print(f"\n1. Testing XML access for PMCID {test_pmcid}...")
    xml_content = get_xml(test_pmcid, xml_folder_path="data/XML_fulltext")
    if xml_content.startswith("XML file for PMCID"):
        print(f"⚠ XML not found (expected if not downloaded yet)")
    else:
        print(f"✓ XML loaded: {len(xml_content)} characters")
        print(f"✓ Preview: {xml_content[:100]}...")
    
    # Test Markdown access
    print(f"\n2. Testing Markdown access for PMCID {test_pmcid}...")
    md_content = get_fulltext(test_pmcid, text_folder_path="data/Markdown")
    if md_content.startswith("Markdown file for PMCID"):
        print(f"⚠ Markdown not found (expected if not converted yet)")
    else:
        print(f"✓ Markdown loaded: {len(md_content)} characters")
        word_count = len(md_content.split())
        print(f"✓ Word count: {word_count:,}")
    
    return True


def test_output_structure():
    """Test: Do output folders exist and are they writable?"""
    print("\n" + "="*60)
    print("TEST: Output folder structure")
    print("="*60)
    
    folders = {
        "PDF input": "data/PDF_test",
        "Markdown": "data/Markdown",
        "XML": "data/XML_fulltext",
        "Outputs": "./outputs"
    }
    
    all_ok = True
    for name, folder in folders.items():
        path = Path(folder)
        if path.exists():
            print(f"✓ {name}: {folder} (exists)")
            # Test writability
            test_file = path / ".test_write"
            try:
                test_file.touch()
                test_file.unlink()
                print(f"  └─ Writable: Yes")
            except:
                print(f"  └─ Writable: No ⚠")
                all_ok = False
        else:
            print(f"✗ {name}: {folder} (missing)")
            all_ok = False
    
    return all_ok


def test_extraction_dry_run():
    """Test: Can we do a dry run of extraction setup (no actual extraction)?"""
    print("\n" + "="*60)
    print("TEST: Extraction dry run (setup only)")
    print("="*60)
    
    pdf_folder = "data/PDF_test"
    pmcids = list_pmcids(pdf_folder)
    
    if not pmcids:
        print("⚠ WARNING: No PMCIDs to test")
        return False
    
    test_pmcid = pmcids[0]
    
    print(f"Testing extraction setup for PMCID: {test_pmcid}\n")
    
    # Test "all" mode with XML
    print("1. Mode: all + XML")
    try:
        xml_content = get_xml(test_pmcid, xml_folder_path="data/XML_fulltext")
        prompt = get_prompt_static()
        examples = get_fewshotexamples_static(xml=True)
        print(f"   ✓ Input ready: {len(xml_content)} chars")
        print(f"   ✓ Prompt ready: {len(prompt)} chars")
        print(f"   ✓ Examples ready: {len(examples)} examples")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test "guided" mode with PDF
    print("\n2. Mode: guided + PDF")
    try:
        md_content = get_fulltext(test_pmcid, text_folder_path="data/Markdown")
        icos = get_icos(test_pmcid)
        prompt = get_prompt_with_icos(icos) if icos else get_prompt_static()
        examples = get_fewshotexamples_static(xml=False)
        print(f"   ✓ Input ready: {len(md_content)} chars")
        print(f"   ✓ ICOs: {len(icos)} entries")
        print(f"   ✓ Prompt ready: {len(prompt)} chars")
        print(f"   ✓ Examples ready: {len(examples)} examples")
    except Exception as e:
        print(f"   ⚠ Some components missing: {e}")
    
    return True


def run_all_tests():
    """Run all tests and report summary."""
    print("\n" + "="*60)
    print("RUNNING ALL CAPABILITY TESTS")
    print("="*60)
    
    tests = [
        ("List PMCIDs", test_list_pmcids),
        ("XML Download", test_xml_download),
        ("PDF Conversion", test_pdf_conversion),
        ("ICOs Retrieval", test_icos_retrieval),
        ("Prompt Generation", test_prompt_generation),
        ("Examples Loading", test_examples_loading),
        ("File Access", test_file_access),
        ("Output Structure", test_output_structure),
        ("Extraction Dry Run", test_extraction_dry_run),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Check output above.")
    
    return results


# Individual test runners for convenience
if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        tests_map = {
            "pmcids": test_list_pmcids,
            "xml": test_xml_download,
            "pdf": test_pdf_conversion,
            "icos": test_icos_retrieval,
            "prompts": test_prompt_generation,
            "examples": test_examples_loading,
            "files": test_file_access,
            "folders": test_output_structure,
            "dryrun": test_extraction_dry_run,
        }
        
        if test_name in tests_map:
            tests_map[test_name]()
        elif test_name == "all":
            run_all_tests()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available tests: {', '.join(tests_map.keys())}, all")
    else:
        # Default: run all tests
        run_all_tests()