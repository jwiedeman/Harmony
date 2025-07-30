# Harmony QA System - User Guide

## Overview
The Harmony QA System is a comprehensive web-based tool for analyzing HTTP Archive (HAR) files against predefined test cases. It helps QA teams identify API parameter issues, validate data integrity, and generate detailed reports.

## Features

### 🔧 Test Case Management
- **Visual Test Builder**: Create test cases using an intuitive web interface
- **Rule Types**: 
  - `EXISTS`: Check if a parameter is present
  - `EQUALS`: Validate parameter has specific value
- **URL Targeting**: Apply tests to specific domains or all requests
- **Optional Parameters**: Mark parameters as optional to avoid false failures
- **Custom Messages**: Define success/failure messages with placeholders
- **Composite Test Groups**: Chain multiple tests together to validate complex sequences

### 📁 HAR File Analysis
- **Drag & Drop Upload**: Easy file upload interface
- **Multi-format Support**: Handles standard HAR files from all major browsers
- **Real-time Processing**: Instant analysis with progress feedback
- **Batch Processing**: Analyze multiple requests simultaneously

### 📊 Results Dashboard
- **Summary Overview**: Quick metrics and failure counts
- **Detailed Results**: Filterable table of all test results
- **Raw Data View**: Complete request/response inspection
- **Export Reports**: Download results as Excel files

## Quick Start Guide

### 1. Create Test Cases
Navigate to the **TEST CASES** tab:
1. Click **NEW TEST CASE**
2. Fill in the test details:
   - **Name**: Descriptive test identifier
   - **Description**: What the test validates
   - **Target URLs**: Comma-separated domains (leave empty for all)
   - **Parameter Name**: The parameter to check
   - **Condition**: EXISTS or EQUALS
   - **Expected Value**: Required for EQUALS condition
   - **Optional**: Check if parameter is not required
   - **Messages**: Custom success/failure messages
3. Click **CREATE** to save

### 2. Upload HAR Files
Navigate to the **HAR ANALYZER** tab:
1. Drag and drop your HAR file or click to select
2. File will be validated and preview information shown
3. Click **START ANALYSIS** to process
4. Results will automatically appear in the Results Dashboard

### 3. Review Results
Navigate to the **RESULTS** tab:
- **Summary**: Overview of requests, tests, passes, and failures
- **Detailed Results**: Filter and sort individual test results
- **Raw Data**: Inspect complete request/response data
- **Export**: Download comprehensive Excel reports

## Example Test Cases

### Basic Parameter Existence
```
Name: App Build Check
Description: Verify app_build parameter exists
Parameter: app_build
Condition: EXISTS
Target URLs: example.com
```

### Specific Value Validation
```
Name: API Version Validation
Description: Ensure API version is v2.0
Parameter: version
Condition: EQUALS
Expected Value: v2.0
Target URLs: api.example.com
```

### Optional Parameter
```
Name: Tracking ID Check
Description: Check for optional tracking
Parameter: tracking_id
Condition: EXISTS
Optional: YES
Target URLs: analytics.example.com
```

### Composite Test Group
Create `test_groups.json` in the project root to define sequences of existing test cases. Groups can also be managed via the `/api/test-groups` endpoints and through the Test Groups screen in the web UI.
Example:
```json
[
  {
    "name": "Basic Sequence",
    "sequence": ["App Build Parameter Check", "API Version Validation", "User Agent Detection"]
  }
]
```

## HAR File Collection

### Chrome Browser
1. Open Developer Tools (F12)
2. Go to **Network** tab
3. Perform actions on your website
4. Right-click in Network tab → **Save all as HAR with content**

### Firefox Browser
1. Open Developer Tools (F12)
2. Go to **Network** tab
3. Perform actions on your website
4. Click gear icon → **Save All As HAR**

### Safari Browser
1. Enable Develop menu in Safari preferences
2. Open Web Inspector
3. Go to **Network** tab
4. Export as HAR file

## Understanding Results

### Test Results
- **PASS**: Parameter found and meets conditions
- **FAIL**: Parameter missing or doesn't match expected value

### Failure Analysis
- **URL Failures**: Which URLs have the most issues
- **Parameter Failures**: Which parameters fail most often
- **Detailed Results**: Individual test outcomes with context

### Report Export
Generated Excel files contain:
- **Test Results Sheet**: All individual test outcomes
- **Summary Sheet**: Aggregate metrics and failure counts
- **Timestamps**: When analysis was performed
- **File Information**: Original HAR file details

## Best Practices

### Test Case Design
1. **Start Simple**: Begin with basic EXISTS tests
2. **Be Specific**: Use targeted URL patterns when possible
3. **Clear Messages**: Write descriptive success/failure messages
4. **Logical Grouping**: Organize related tests together

### HAR Collection
1. **Clear Browser Cache**: Start with clean state
2. **Complete Workflows**: Capture full user journeys
3. **Multiple Scenarios**: Test different user paths
4. **Regular Updates**: Keep test data current

### Analysis Workflow
1. **Baseline First**: Establish expected behavior
2. **Iterative Testing**: Run tests frequently
3. **Fix and Retest**: Address issues systematically
4. **Documentation**: Keep test cases updated

## Technical Specifications

### Supported Formats
- **Input**: HAR files (HTTP Archive format)
- **Output**: Excel (.xlsx) reports
- **Browsers**: Chrome, Firefox, Safari, Edge

### System Requirements
- **Modern Web Browser**: Chrome 80+, Firefox 75+, Safari 13+
- **JavaScript Enabled**: Required for full functionality
- **File Size**: HAR files up to 100MB supported

### API Integration
The system provides REST APIs for:
- Test case management (CRUD operations)
- HAR file analysis
- Report generation and export
- Programmatic access to all features

## Troubleshooting

### Common Issues
1. **HAR Upload Fails**: Check file is valid HAR format
2. **No Results**: Ensure test cases match your URLs
3. **Export Issues**: Verify browser allows downloads

### Support
For technical support or feature requests, refer to the system documentation or contact your QA team lead.

---

**Harmony QA System v1.0** - Professional HTTP Archive Analysis Tool