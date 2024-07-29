from pdf_extractor import extract_pdf_text
from AI import ask_ai

pdf_path = 'pdfs/Rishum01_14_91168324.pdf'


system_prompt = """
please provide a quote supporting each step.
you are a drug leaflet summarizer. You are given the content of drug user leaflet and your task is to return a paragraph
describing the drug, what is it intended for and how to use it.
"""


def main():
    # For each drug get its PDF from health website

    # For each PDF extract text
    pdf_content = extract_pdf_text(pdf_path)
    summary = ask_ai(pdf_content, system_prompt)

    print(summary)

    # For each extracted text, ask AI to summarize it

    # Save summaries to a json file

    # populate pinecone index with summaries

    # query the index for a given drug and return top k results


if __name__ == '__main__':
    main()
