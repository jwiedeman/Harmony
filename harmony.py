import json
import os
import importlib.util
from urllib.parse import urlparse, parse_qs
from collections import OrderedDict
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Define target URL patterns to look for
TARGET_URLS = ["metrics", "smetrics", "hb", "a.fox.com", "b.fox.com"]

def find_har_file():
    """Look for any HAR file in the current directory."""
    for file in os.listdir('.'):
        if file.endswith('.har'):
            print(f"Found HAR file: {file}")
            return file
    print("No HAR file found in the current directory.")
    return None

def load_har_file(file_path):
    """Load HAR file and return parsed JSON data."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_tests():
    """Dynamically load test cases from the /tests/ directory."""
    test_cases = []
    tests_folder = './tests'
    for filename in os.listdir(tests_folder):
        if filename.endswith(".py"):
            path = os.path.join(tests_folder, filename)
            spec = importlib.util.spec_from_file_location(filename[:-3], path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            test_cases.append(module.test_case)
    return test_cases

def extract_parameters(url, post_data_params):
    """Extract parameters from both URL query and post data."""
    parsed_url = urlparse(url)
    url_params = parse_qs(parsed_url.query)
    url_params = {key: value[0] for key, value in url_params.items()}
    combined_params = {**url_params, **post_data_params}
    return combined_params

def apply_test_cases(adobe_call, test_cases):
    """Apply each test case to the adobe_call and log any flagged actions."""
    results = []
    parsed_url = urlparse(adobe_call["url"])
    call_domain = parsed_url.netloc

    for test in test_cases:
        target_urls = test.get("target_urls", [])
        if target_urls and not any(target in call_domain for target in target_urls):
            continue

        conditions_met = True
        for condition in test.get("conditions", []):
            cond_name = condition["name"]
            cond_values = condition.get("value", [])
            is_optional = condition.get("optional", False)
            param_value = adobe_call["parameters"].get(cond_name)
            if param_value:
                if cond_values and param_value not in cond_values:
                    conditions_met = False
                    break
            elif not is_optional:
                conditions_met = False
                break

        if not conditions_met:
            continue

        for action in test.get("actions", []):
            if action["type"] == "flag":
                results.append(f"Flag: {action['message']}")

        for param_check in test.get("parameter_checks", []):
            param_names = param_check.get("names", [param_check.get("name")])
            condition = param_check.get("condition", "")
            found = False
            found_value = None
            for name in param_names:
                if name in adobe_call["parameters"]:
                    found = True
                    found_value = adobe_call["parameters"][name]
                    break

            if condition == "exists":
                if found:
                    results.append(Fore.GREEN + param_check["on_pass"].format(value=found_value, url=adobe_call["url"]) + Style.RESET_ALL)
                else:
                    results.append(Fore.RED + param_check["on_fail"] + Style.RESET_ALL)

    return results

def parse_har_for_adobe_calls(har_data, test_cases):
    adobe_calls = []
    for entry in har_data['log']['entries']:
        url = entry['request']['url']
        post_data = entry['request'].get('postData', {})
        post_data_params = {param["name"]: param["value"] for param in post_data.get('params', [])}
        parameters = extract_parameters(url, post_data_params)
        
        adobe_call = {
            "url": url,
            "parameters": parameters,
            "payload": post_data.get("text", "No payload")
        }
        
        results = apply_test_cases(adobe_call, test_cases)
        if results:
            adobe_call["results"] = results
        adobe_calls.append(adobe_call)
    return adobe_calls

def combine_nested_keys(params):
    """Combine parameters with cascading keys like 'c.', '.c', 'a.', etc."""
    combined_params = OrderedDict()
    current_key = ""

    for key, value in params.items():
        if key.endswith('.') or key.startswith('.'):
            current_key += key.strip('.')
        else:
            full_key = f"{current_key}.{key}" if current_key else key
            combined_params[full_key] = value
            current_key = ""

    return combined_params

def main():
    har_file_path = find_har_file()
    if har_file_path:
        har_data = load_har_file(har_file_path)
        test_cases = load_tests()
        adobe_calls = parse_har_for_adobe_calls(har_data, test_cases)

        for call in adobe_calls:
            if "results" in call:
                print(f"URL: {call['url']}")
                combined_params = combine_nested_keys(call['parameters'])
                print("\nParameters:")
                print(json.dumps(combined_params, indent=2))
                print("\nPayload:")
                print("No payload" if call['payload'] == "No payload" else json.dumps(call['payload'], indent=2))
                print("\nResults:")
                import csv

    for result in call["results"]:
        print(result)
    # Write results to CSV
    with open('harmony_test_results.csv', 'w', newline='') as csvfile:
        fieldnames = ['url', 'parameter', 'result', 'details']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for call in adobe_calls:
            for result in call.get("results", []):
                writer.writerow({
                    'url': call['url'],
                    'parameter': result.split(':')[1].strip(),
                    'result': result.split(':')[0].strip(),
                    'details': result
                })
            print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()
