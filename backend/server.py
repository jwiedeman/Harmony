import os
import json
import uuid
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import openpyxl
from collections import OrderedDict
from urllib.parse import urlparse, parse_qs
import tempfile
import shutil
import glob
from openpyxl import load_workbook

app = FastAPI(title="Harmony QA API", description="QA Testing API for HAR file analysis")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TestCase(BaseModel):
    id: str
    name: str
    description: str
    target_urls: List[str]
    parameter_name: str
    condition: str
    expected_value: Optional[str] = None
    optional: bool = False
    on_pass_message: str
    on_fail_message: str

class TestResult(BaseModel):
    url: str
    parameter: str
    result: str
    details: str
    test_case_name: str

class AnalysisReport(BaseModel):
    total_requests: int
    total_tests: int
    passed_tests: int
    failed_tests: int
    url_failures: Dict[str, int]
    dimension_failures: Dict[str, int]
    detailed_results: List[TestResult]
    raw_data: List[Dict[str, Any]]

class HarFile(BaseModel):
    filename: str
    path: str
    size: int
    modified: str

# In-memory storage for analysis results
analysis_results_store = {}

# Function to load test cases from Excel file
def load_tests_from_xlsx(xlsx_path='test_cases.xlsx'):
    """Load test cases from Excel file, similar to the original helper function."""
    test_cases = []
    try:
        workbook = load_workbook(xlsx_path)
        sheet = workbook.active
        
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if not row[0]:  # Skip empty rows
                continue
                
            # Handle None values and convert to appropriate types
            target_urls = row[2].split(',') if row[2] else []
            target_urls = [url.strip() for url in target_urls if url.strip()]
            
            test_case = TestCase(
                id=str(uuid.uuid4()),
                name=str(row[0]) if row[0] else f"Test Case {row_num}",
                description=str(row[1]) if row[1] else "",
                target_urls=target_urls,
                parameter_name=str(row[3]) if row[3] else "",
                condition=str(row[4]).lower() if row[4] else "exists",
                expected_value=str(row[5]) if row[5] and row[5] != "None" else None,
                optional=str(row[6]).lower() == 'true' if row[6] else False,
                on_pass_message=str(row[7]) if row[7] else f"Parameter {row[3]} found: {{value}}",
                on_fail_message=str(row[8]) if row[8] else f"Parameter {row[3]} missing from {{url}}"
            )
            test_cases.append(test_case)
            
        print(f"Loaded {len(test_cases)} test cases from {xlsx_path}")
        return test_cases
        
    except FileNotFoundError:
        print(f"Test cases file {xlsx_path} not found. Using empty test case list.")
        return []
    except Exception as e:
        print(f"Error loading test cases from {xlsx_path}: {e}")
        return []

# Function to save test cases to Excel file
def save_tests_to_xlsx(test_cases: List[TestCase], xlsx_path='test_cases.xlsx'):
    """Save test cases to Excel file."""
    try:
        # Create new workbook
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Test Cases"
        
        # Headers
        headers = [
            "Test Name", "Description", "Target URLs", "Parameter Name", 
            "Condition", "Expected Value", "Optional", "On Pass Message", "On Fail Message"
        ]
        
        for col, header in enumerate(headers, 1):
            sheet.cell(row=1, column=col, value=header)
        
        # Data
        for row, test_case in enumerate(test_cases, 2):
            sheet.cell(row=row, column=1, value=test_case.name)
            sheet.cell(row=row, column=2, value=test_case.description)
            sheet.cell(row=row, column=3, value=', '.join(test_case.target_urls))
            sheet.cell(row=row, column=4, value=test_case.parameter_name)
            sheet.cell(row=row, column=5, value=test_case.condition)
            sheet.cell(row=row, column=6, value=test_case.expected_value or "")
            sheet.cell(row=row, column=7, value=str(test_case.optional))
            sheet.cell(row=row, column=8, value=test_case.on_pass_message)
            sheet.cell(row=row, column=9, value=test_case.on_fail_message)
        
        workbook.save(xlsx_path)
        print(f"Saved {len(test_cases)} test cases to {xlsx_path}")
        return True
        
    except Exception as e:
        print(f"Error saving test cases to {xlsx_path}: {e}")
        return False

# Function to get available HAR files
def get_available_har_files():
    """Get list of available HAR files in the project directory."""
    har_files = []
    
    # Look for HAR files in parent directory (project root) and common subdirectories  
    base_paths = [
        "../",  # Project root
        "../data/", 
        "../samples/",
        "../test_data/",
        "./",  # Current directory
        "data/",
        "samples/", 
        "test_data/"
    ]
    
    for base_path in base_paths:
        try:
            search_pattern = os.path.join(base_path, "*.har")
            for file_path in glob.glob(search_pattern):
                try:
                    stat = os.stat(file_path)
                    # Get relative path from project root
                    rel_path = os.path.relpath(file_path, "../")
                    har_files.append(HarFile(
                        filename=os.path.basename(file_path),
                        path=rel_path,
                        size=stat.st_size,
                        modified=str(stat.st_mtime)
                    ))
                except OSError:
                    continue
        except:
            continue
    
    # Remove duplicates based on filename
    seen_files = set()
    unique_har_files = []
    for har_file in har_files:
        if har_file.filename not in seen_files:
            unique_har_files.append(har_file)
            seen_files.add(har_file.filename)
    
    return unique_har_files

# Helper functions (ported from original helper_functions.py)
def extract_parameters(url: str, post_data_params: dict) -> dict:
    parsed_url = urlparse(url)
    url_params = parse_qs(parsed_url.query)
    url_params = {key: value[0] for key, value in url_params.items()}
    combined_params = {**url_params, **post_data_params}
    return combined_params

def apply_test_cases(call: dict, test_cases: List[TestCase]) -> List[tuple]:
    results = []
    parsed_url = urlparse(call["url"])
    call_domain = parsed_url.netloc
    
    for test in test_cases:
        # Check if this test applies to this URL
        if test.target_urls and not any(target in call_domain or target in call["url"] for target in test.target_urls):
            continue
        
        param_value = call["parameters"].get(test.parameter_name)
        
        if test.condition == "exists":
            if param_value is not None:
                result_msg = test.on_pass_message.format(value=param_value, url=call["url"])
                results.append((f"Pass: {result_msg}", test.parameter_name, test.name))
            else:
                if not test.optional:
                    result_msg = test.on_fail_message.format(url=call["url"])
                    results.append((f"Fail: {result_msg}", test.parameter_name, test.name))
        
        elif test.condition == "equals":
            if param_value is not None:
                if str(param_value) == str(test.expected_value):
                    result_msg = test.on_pass_message.format(value=param_value, url=call["url"])
                    results.append((f"Pass: {result_msg}", test.parameter_name, test.name))
                else:
                    result_msg = test.on_fail_message.format(url=call["url"])
                    results.append((f"Fail: Expected '{test.expected_value}' but got '{param_value}'", test.parameter_name, test.name))
            else:
                if not test.optional:
                    result_msg = test.on_fail_message.format(url=call["url"])
                    results.append((f"Fail: {result_msg}", test.parameter_name, test.name))
    
    return results

def parse_har_for_calls(har_data: dict, test_cases: List[TestCase]) -> List[dict]:
    calls = []
    for entry in har_data['log']['entries']:
        url = entry['request']['url']
        post_data = entry['request'].get('postData', {})
        
        # Parse POST data parameters
        post_data_params = {}
        if 'params' in post_data:
            post_data_params = {param["name"]: param["value"] for param in post_data.get('params', [])}
        elif 'text' in post_data:
            try:
                # Try to parse JSON from post data text
                json_data = json.loads(post_data['text'])
                if isinstance(json_data, dict):
                    post_data_params = json_data
            except:
                pass
        
        parameters = extract_parameters(url, post_data_params)
        
        call = {
            "url": url,
            "method": entry['request']['method'],
            "parameters": parameters,
            "payload": post_data.get("text", "No payload"),
            "status": entry['response']['status']
        }
        
        results = apply_test_cases(call, test_cases)
        call["results"] = results
        calls.append(call)
    
    return calls

def analyze_failures(calls: List[dict]) -> tuple:
    url_failures = {}
    dimension_failures = {}
    
    for call in calls:
        for result, param_name, test_name in call.get("results", []):
            if "Fail" in result:
                url_failures[call['url']] = url_failures.get(call['url'], 0) + 1
                dimension_failures[param_name] = dimension_failures.get(param_name, 0) + 1
    
    return url_failures, dimension_failures

# API Endpoints
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Harmony QA API"}

@app.get("/api/test-cases")
async def get_test_cases():
    test_cases = load_tests_from_xlsx()
    return {"test_cases": [tc.dict() for tc in test_cases]}

@app.post("/api/test-cases")
async def create_test_case(test_case: TestCase):
    # Load existing test cases
    test_cases = load_tests_from_xlsx()
    
    # Add new test case
    if not test_case.id:
        test_case.id = str(uuid.uuid4())
    
    test_cases.append(test_case)
    
    # Save back to Excel
    if save_tests_to_xlsx(test_cases):
        return {"message": "Test case created successfully", "id": test_case.id}
    else:
        raise HTTPException(status_code=500, detail="Failed to save test case")

@app.put("/api/test-cases/{test_case_id}")
async def update_test_case(test_case_id: str, test_case: TestCase):
    # Load existing test cases
    test_cases = load_tests_from_xlsx()
    
    # Find and update the test case
    updated = False
    for i, tc in enumerate(test_cases):
        if tc.id == test_case_id:
            test_case.id = test_case_id
            test_cases[i] = test_case
            updated = True
            break
    
    if not updated:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    # Save back to Excel
    if save_tests_to_xlsx(test_cases):
        return {"message": "Test case updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update test case")

@app.delete("/api/test-cases/{test_case_id}")
async def delete_test_case(test_case_id: str):
    # Load existing test cases
    test_cases = load_tests_from_xlsx()
    
    # Find and remove the test case
    test_cases = [tc for tc in test_cases if tc.id != test_case_id]
    
    # Save back to Excel
    if save_tests_to_xlsx(test_cases):
        return {"message": "Test case deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete test case")

@app.get("/api/har-files")
async def get_har_files():
    har_files = get_available_har_files()
    return {"har_files": [hf.dict() for hf in har_files]}

@app.post("/api/analyze-har-file/{filename}")
async def analyze_har_file_by_name(filename: str):
    """Analyze a HAR file that exists in the project directory."""
    try:
        # Find the HAR file
        har_files = get_available_har_files()
        har_file = next((hf for hf in har_files if hf.filename == filename), None)
        
        if not har_file:
            raise HTTPException(status_code=404, detail=f"HAR file '{filename}' not found")
        
        # Read and parse HAR file
        with open(har_file.path, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        # Get test cases from Excel
        test_cases = load_tests_from_xlsx()
        if not test_cases:
            raise HTTPException(status_code=400, detail="No test cases found in test_cases.xlsx. Please create test cases first.")
        
        # Analyze the HAR file
        calls = parse_har_for_calls(har_data, test_cases)
        url_failures, dimension_failures = analyze_failures(calls)
        
        # Create detailed results
        detailed_results = []
        for call in calls:
            for result, param_name, test_name in call.get("results", []):
                detailed_results.append(TestResult(
                    url=call["url"],
                    parameter=param_name,
                    result="Pass" if "Pass" in result else "Fail",
                    details=result,
                    test_case_name=test_name
                ))
        
        # Create analysis report
        total_tests = len(detailed_results)
        passed_tests = len([r for r in detailed_results if r.result == "Pass"])
        failed_tests = total_tests - passed_tests
        
        report = AnalysisReport(
            total_requests=len(calls),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            url_failures=url_failures,
            dimension_failures=dimension_failures,
            detailed_results=detailed_results,
            raw_data=calls
        )
        
        # Store results
        report_id = str(uuid.uuid4())
        analysis_results_store[report_id] = report
        
        return {"report_id": report_id, "report": report}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid HAR file format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/analyze-har")
async def analyze_har(file: UploadFile = File(...)):
    if not file.filename.endswith('.har'):
        raise HTTPException(status_code=400, detail="Please upload a HAR file")
    
    try:
        # Read and parse HAR file
        contents = await file.read()
        har_data = json.loads(contents.decode('utf-8'))
        
        # Get test cases from Excel
        test_cases = load_tests_from_xlsx()
        if not test_cases:
            raise HTTPException(status_code=400, detail="No test cases found in test_cases.xlsx. Please create test cases first.")
        
        # Analyze the HAR file
        calls = parse_har_for_calls(har_data, test_cases)
        url_failures, dimension_failures = analyze_failures(calls)
        
        # Create detailed results
        detailed_results = []
        for call in calls:
            for result, param_name, test_name in call.get("results", []):
                detailed_results.append(TestResult(
                    url=call["url"],
                    parameter=param_name,
                    result="Pass" if "Pass" in result else "Fail",
                    details=result,
                    test_case_name=test_name
                ))
        
        # Create analysis report
        total_tests = len(detailed_results)
        passed_tests = len([r for r in detailed_results if r.result == "Pass"])
        failed_tests = total_tests - passed_tests
        
        report = AnalysisReport(
            total_requests=len(calls),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            url_failures=url_failures,
            dimension_failures=dimension_failures,
            detailed_results=detailed_results,
            raw_data=calls
        )
        
        # Store results
        report_id = str(uuid.uuid4())
        analysis_results_store[report_id] = report
        
        return {"report_id": report_id, "report": report}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid HAR file format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    if report_id not in analysis_results_store:
        raise HTTPException(status_code=404, detail="Report not found")
    return analysis_results_store[report_id]

@app.get("/api/reports")
async def get_all_reports():
    return {"reports": list(analysis_results_store.keys())}

@app.post("/api/reports/{report_id}/export")
async def export_report(report_id: str):
    if report_id not in analysis_results_store:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = analysis_results_store[report_id]
    
    # Create Excel file
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Test Results"
    
    # Headers
    headers = ["URL", "Parameter", "Result", "Details", "Test Case"]
    for col, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col, value=header)
    
    # Data
    for row, result in enumerate(report.detailed_results, 2):
        sheet.cell(row=row, column=1, value=result.url)
        sheet.cell(row=row, column=2, value=result.parameter)
        sheet.cell(row=row, column=3, value=result.result)
        sheet.cell(row=row, column=4, value=result.details)
        sheet.cell(row=row, column=5, value=result.test_case_name)
    
    # Summary sheet
    summary_sheet = workbook.create_sheet("Summary")
    summary_data = [
        ["Metric", "Value"],
        ["Total Requests", report.total_requests],
        ["Total Tests", report.total_tests],
        ["Passed Tests", report.passed_tests],
        ["Failed Tests", report.failed_tests],
        ["", ""],
        ["URL Failures", "Count"]
    ]
    
    for url, count in report.url_failures.items():
        summary_data.append([url, count])
    
    summary_data.extend([["", ""], ["Parameter Failures", "Count"]])
    for param, count in report.dimension_failures.items():
        summary_data.append([param, count])
    
    for row, data in enumerate(summary_data, 1):
        for col, value in enumerate(data, 1):
            summary_sheet.cell(row=row, column=col, value=value)
    
    # Save to temp file
    temp_file = f"/tmp/harmony_report_{report_id}.xlsx"
    workbook.save(temp_file)
    
    return FileResponse(
        temp_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"harmony_report_{report_id}.xlsx"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)