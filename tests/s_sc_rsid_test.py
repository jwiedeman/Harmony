# s_sc_rsid_test.py
test_case = {
    "name": "s_sc_rsid_check",
    "description": "Check if 's:sc:rsid' parameter exists and matches 'foxnewsglobalproduction'.",
    "target_urls": ["hb.omtrdc"],  # Apply this test to these URLs
    "parameter_checks": [
        {
            "names": ["s:sc:rsid"],  # The parameter name to check
            "condition": "exists",
            "on_pass": "Pass: 's:sc:rsid' parameter found with value '{value}'. URL: {url}.",
            "on_fail": "Fail: 's:sc:rsid' parameter missing. URL: {url}. Please add the 's:sc:rsid' parameter."
        },
        {
            "names": ["s:sc:rsid"],
            "condition": "equals",
            "value": "foxnewsglobalproductionn",
            "on_pass": "Pass: 's:sc:rsid' parameter matches expected value 'foxnewsglobalproduction'.",
            "on_fail": "Fail: 's:sc:rsid' parameter does not match the expected value 'foxnewsglobalproduction'."
        }
    ]
}
