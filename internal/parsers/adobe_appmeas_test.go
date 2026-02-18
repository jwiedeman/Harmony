package parsers

import (
	"testing"

	"github.com/jwiedeman/specwatch/internal/har"
)

func TestAdobeAppMeasurement_Detect(t *testing.T) {
	p := &AdobeAppMeasurement{}

	tests := []struct {
		url    string
		expect bool
	}{
		{"https://foxnews.112.2o7.net/b/ss/foxnewsglobal/1/JS-2.22.0/s1234?pageName=test", true},
		{"https://example.com/b/ss/rsid/1/?events=event1", true},
		{"https://www.google-analytics.com/g/collect?v=2", false},
		{"https://example.com/page", false},
	}

	for _, tt := range tests {
		ev := har.NetworkEvent{URL: tt.url}
		if got := p.Detect(ev); got != tt.expect {
			t.Errorf("Detect(%q) = %v, want %v", tt.url, got, tt.expect)
		}
	}
}

func TestAdobeAppMeasurement_Parse(t *testing.T) {
	p := &AdobeAppMeasurement{}
	ev := har.NetworkEvent{
		Method: "GET",
		URL:    "https://foxnews.112.2o7.net/b/ss/foxnewsglobal/1/JS-2.22.0/s1234",
		Headers: map[string]string{
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
		},
		QueryParams: map[string]string{
			"pageName": "politics:article-123",
			"g":        "https://foxnews.com/politics/article-123",
			"v75":      "https://foxnews.com/politics/article-123",
			"v3":       "article",
			"v18":      "article-123",
			"v4":       "politics",
			"c75":      "https://foxnews.com/politics/article-123",
			"c4":       "politics",
			"events":   "event1",
			"pe":       "",
			"pev2":     "",
		},
		PostBody:   "",
		PostParams: map[string]string{},
	}

	b := p.Parse(ev)

	if b.Vendor != "adobe_appmeasurement" {
		t.Errorf("Vendor = %q, want adobe_appmeasurement", b.Vendor)
	}
	if b.RSID != "foxnewsglobal" {
		t.Errorf("RSID = %q, want foxnewsglobal", b.RSID)
	}
	if b.PageName != "politics:article-123" {
		t.Errorf("PageName = %q, want politics:article-123", b.PageName)
	}
	if b.PageURL != "https://foxnews.com/politics/article-123" {
		t.Errorf("PageURL = %q, want url", b.PageURL)
	}
	if b.EVars["75"] != "https://foxnews.com/politics/article-123" {
		t.Errorf("EVars[75] = %q", b.EVars["75"])
	}
	if b.EVars["3"] != "article" {
		t.Errorf("EVars[3] = %q, want article", b.EVars["3"])
	}
	if b.Props["75"] != "https://foxnews.com/politics/article-123" {
		t.Errorf("Props[75] = %q", b.Props["75"])
	}
	if len(b.EventList) != 1 || b.EventList[0] != "event1" {
		t.Errorf("EventList = %v, want [event1]", b.EventList)
	}
	if b.Platform != "web" {
		t.Errorf("Platform = %q, want web", b.Platform)
	}
}

func TestAdobeAppMeasurement_Parse_MultipleEvents(t *testing.T) {
	p := &AdobeAppMeasurement{}
	ev := har.NetworkEvent{
		Method: "GET",
		URL:    "https://example.com/b/ss/testrsid/1/JS-2.0/s1",
		QueryParams: map[string]string{
			"events": "event1,event50,event52",
		},
		Headers:    map[string]string{},
		PostParams: map[string]string{},
	}

	b := p.Parse(ev)
	if len(b.EventList) != 3 {
		t.Errorf("expected 3 events, got %d: %v", len(b.EventList), b.EventList)
	}
}

func TestParseAll(t *testing.T) {
	events := []har.NetworkEvent{
		{
			URL:         "https://example.com/b/ss/rsid/1/?events=event1&pageName=test",
			Method:      "GET",
			QueryParams: map[string]string{"events": "event1", "pageName": "test"},
			Headers:     map[string]string{},
			PostParams:  map[string]string{},
		},
		{
			URL:         "https://www.google-analytics.com/g/collect?v=2",
			Method:      "GET",
			QueryParams: map[string]string{"v": "2"},
			Headers:     map[string]string{},
			PostParams:  map[string]string{},
		},
		{
			URL:         "https://example.com/page",
			Method:      "GET",
			QueryParams: map[string]string{},
			Headers:     map[string]string{},
			PostParams:  map[string]string{},
		},
	}

	beacons := ParseAll(events)
	if len(beacons) != 1 {
		t.Errorf("expected 1 beacon (Adobe only), got %d", len(beacons))
	}
	if len(beacons) > 0 && beacons[0].Vendor != "adobe_appmeasurement" {
		t.Errorf("expected adobe_appmeasurement, got %q", beacons[0].Vendor)
	}
}

func TestDetectPlatform(t *testing.T) {
	tests := []struct {
		ua       string
		expected string
	}{
		{"Mozilla/5.0 (Linux; Android 12; Roku Ultra)", "roku"},
		{"Mozilla/5.0 (Linux; Android 9; AFTMM Fire TV)", "firetv"},
		{"Mozilla/5.0 (SMART-TV; Tizen 5.5)", "samsung_tv"},
		{"VizioTV/1.0", "vizio"},
		{"AppleTV/tvOS 15.0", "tvos"},
		{"Mozilla/5.0 (Linux; Android 12; Pixel 6)", "android"},
		{"Mozilla/5.0 (iPhone; CPU iPhone OS 15_0)", "ios"},
		{"Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "web"},
	}

	for _, tt := range tests {
		if got := detectPlatform(tt.ua); got != tt.expected {
			t.Errorf("detectPlatform(%q) = %q, want %q", tt.ua, got, tt.expected)
		}
	}
}
