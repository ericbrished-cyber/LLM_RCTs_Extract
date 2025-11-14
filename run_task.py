import sys, time, threading, os
from utils import get_xml, list_pmcids, get_icos, get_prompt_static, get_fewshotexamples_static, visualize
import json
import langextract as lx
from dotenv import load_dotenv, find_dotenv

# Load .env early
load_dotenv(find_dotenv())

pdf_folder = "data/PDF_test"
output_folder = "./outputs"
os.makedirs(output_folder, exist_ok=True)

pmcid_lst = list_pmcids(pdf_folder)

class Spinner:
    def __init__(self, label: str):
        self.label = label
        self._stop = threading.Event()
        self._t = None
    def _spin(self):
        glyph = "|/-\\"
        i = 0
        while not self._stop.is_set():
            sys.stdout.write(f"\r{self.label} {glyph[i % 4]}")
            sys.stdout.flush()
            i += 1
            time.sleep(0.1)
        # clear line
        sys.stdout.write("\r" + " " * (len(self.label) + 2) + "\r")
        sys.stdout.flush()
    def __enter__(self):
        self._t = threading.Thread(target=self._spin, daemon=True)
        self._t.start()
        return self
    def __exit__(self, *exc):
        self._stop.set()
        if self._t:
            self._t.join()

def run_task(model="gemini-2.5-flash"):
    total = len(pmcid_lst)
    print(f"Found {total} PDFs. Output → {os.path.abspath(output_folder)}", flush=True)

    for i, pmcid in enumerate(pmcid_lst, 1):
        label = f"[{i}/{total}] PMCID={pmcid} extracting…"
        prompt = get_prompt_static()
        input_text = get_xml(pmcid)
        examples = get_fewshotexamples_static()

        try:
            with Spinner(label):
                result = lx.extract(
                    text_or_documents=input_text,
                    prompt_description=prompt,
                    examples=examples,
                    model_id=model,
                    api_key=os.environ.get("OPENAI_API_KEY"),
                    fence_output=True,
                    use_schema_constraints=False,
                )
            # success line
            print(f"[{i}/{total}] PMCID={pmcid} ✓ extracted. Saving…", flush=True)
            lx.io.save_annotated_documents(
                [result],
                output_name=f"{pmcid}.jsonl",
                output_dir=output_folder
            )
            print(f"[{i}/{total}] PMCID={pmcid} ✓ saved {pmcid}.jsonl", flush=True)
        except KeyboardInterrupt:
            print(f"\n[{i}/{total}] PMCID={pmcid} ✗ interrupted by user.", flush=True)
            raise
        except Exception as e:
            print(f"\n[{i}/{total}] PMCID={pmcid} ✗ failed: {e}", flush=True)

# Run with your chosen model
#run_task(model="gpt-5-mini")



visualize(5459456, output_dir=output_folder)