import os
import json
import tqdm

from pdf_extractor import extract_pdf_text
from drug_pdf_retriever import get_drugs_pdfs
from AI import ask_ai
from semantic_search import get_index, populate_index, query_index

# pdf_path = 'pdfs/Rishum01_14_91168324.pdf'
pdfs_dir = 'pdfs'
summaries_path = 'summaries.json'
MAX_CHUNK_SIZE = 10000  # Maximum number of characters the AI can handle
failed_path = 'failed.json'

system_prompt = """
you are a drug leaflet summarizer. You are given the content of drug user leaflet and your task is to return a paragraph
describing the drug, what is it intended for and how to use it. DO NOT USE MORE THAN 100 WORDS FOR THE SUMMARY
"""


def load_existing_summaries(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}


def pre_process_summaries():
    # For each drug get its PDF from health website
    get_drugs_pdfs()
    failed_process_list = {'files': []}

    # Iterate over all files in the directory and get summary. save the summaries to a json file.
    summaries = load_existing_summaries(summaries_path)
    for filename in tqdm.tqdm(os.listdir(pdfs_dir)):
        try:
            if filename.lower().endswith('.pdf'):
                drug_name = filename[:-4]
                pdf_path = os.path.join(pdfs_dir, filename)
                print(f"Processing file: {filename}")

                if drug_name in summaries:
                    print(f"Summary already exists for: {filename}. Skipping.")
                    continue

                # Extract text from the PDF
                try:
                    print(f"Extracting text from: {filename}")
                    pdf_content = extract_pdf_text(pdf_path)
                    if not pdf_content.strip():
                        print(f'failed to extract text from: {filename}, came back empty.')
                        failed_process_list['files'].append(filename)
                        continue
                except Exception as e:
                    print(f'failed to extract text from: {filename}')
                    failed_process_list['files'].append(filename)
                    continue

                # Get the summary from the AI model
                print(f"Generating summary for: {filename}")
                chunks = [pdf_content[i:i + MAX_CHUNK_SIZE] for i in range(0, len(pdf_content), MAX_CHUNK_SIZE)]

                # Summarize each chunk and combine the results
                summary = ""
                for chunk in chunks:
                    print(f"Summarizing chunk of size {len(chunk)} characters...")
                    chunk_summary = ask_ai(chunk, system_prompt)
                    summary += chunk_summary + " "  # Append chunk summary

                # Save the summary to the map
                summaries[drug_name] = summary.strip()
        except Exception as e:
            print(f'failed to process file: {filename}.')
            failed_process_list['files'].append(filename)

    # Save the summaries to a JSON file
    print("Saving summaries to JSON file...")
    with open(summaries_path, 'w', encoding='utf-8') as file:
        json.dump(summaries, file, ensure_ascii=False, indent=4)

    print("Summaries have been saved to:", summaries_path)

    with open(failed_path, 'w', encoding='utf-8') as file:
        json.dump(failed_process_list, file, ensure_ascii=False, indent=4)

    print("failed filenames have been saved to:", failed_path)


def pre_process_index():
    # Get summaries
    with open(summaries_path, 'r', encoding='utf-8') as file:
        summaries = json.load(file)

    # populate pinecone index with summaries
    index = get_index()
    populate_index([(drug, summaries[drug]) for drug in summaries], index)


def query():
    index = get_index()

    while True:
        res = query_index(input('what drug are you looking for?\n'), index)
        print('The following drugs fit the request:')
        drugs = res['matches']

        for drug in drugs:
            print(f"drug name: {drug['metadata']['drug']}")
            print(f"drug description: {drug['metadata']['text']}")
            print()


def pre_process():
    pre_process_summaries()
    pre_process_index()


if __name__ == '__main__':
    pre_process()
    # query()
