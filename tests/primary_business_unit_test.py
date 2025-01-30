# primary_business_unit_test.py
test_case = {
    "name": "primary_business_unit_check",
    "description": "Check if 'primary_business_unit' parameter exists.",
    "target_urls": ["metrics", "smetrics", "a.fox.com", "b.fox.com"],  # Only apply to these URLs
    "parameter_checks": [
        {
            "name": "primary_business_unit",
            "condition": "exists",
            "on_pass": "Pass: 'primary_business_unit' parameter found with value {value}. URL: {url}.",
            "on_fail": "Fail: 'primary_business_unit' parameter missing. URL: {url}. Please add the 'primary_business_unit' parameter."
        }
    ]
}
