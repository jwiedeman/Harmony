# page_type_test.py
test_case = {
    "name": "page_type_check",
    "description": "Check if 'page_type' parameter exists.",
    "target_urls": ["metrics", "smetrics", "a.fox.com", "b.fox.com"],  # Only apply to these URLs
    "parameter_checks": [
        {
            "name": "page_type",
            "condition": "exists",
            "on_pass": "Pass: 'page_type' parameter found with value {value}. URL: {url}.",
            "on_fail": "Fail: 'page_type' parameter missing. URL: {url}. Please add the 'page_type' parameter."
        }
    ]
}
