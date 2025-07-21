function readFileAsArrayBuffer(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(reader.error);
        reader.readAsArrayBuffer(file);
    });
}

async function parseTestCases(file) {
    const data = await readFileAsArrayBuffer(file);
    const workbook = XLSX.read(data, { type: 'array' });
    const sheet = workbook.Sheets[workbook.SheetNames[0]];
    const rows = XLSX.utils.sheet_to_json(sheet, { defval: '' });
    return rows.map(row => ({
        name: row['Test Name'] || '',
        description: row['Description'] || '',
        target_urls: row['Target URLs'] ? row['Target URLs'].split(',').map(u => u.trim()).filter(Boolean) : [],
        parameter_name: row['Parameter Name'] || '',
        condition: String(row['Condition'] || 'exists').toLowerCase(),
        expected_value: row['Expected Value'] ? String(row['Expected Value']) : null,
        optional: String(row['Optional']).toLowerCase() === 'true',
        on_pass_message: row['On Pass Message'] || `Parameter ${row['Parameter Name']} found with value: {value}`,
        on_fail_message: row['On Fail Message'] || `Parameter ${row['Parameter Name']} missing from {url}`,
    }));
}

async function parseHar(file) {
    const data = await readFileAsArrayBuffer(file);
    const text = new TextDecoder().decode(data);
    return JSON.parse(text);
}

function extractParameters(url, postDataParams) {
    const urlObj = new URL(url);
    const params = {};
    for (const [k, v] of urlObj.searchParams.entries()) {
        params[k] = v;
    }
    return Object.assign(params, postDataParams);
}

function applyTestCases(call, testCases) {
    const results = [];
    const urlDomain = new URL(call.url).hostname;
    for (const tc of testCases) {
        if (tc.target_urls.length > 0 && !tc.target_urls.some(t => call.url.includes(t) || urlDomain.includes(t))) {
            continue;
        }
        const paramValue = call.parameters[tc.parameter_name];
        if (tc.condition === 'exists') {
            if (paramValue !== undefined) {
                const msg = tc.on_pass_message.replace('{value}', paramValue).replace('{url}', call.url);
                results.push({ result: 'Pass', details: msg, parameter: tc.parameter_name, test: tc.name });
            } else if (!tc.optional) {
                const msg = tc.on_fail_message.replace('{url}', call.url);
                results.push({ result: 'Fail', details: msg, parameter: tc.parameter_name, test: tc.name });
            }
        } else if (tc.condition === 'equals') {
            if (paramValue !== undefined) {
                if (String(paramValue) === String(tc.expected_value)) {
                    const msg = tc.on_pass_message.replace('{value}', paramValue).replace('{url}', call.url);
                    results.push({ result: 'Pass', details: msg, parameter: tc.parameter_name, test: tc.name });
                } else {
                    const msg = tc.on_fail_message.replace('{url}', call.url);
                    results.push({ result: 'Fail', details: `Expected '${tc.expected_value}' but got '${paramValue}'`, parameter: tc.parameter_name, test: tc.name });
                }
            } else if (!tc.optional) {
                const msg = tc.on_fail_message.replace('{url}', call.url);
                results.push({ result: 'Fail', details: msg, parameter: tc.parameter_name, test: tc.name });
            }
        }
    }
    return results;
}

function analyzeHar(harData, testCases) {
    const entries = harData.log.entries;
    const calls = [];
    for (const entry of entries) {
        const url = entry.request.url;
        const method = entry.request.method;
        const postData = entry.request.postData || {};
        let postParams = {};
        if (postData.params) {
            for (const p of postData.params) {
                postParams[p.name] = p.value;
            }
        } else if (postData.text) {
            try {
                const json = JSON.parse(postData.text);
                if (typeof json === 'object') postParams = json;
            } catch {}
        }
        const parameters = extractParameters(url, postParams);
        const call = { url, method, parameters, payload: postData.text || 'No payload', status: entry.response.status };
        call.results = applyTestCases(call, testCases);
        calls.push(call);
    }
    return calls;
}

function summarize(calls) {
    const urlFailures = {};
    const parameterFailures = {};
    const detailedResults = [];
    for (const call of calls) {
        for (const r of call.results) {
            detailedResults.push({ url: call.url, parameter: r.parameter, result: r.result, details: r.details, test_case_name: r.test });
            if (r.result === 'Fail') {
                urlFailures[call.url] = (urlFailures[call.url] || 0) + 1;
                parameterFailures[r.parameter] = (parameterFailures[r.parameter] || 0) + 1;
            }
        }
    }
    const totalTests = detailedResults.length;
    const passed = detailedResults.filter(r => r.result === 'Pass').length;
    return {
        total_requests: calls.length,
        total_tests: totalTests,
        passed_tests: passed,
        failed_tests: totalTests - passed,
        url_failures: urlFailures,
        dimension_failures: parameterFailures,
        detailed_results: detailedResults,
        raw_data: calls,
    };
}

function displayReport(report) {
    const container = document.getElementById('results');
    container.innerHTML = '';
    const summary = document.createElement('div');
    summary.innerHTML = `<h3>Summary</h3>
    <p>Total Requests: <strong>${report.total_requests}</strong></p>
    <p>Total Tests: <strong>${report.total_tests}</strong></p>
    <p>Passed Tests: <strong style="color:green">${report.passed_tests}</strong></p>
    <p>Failed Tests: <strong style="color:red">${report.failed_tests}</strong></p>`;
    container.appendChild(summary);

    const details = document.createElement('details');
    details.open = true;
    details.innerHTML = '<summary>Detailed Results</summary>';
    const table = document.createElement('table');
    table.border = '1';
    const header = document.createElement('tr');
    ['Status','URL','Parameter','Test Case','Details'].forEach(h => { const th = document.createElement('th'); th.textContent = h; header.appendChild(th); });
    table.appendChild(header);
    for (const r of report.detailed_results) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${r.result}</td><td>${r.url}</td><td>${r.parameter}</td><td>${r.test_case_name}</td><td>${r.details}</td>`;
        table.appendChild(tr);
    }
    details.appendChild(table);
    container.appendChild(details);

    const exportBtn = document.createElement('button');
    exportBtn.textContent = 'Export Excel';
    exportBtn.onclick = () => exportReport(report);
    container.appendChild(exportBtn);
}

function exportReport(report) {
    const wb = XLSX.utils.book_new();
    const wsData = [ ['URL','Parameter','Result','Details','Test Case'] ];
    report.detailed_results.forEach(r => {
        wsData.push([r.url, r.parameter, r.result, r.details, r.test_case_name]);
    });
    const ws = XLSX.utils.aoa_to_sheet(wsData);
    XLSX.utils.book_append_sheet(wb, ws, 'Results');

    const summaryData = [ ['Metric','Value'],
        ['Total Requests', report.total_requests],
        ['Total Tests', report.total_tests],
        ['Passed Tests', report.passed_tests],
        ['Failed Tests', report.failed_tests],
        [],['URL Failures','Count'] ];
    for (const [url,c] of Object.entries(report.url_failures)) {
        summaryData.push([url, c]);
    }
    summaryData.push([],['Parameter Failures','Count']);
    for (const [p,c] of Object.entries(report.dimension_failures)) {
        summaryData.push([p, c]);
    }
    const wsSummary = XLSX.utils.aoa_to_sheet(summaryData);
    XLSX.utils.book_append_sheet(wb, wsSummary, 'Summary');

    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([wbout], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `harmony_report_${Date.now()}.xlsx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

document.getElementById('analyzeBtn').addEventListener('click', async () => {
    const tcFile = document.getElementById('testCasesInput').files[0];
    const harFile = document.getElementById('harInput').files[0];
    if (!tcFile || !harFile) {
        alert('Please select both test_cases.xlsx and a HAR file.');
        return;
    }
    try {
        const testCases = await parseTestCases(tcFile);
        const harData = await parseHar(harFile);
        const calls = analyzeHar(harData, testCases);
        const report = summarize(calls);
        displayReport(report);
    } catch (err) {
        alert('Error: ' + err.message);
        console.error(err);
    }
});
