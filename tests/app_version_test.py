# app_version_test.py
test_case = {
    "name": "app_version_check",
    "description": "Check if 'app_version' parameter exists.",
    "target_urls": ["metrics", "smetrics", "a.fox.com", "b.fox.com"],  # Only apply to these URLs
    "parameter_checks": [
        {
            "name": "app_version",
            "condition": "exists",
            "on_pass": "Pass: 'app_version' parameter found with value {value}. URL: {url}.",
            "on_fail": "Fail: 'app_version' parameter missing. URL: {url}. Please add the 'app_version' parameter."
        }
    ]
}
