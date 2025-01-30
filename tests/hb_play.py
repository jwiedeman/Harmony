# event_type_dependent_test.py
test_case = {
    "name": "event_type_dependent_check",
    "description": "Conditional check for event type 'pause', 'play', or 'aa_start' with required dimensions.",
    "target_urls": ["metrics", "smetrics", "hb", "a.fox.com", "b.fox.com"],  # Only apply to these URLs
    "conditions": [
        {
            "name": "s:event:type",
            "value": ["play"],  # Check for any of these values
            "optional": False  # Condition is mandatory for this test
        }
    ],
    "parameter_checks": [
        {
            "name": "s:event:sid",
            "condition": "exists",
            "on_pass": "Pass: 's:event:sid' parameter found. URL: {url}.",
            "on_fail": "Fail: 's:event:sid' parameter missing. URL: {url}. Please add this parameter."
        },
        {
            "name": "l:event:duration",
            "condition": "exists",
            "on_pass": "Pass: 'l:event:duration' parameter found.",
            "on_fail": "Fail: 'l:event:duration' parameter missing. Please add this parameter."
        },
        {
            "name": "l:event:playhead",
            "condition": "exists",
            "on_pass": "Pass: 'l:event:playhead' parameter found.",
            "on_fail": "Fail: 'l:event:playhead' parameter missing. Please add this parameter."
        },
        {
            "name": "l:event:prev_ts",
            "condition": "exists",
            "on_pass": "Pass: 'l:event:prev_ts' parameter found.",
            "on_fail": "Fail: 'l:event:prev_ts' parameter missing. Please add this parameter."
        },
        {
            "name": "l:event:ts",
            "condition": "exists",
            "on_pass": "Pass: 'l:event:ts' parameter found.",
            "on_fail": "Fail: 'l:event:ts' parameter missing. Please add this parameter."
        },
        {
            "name": "s:asset:name",
            "condition": "exists",
            "on_pass": "Pass: 's:asset:name' parameter found.",
            "on_fail": "Fail: 's:asset:name' parameter missing. Please add this parameter."
        },
        {
            "name": "l:asset:length",
            "condition": "exists",
            "on_pass": "Pass: 'l:asset:length' parameter found.",
            "on_fail": "Fail: 'l:asset:length' parameter missing. Please add this parameter."
        },
        {
            "name": "s:asset:publisher",
            "condition": "exists",
            "on_pass": "Pass: 's:asset:publisher' parameter found.",
            "on_fail": "Fail: 's:asset:publisher' parameter missing. Please add this parameter."
        },
        {
            "name": "s:asset:type",
            "condition": "exists",
            "on_pass": "Pass: 's:asset:type' parameter found.",
            "on_fail": "Fail: 's:asset:type' parameter missing. Please add this parameter."
        }
    ]
}
