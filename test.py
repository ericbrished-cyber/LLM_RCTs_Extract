import json
import langextract as lx
import textwrap

# Load the JSON file
with open('gold-standard/annotated_rct_dataset.json', 'r') as file:
    data = json.load(file)

# Load the templates
with open('prompt_templates/templates_binary.yaml', 'r') as binary_template_file:
    binary_template = binary_template_file.read()

with open('prompt_templates/templates_continuous.yaml', 'r') as continuous_template_file:
    continuous_template = continuous_template_file.read()

# Create the dictionary and fill templates
result_dict = {}
for entry in data:
    if "id" in entry:
        result_dict[entry["id"]] = [
            entry["intervention"],
            entry["comparator"],
            entry["outcome"],
            entry["outcome_type"]
        ]
        # Replace placeholders in the templates
        if entry["outcome_type"] == "binary":
            examples = [
                    lx.data.ExampleData(
                        text="ROMEO. But soft! What light through yonder window breaks? It is the east, and Juliet is the sun.",
                        extractions=[
                            lx.data.Extraction(
                                extraction_class="character",
                                extraction_text="ROMEO",
                                attributes={"emotional_state": "wonder"}
                            ),
                            lx.data.Extraction(
                                extraction_class="emotion",
                                extraction_text="But soft!",
                                attributes={"feeling": "gentle awe"}
                            ),
                            lx.data.Extraction(
                                extraction_class="relationship",
                                extraction_text="Juliet is the sun",
                                attributes={"type": "metaphor"}
                            ),
                        ]
                    )
                ]
                 
            filled_prompt = binary_template.replace("{{intervention}}", entry["intervention"]) \
                                           .replace("{{comparator}}", entry["comparator"]) \
                                           .replace("{{outcome}}", entry["outcome"])
        else:
            filled_prompt = continuous_template.replace("{{intervention}}", entry["intervention"]) \
                                               .replace("{{comparator}}", entry["comparator"]) \
                                               .replace("{{outcome}}", entry["outcome"])
            
            examples = [
                    lx.data.ExampleData(
                        text="ROMEO. But soft! What light through yonder window breaks? It is the east, and Juliet is the sun.",
                        extractions=[
                            lx.data.Extraction(
                                extraction_class="character",
                                extraction_text="ROMEO",
                                attributes={"emotional_state": "wonder"}
                            ),
                            lx.data.Extraction(
                                extraction_class="emotion",
                                extraction_text="But soft!",
                                attributes={"feeling": "gentle awe"}
                            ),
                            lx.data.Extraction(
                                extraction_class="relationship",
                                extraction_text="Juliet is the sun",
                                attributes={"type": "metaphor"}
                            ),
                        ]
                    )
                ]
        # 1. Define the prompt and extraction rules
        prompt = filled_prompt

        # 2. Provide a high-quality example to guide the model
        # The input text to be processed
        input_text = get_fulltext_from_id(entry)

        # Run the extraction
        result = lx.extract(
            text_or_documents=input_text,
            prompt_description=prompt,
            examples=examples,
            model_id="gemini-2.5-flash",
        )


        print(f"ID: {entry['id']}\n{filled_prompt}\n")

