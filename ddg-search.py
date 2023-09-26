import requests
import json
import sys

# Define the base URL and paths
base_url = "https://github.com/duckduckgo/tracker-radar/tree/main/domains"
raw_base_url = "https://raw.githubusercontent.com/duckduckgo/tracker-radar/main/domains"

# Function to search for a domain and retrieve its subdomains
def search_domain(domain_to_search):
    try:
        # Get the list of countries
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
                        print(f"- {subdomain}")
                    sys.exit(0)
    except Exception as e:
        print(f"Error searching for domain: {str(e)}")

if __name__ == "__main__":
    domain_to_search = input("Enter the domain to search: ")
    search_domain(domain_to_search)
