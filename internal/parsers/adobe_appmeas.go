package parsers

import (
	"net/url"
	"regexp"
	"strings"

	"github.com/jwiedeman/specwatch/internal/har"
)

func init() {
	Register(&AdobeAppMeasurement{})
}

// AdobeAppMeasurement parses Adobe Analytics /b/ss/ image request beacons.
type AdobeAppMeasurement struct{}

var bssPattern = regexp.MustCompile(`/b/ss/([^/]+)/`)
var evarPattern = regexp.MustCompile(`^v(\d+)$`)
var propPattern = regexp.MustCompile(`^c(\d+)$`)

func (a *AdobeAppMeasurement) Detect(ev har.NetworkEvent) bool {
	return strings.Contains(ev.URL, "/b/ss/")
}

func (a *AdobeAppMeasurement) Parse(ev har.NetworkEvent) Beacon {
	b := Beacon{
		Vendor:    "adobe_appmeasurement",
		RawURL:    ev.URL,
		EVars:     make(map[string]string),
		Props:     make(map[string]string),
		RawParams: make(map[string]string),
	}

	// Extract RSID from URL path: /b/ss/{rsid}/...
	if matches := bssPattern.FindStringSubmatch(ev.URL); len(matches) > 1 {
		b.RSID = matches[1]
	}

	// Merge all params: query string + post params
	params := mergeParams(ev)
	b.RawParams = params

	// Extract known fields
	b.PageName = params["pageName"]
	b.LinkType = params["pe"]
	b.LinkName = params["pev2"]

	// Page URL: prefer "g" param, fall back to "r" (referrer)
	if g, ok := params["g"]; ok && g != "" {
		b.PageURL = g
	} else if r, ok := params["r"]; ok && r != "" {
		b.PageURL = r
	}

	// Events list
	if events, ok := params["events"]; ok && events != "" {
		b.EventList = strings.Split(events, ",")
	}

	// eVars and Props
	for k, v := range params {
		if m := evarPattern.FindStringSubmatch(k); len(m) > 1 {
			b.EVars[m[1]] = v
		} else if m := propPattern.FindStringSubmatch(k); len(m) > 1 {
			b.Props[m[1]] = v
		}
	}

	// Platform detection from User-Agent
	if ua, ok := ev.Headers["User-Agent"]; ok {
		b.Platform = detectPlatform(ua)
	}

	return b
}

func mergeParams(ev har.NetworkEvent) map[string]string {
	params := make(map[string]string)

	// Start with query params from HAR
	for k, v := range ev.QueryParams {
		params[k] = v
	}

	// For POST requests, also parse the URL query string directly
	// and merge post params
	if ev.Method == "POST" {
		if parsed, err := url.Parse(ev.URL); err == nil {
			for k, v := range parsed.Query() {
				if _, exists := params[k]; !exists && len(v) > 0 {
					params[k] = v[0]
				}
			}
		}
		// Post body may be URL-encoded form data
		if ev.PostBody != "" {
			if vals, err := url.ParseQuery(ev.PostBody); err == nil {
				for k, v := range vals {
					if len(v) > 0 {
						params[k] = v[0]
					}
				}
			}
		}
		for k, v := range ev.PostParams {
			params[k] = v
		}
	}

	return params
}

func detectPlatform(ua string) string {
	ua = strings.ToLower(ua)
	switch {
	case strings.Contains(ua, "roku"):
		return "roku"
	case strings.Contains(ua, "firetv") || strings.Contains(ua, "fire tv"):
		return "firetv"
	case strings.Contains(ua, "tizen"):
		return "samsung_tv"
	case strings.Contains(ua, "vizio"):
		return "vizio"
	case strings.Contains(ua, "appletv") || strings.Contains(ua, "tvos"):
		return "tvos"
	case strings.Contains(ua, "android"):
		return "android"
	case strings.Contains(ua, "iphone") || strings.Contains(ua, "ipad"):
		return "ios"
	default:
		return "web"
	}
}
