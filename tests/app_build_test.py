# app_build_test.py
test_case = {
    "name": "app_build_check",
    "description": "Check if 'app_build' parameter exists.",
    "target_urls": ["metrics", "smetrics", "a.fox.com", "b.fox.com"],  # Only apply to these URLs
    "parameter_checks": [
        {
            "name": "app_build",
            "condition": "exists",
            "on_pass": "Pass: 'app_build' parameter found with value {value}. URL: {url}.",
            "on_fail": "Fail: 'app_build' parameter missing. URL: {url}. Please add the 'app_build' parameter."
        }
    ]
}
