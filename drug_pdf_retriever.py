import requests
import json
import os

base_drug_url = 'https://mohpublic.z6.web.core.windows.net/IsraelDrugs/'
all_drug_names_url = 'https://medlookup.org/getAllDrugNames'
get_drugs_info_url = 'https://medlookup.org/getDragsInfo'
all_drug_names_file_path = 'all_drug_names.json'
download_dir = 'pdfs'


def get_drug_names():
    # Check if the JSON file already exists
    if os.path.exists(all_drug_names_file_path):
        # Read the JSON data from the file
        try:
            with open(all_drug_names_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            print("Loaded JSON data from file.")
            return data
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            return None
    else:
        # Fetch the JSON data from the server
        try:
            response = requests.get(all_drug_names_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            response.encoding = 'utf-8'  # Ensure the response is treated as UTF-8
            data = response.json()  # Parse the JSON content

            # Save the JSON data to a file
            try:
                with open(all_drug_names_file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                print("Saved JSON data to file.")
            except Exception as e:
                print(f"An error occurred while saving the file: {e}")

            return data
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None


def get_drugs_info(drug_names):
    payload = {"d": drug_names}

    try:
        # Send the POST request with the JSON payload
        response = requests.post(get_drugs_info_url, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Get and return the response data
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def get_drugs_leaflets(drug_names, language):
    response = get_drugs_info(drug_names)
    leaflets = list(set([response[drug][language]['l'] for drug in response]))
    leaflets_urls = list(map(lambda pdf: base_drug_url + pdf, leaflets))

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    for url in leaflets_urls:
        try:
            # Get the filename from the URL
            filename = os.path.basename(url)
            file_path = os.path.join(download_dir, filename)

            # Send a GET request to the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Write the content to a file
            with open(file_path, 'wb') as file:
                file.write(response.content)

            print(f"Successfully downloaded {filename}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while downloading {url}: {e}")

all_drugs = get_drug_names()['drugs']
get_drugs_leaflets(all_drugs[:6], 'e')