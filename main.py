import requests
import json
import os
import concurrent.futures
import signal
import sys

# Define the base URL and paths
base_url = "https://github.com/duckduckgo/tracker-radar/tree/main/domains"
raw_base_url = "https://raw.githubusercontent.com/duckduckgo/tracker-radar/main/domains"
base_folder = "domains"

# Function to process a single country and its files
def process_country(country):
    try:
        country_url = f"{base_url}/{country}"
        country_response = requests.get(country_url)
        country_response_json = json.loads(country_response.text)

        print(f"Parsing: {country}")
        for file in country_response_json['payload']['tree']['items']:
            domain_name = file['name']
            file_url = f"{raw_base_url}/{country}/{domain_name}"
            file_response = requests.get(file_url)
            file_response_json = json.loads(file_response.text)

            subdomains = file_response_json.get('subdomains', [])
            if subdomains:
                subdomain_only = domain_name.split('.json')[0]
                full_urls = [f"{subdomain}.{subdomain_only}" for subdomain in subdomains]
                file_path = os.path.join(base_folder, f"{subdomain_only}.txt")

                # Set to keep track of entries in the file
                existing_entries = set()

                # Read existing entries in the file, if the file exists
                if os.path.exists(file_path):
                    with open(file_path, "r") as file_read:
                        existing_entries.update(file_read.read().splitlines())

                # Check for duplicates and append non-duplicates
                new_entries = [entry for entry in full_urls if entry not in existing_entries]

                if new_entries:
                    with open(file_path, "a") as file_write:
                        file_write.write("\n".join(new_entries) + "\n")
    except Exception as e:
        print(f"Error processing {country}: {str(e)}")

def search_domain(domain_to_search):
    try:
        r = requests.get(base_url)
        response = json.loads(r.text)

        for item in response['payload']['tree']['items']:
            country = item['name']
            country_url = f"{base_url}/{country}"
            country_response = requests.get(country_url)
            country_response_json = json.loads(country_response.text)

            for file in country_response_json['payload']['tree']['items']:
                domain_name = file['name']
                if domain_name.endswith('.json'):
                    domain_name = domain_name[:-5]  # Remove the '.json' extension
                file_url = f"{raw_base_url}/{country}/{file['name']}"
                file_response = requests.get(file_url)
                file_response_json = json.loads(file_response.text)

                if domain_to_search == domain_name:
                    print(f"Domain: {domain_to_search}")
                    print("Subdomains:")
                    for subdomain in file_response_json.get('subdomains', []):
                        print(f"{subdomain}.{domain_name}")
                    sys.exit(0)
    except Exception as e:
        print(f"Error searching for domain: {str(e)}")

def signal_handler(sig, frame):
    print("\nCtrl+C detected. Exiting gracefully.")
    sys.exit(0)

if __name__ == "__main__":
    # Set up a Ctrl+C signal handler
    signal.signal(signal.SIGINT, signal_handler)

    if len(sys.argv) != 2:
        print("Usage: ddg.py [scrape | search domain.com]")
        sys.exit(1)

    action = sys.argv[1]

    if action == "scrape":
        r = requests.get(base_url)
        response = json.loads(r.text)

        if not os.path.exists(base_folder):
            os.mkdir(base_folder)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            country_items = [item['name'] for item in response['payload']['tree']['items']]
            executor.map(process_country, country_items)

        print("Scraping Done")

    elif action == "search":
        argument = sys.argv[2]
        search_domain(argument)

    else:
        print("Invalid action. Use 'scrape' or 'search'.")
        sys.exit(1)
