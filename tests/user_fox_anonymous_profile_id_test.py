# user_fox_anonymous_profile_id_test.py
test_case = {
    "name": "user_fox_anonymous_profile_id_check",
    "description": "Check if 'user_fox_anonymous_profile_id' parameter exists.",
    "target_urls": ["metrics", "smetrics", "a.fox.com", "b.fox.com"],  # Only apply to these URLs
    "parameter_checks": [
        {
            "name": "user_fox_anonymous_profile_id",
            "condition": "exists",
            "on_pass": "Pass: 'user_fox_anonymous_profile_id' parameter found with value {value}.",
            "on_fail": "Fail: 'user_fox_anonymous_profile_id' parameter missing. Please add the 'user_fox_anonymous_profile_id' parameter."
        }
    ]
}
