import requests
import json
import sys
from datetime import datetime

class HarmonyAPITester:
    def __init__(self, base_url="https://demobackend.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_case_id = None
        self.report_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'} if not files else {}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Response: {response.json()}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        return success and response.get('status') == 'healthy'

    def test_get_empty_test_cases(self):
        """Test getting test cases when none exist"""
        success, response = self.run_test(
            "Get Empty Test Cases",
            "GET",
            "api/test-cases",
            200
        )
        return success and response.get('test_cases') == []

    def test_create_test_case(self):
        """Create a test case"""
        test_case_data = {
            "id": "",  # Backend will generate UUID if empty
            "name": "App Build Parameter Test",
            "description": "Check if app_build parameter exists in requests",
            "target_urls": ["example.com"],
            "parameter_name": "app_build",
            "condition": "exists",
            "expected_value": None,
            "optional": False,
            "on_pass_message": "Parameter app_build found with value: {value}",
            "on_fail_message": "Parameter app_build missing from {url}"
        }
        
        success, response = self.run_test(
            "Create Test Case",
            "POST",
            "api/test-cases",
            200,
            data=test_case_data
        )
        
        if success and 'id' in response:
            self.test_case_id = response['id']
            return True
        return False

    def test_get_test_cases(self):
        """Test getting test cases after creation"""
        success, response = self.run_test(
            "Get Test Cases",
            "GET",
            "api/test-cases",
            200
        )
        return success and len(response.get('test_cases', [])) > 0

    def test_update_test_case(self):
        """Update the created test case"""
        if not self.test_case_id:
            print("❌ No test case ID available for update")
            return False
            
        updated_data = {
            "id": self.test_case_id,
            "name": "Updated App Build Parameter Test",
            "description": "Updated description for app_build parameter check",
            "target_urls": ["example.com"],
            "parameter_name": "app_build",
            "condition": "equals",
            "expected_value": "1.0",
            "optional": False,
            "on_pass_message": "Parameter app_build has correct value: {value}",
            "on_fail_message": "Parameter app_build has incorrect value at {url}"
        }
        
        success, response = self.run_test(
            "Update Test Case",
            "PUT",
            f"api/test-cases/{self.test_case_id}",
            200,
            data=updated_data
        )
        return success

    def test_analyze_har_without_file(self):
        """Test HAR analysis without file (should fail)"""
        success, response = self.run_test(
            "Analyze HAR Without File",
            "POST",
            "api/analyze-har",
            422  # FastAPI validation error
        )
        return success

    def test_analyze_har_with_demo_file(self):
        """Test HAR analysis with demo file"""
        try:
            with open('/app/demo.har', 'rb') as f:
                files = {'file': ('demo.har', f, 'application/json')}
                success, response = self.run_test(
                    "Analyze Demo HAR File",
                    "POST",
                    "api/analyze-har",
                    200,
                    files=files
                )
                
                if success and 'report_id' in response:
                    self.report_id = response['report_id']
                    report = response.get('report', {})
                    print(f"   Analysis Results:")
                    print(f"   - Total Requests: {report.get('total_requests', 0)}")
                    print(f"   - Total Tests: {report.get('total_tests', 0)}")
                    print(f"   - Passed Tests: {report.get('passed_tests', 0)}")
                    print(f"   - Failed Tests: {report.get('failed_tests', 0)}")
                    return True
                return False
        except FileNotFoundError:
            print("❌ Demo HAR file not found at /app/demo.har")
            return False

    def test_get_report(self):
        """Test getting analysis report"""
        if not self.report_id:
            print("❌ No report ID available")
            return False
            
        success, response = self.run_test(
            "Get Analysis Report",
            "GET",
            f"api/reports/{self.report_id}",
            200
        )
        return success and 'total_requests' in response

    def test_get_all_reports(self):
        """Test getting all reports"""
        success, response = self.run_test(
            "Get All Reports",
            "GET",
            "api/reports",
            200
        )
        return success and 'reports' in response

    def test_export_report(self):
        """Test report export"""
        if not self.report_id:
            print("❌ No report ID available for export")
            return False
            
        success, response = self.run_test(
            "Export Report",
            "POST",
            f"api/reports/{self.report_id}/export",
            200
        )
        return success

    def test_delete_test_case(self):
        """Delete the created test case"""
        if not self.test_case_id:
            print("❌ No test case ID available for deletion")
            return False
            
        success, response = self.run_test(
            "Delete Test Case",
            "DELETE",
            f"api/test-cases/{self.test_case_id}",
            200
        )
        return success

    def test_get_nonexistent_report(self):
        """Test getting non-existent report (should fail)"""
        success, response = self.run_test(
            "Get Non-existent Report",
            "GET",
            "api/reports/nonexistent-id",
            404
        )
        return success

def main():
    print("🚀 Starting Harmony QA System API Tests")
    print("=" * 50)
    
    # Initialize tester
    tester = HarmonyAPITester("http://localhost:8001")
    
    # Run all tests in sequence
    tests = [
        tester.test_health_check,
        tester.test_get_empty_test_cases,
        tester.test_create_test_case,
        tester.test_get_test_cases,
        tester.test_update_test_case,
        tester.test_analyze_har_without_file,
        tester.test_analyze_har_with_demo_file,
        tester.test_get_report,
        tester.test_get_all_reports,
        tester.test_export_report,
        tester.test_get_nonexistent_report,
        tester.test_delete_test_case
    ]
    
    # Execute tests
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())