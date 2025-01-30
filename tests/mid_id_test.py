# mid_parameter_test.py
test_case = {
    "name": "mid_presence_check",
    "description": "Check if 'mid' parameter (or its variations) exists in Adobe call parameters.",
    "target_urls": ["metrics", "smetrics", "a.fox.com", "b.fox.com"],  # Only apply to these URLs
    "parameter_checks": [
        {
            "names": ["mid", "s:user:mid"],  # Multiple parameter names that can satisfy this check
            "condition": "exists",
            "on_pass": "Pass: One of 'mid' variations found with value {value}. URL: {url}.",
            "on_fail": "Fail: No 'mid' parameter variations found. URL: {url}. Please add the 'mid' parameter."
        }
    ]
}
