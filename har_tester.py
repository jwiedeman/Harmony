import json
import csv

# Function to read HAR file
def read_har(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to perform basic tests on HAR data
def perform_tests(har_data):
    results = []
    # Example test: Check if there are any entries
    if 'log' in har_data and 'entries' in har_data['log']:
        results.append({'test': 'Entries exist', 'result': 'Pass' if har_data['log']['entries'] else 'Fail'})
    else:
        results.append({'test': 'Entries exist', 'result': 'Fail'})
    return results

# Function to write test results to CSV
def write_results_to_csv(results, output_path):
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['test', 'result', 'details']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({**result, 'details': result.get('details', 'N/A')})

# Example usage
if __name__ == "__main__":
    har_data = read_har('example.har')
    test_results = perform_tests(har_data)
    write_results_to_csv(test_results, 'test_results.csv')