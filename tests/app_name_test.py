# app_name_test.py
test_case = {
    "name": "app_name_check",
    "description": "Check if 'app_name' parameter exists.",
    "target_urls": ["metrics", "smetrics", "a.fox.com", "b.fox.com"],  # Only apply to these URLs
    "parameter_checks": [
        {
            "name": "app_name",
            "condition": "exists",
            "on_pass": "Pass: 'app_name' parameter found with value {value}. URL: {url}.",
            "on_fail": "Fail: 'app_name' parameter missing. URL: {url}. Please add the 'app_name' parameter."
        }
    ]
}
