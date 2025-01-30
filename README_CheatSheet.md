# Test Case CSV Cheat Sheet

This cheat sheet provides an overview of the columns and options available for creating test cases in the CSV format. Use this guide to build new test cases for the Harmony crawler.

## CSV Columns

- **Test Name**: A unique identifier for the test case.
  - Example: `app_build_check`

- **Description**: A brief description of what the test case checks.
  - Example: `Check if 'app_build' parameter exists.`

- **Target URLs**: A comma-separated list of URL patterns to which the test case applies.
  - Example: `metrics,smetrics,a.fox.com,b.fox.com`

- **Parameter Name**: The name of the parameter to check in the HAR data.
  - Example: `app_build`

- **Condition**: The condition to check for the parameter. Options include:
  - `exists`: Check if the parameter exists.
  - `equals`: Check if the parameter equals a specific value.

- **Expected Value**: The expected value for the parameter (used with the `equals` condition).
  - Example: `foxnewsglobalproduction`

- **Optional**: A flag indicating if the parameter is optional. Use `True` or `False`.
  - Example: `False`

- **On Pass Message**: The message to display if the test passes. Use `{value}` and `{url}` as placeholders.
  - Example: `Pass: 'app_build' parameter found with value {value}. URL: {url}.`

- **On Fail Message**: The message to display if the test fails. Use `{url}` as a placeholder.
  - Example: `Fail: 'app_build' parameter missing. URL: {url}. Please add the 'app_build' parameter.`

## Creating New Test Cases

1. Open the `test_cases.csv` file.
2. Add a new row with the desired test case details.
3. Save the file and run the Harmony crawler to apply the new test cases.

## Example Test Case

```
Test Name,Description,Target URLs,Parameter Name,Condition,Expected Value,Optional,On Pass Message,On Fail Message
app_build_check,Check if 'app_build' parameter exists.,"metrics,smetrics,a.fox.com,b.fox.com",app_build,exists,,False,Pass: 'app_build' parameter found with value {value}. URL: {url}.,Fail: 'app_build' parameter missing. URL: {url}. Please add the 'app_build' parameter.
```

Use this cheat sheet as a reference to create comprehensive and effective test cases for your HAR data analysis.