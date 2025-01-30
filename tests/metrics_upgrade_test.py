# metrics_upgrade_test.py
test_case = {
    "name": "metrics_upgrade",
    "description": "Flag if the URL contains 'metrics' instead of 'smetrics' and suggest an upgrade.",
    "target_urls": ["metrics.foxnews.com"],  # Apply only to metrics URLs, not smetrics
    "actions": [
        {
            "type": "flag",
            "message": "Consider upgrading to 'smetrics' for report suite tracking. URL: {url}."
        }
    ]
}
