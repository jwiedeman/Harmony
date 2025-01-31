# Harmony

Harmony is a tool designed to analyze HAR (HTTP Archive) files and apply test cases to verify the presence and values of specific parameters in network requests. This README provides a comprehensive guide to getting started with Harmony, including installation instructions, usage, and details on the expected format of input and output files.

## Quickstart Guide

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/jwiedeman/Harmony.git
   cd Harmony
   ```

2. **Install Dependencies**
   Ensure you have Python installed, then install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running Harmony

1. **Prepare Test Cases**
   - Edit the `test_cases.xlsx` file to define your test cases. Use the following format:
     - **Test Name**: A unique identifier for the test case.
     - **Description**: A brief description of what the test case checks.
     - **Target URLs**: A comma-separated list of URL patterns to which the test case applies.
     - **Parameter Name**: The name of the parameter to check in the HAR data.
     - **Condition**: The condition to check for the parameter (e.g., `exists`, `equals`).
     - **Expected Value**: The expected value for the parameter (used with the `equals` condition).
     - **Optional**: A flag indicating if the parameter is optional (`True` or `False`).
     - **On Pass Message**: The message to display if the test passes. Use `{value}` and `{url}` as placeholders.
     - **On Fail Message**: The message to display if the test fails. Use `{url}` as a placeholder.

2. **Place HAR Files**
   - Drop your HAR files into the project root directory.

3. **Execute the Script**
   ```bash
   python harmony.py
   ```

4. **View Results**
   - Results will be saved in `harmony_test_results.xlsx`, formatted according to the template.

## How to Use Harmony

- **Test Cases**: Define your test cases in `test_cases.xlsx` using the format described above.
- **HAR Files**: Place your HAR files in the project root directory.
- **Run Harmony**: Execute the script to process the HAR files and apply the test cases.
- **Results**: Check the `harmony_test_results.xlsx` file for the results of the test cases.

## Excel File Formats

### Test Cases (test_cases.xlsx)

| Column          | Description                                                                 |
|-----------------|-----------------------------------------------------------------------------|
| Test Name       | Unique identifier for the test case.                                        |
| Description     | Brief description of the test case.                                         |
| Target URLs     | Comma-separated list of URL patterns.                                        |
| Parameter Name  | Name of the parameter to check.                                              |
| Condition       | Condition to check (e.g., `exists`, `equals`).                              |
| Expected Value  | Expected value for the parameter (used with `equals` condition).             |
| Optional        | Flag indicating if the parameter is optional (`True` or `False`).            |
| On Pass Message | Message displayed if the test passes. Use `{value}` and `{url}` as placeholders. |
| On Fail Message | Message displayed if the test fails. Use `{url}` as a placeholder.           |

### Test Results (harmony_test_results.xlsx)

| Column    | Description                        |
|-----------|------------------------------------|
| URL       | The URL of the request.            |
| Parameter | The parameter being checked.       |
| Result    | The result of the test (Pass/Fail).|
| Details   | Additional details about the result.|

### Analysis (template.xlsx)

#### Sheet: Analysis

| Column          | Description                        |
|-----------------|------------------------------------|
| Metric          | Name of the metric.                |
| Value           | Value of the metric.               |
| URL Failures    | List of URLs with failures.        |
| Count           | Count of failures per URL.         |
| Dimension Failures | List of dimension failures.     |
| Count           | Count of failures per dimension.   |

## Cheat Sheet

Refer to the [Cheat Sheet](README_CheatSheet.md) for detailed information on creating test cases.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.