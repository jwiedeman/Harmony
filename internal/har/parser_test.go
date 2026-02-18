package har

import (
	"os"
	"path/filepath"
	"testing"
)

func TestParseFile(t *testing.T) {
	// Use the comprehensive demo HAR
	path := filepath.Join("..", "..", "testdata", "comprehensive-demo.har")
	if _, err := os.Stat(path); os.IsNotExist(err) {
		t.Skip("testdata/comprehensive-demo.har not found")
	}

	events, err := ParseFile(path)
	if err != nil {
		t.Fatalf("ParseFile() error: %v", err)
	}

	if len(events) != 5 {
		t.Errorf("expected 5 events, got %d", len(events))
	}

	// First entry should have query params parsed from URL
	ev := events[0]
	if ev.URL != "https://example.com/api/data?app_build=1.0&user_id=123" {
		t.Errorf("unexpected URL: %s", ev.URL)
	}
	if ev.QueryParams["app_build"] != "1.0" {
		t.Errorf("expected app_build=1.0, got %q", ev.QueryParams["app_build"])
	}
	if ev.Method != "GET" {
		t.Errorf("expected GET, got %s", ev.Method)
	}
}

func TestParseFile_Adobe(t *testing.T) {
	path := filepath.Join("..", "..", "testdata", "adobe_test.har")
	if _, err := os.Stat(path); os.IsNotExist(err) {
		t.Skip("testdata/adobe_test.har not found")
	}

	events, err := ParseFile(path)
	if err != nil {
		t.Fatalf("ParseFile() error: %v", err)
	}

	if len(events) != 6 {
		t.Errorf("expected 6 events, got %d", len(events))
	}

	// First event should be an Adobe beacon
	ev := events[0]
	if ev.QueryParams["v75"] != "https://foxnews.com/politics/article-123" {
		t.Errorf("unexpected v75: %q", ev.QueryParams["v75"])
	}
}

func TestEntryToEvent_FallbackQueryParse(t *testing.T) {
	// Test that query params are parsed from URL when queryString is empty
	entry := Entry{
		Request: Request{
			Method:      "GET",
			URL:         "https://example.com/test?foo=bar&baz=qux",
			QueryString: nil,
		},
	}

	ev := entryToEvent(entry)
	if ev.QueryParams["foo"] != "bar" {
		t.Errorf("expected foo=bar, got %q", ev.QueryParams["foo"])
	}
	if ev.QueryParams["baz"] != "qux" {
		t.Errorf("expected baz=qux, got %q", ev.QueryParams["baz"])
	}
}

func TestParseFile_NotFound(t *testing.T) {
	_, err := ParseFile("/nonexistent/file.har")
	if err == nil {
		t.Error("expected error for nonexistent file")
	}
}

func TestParseFile_InvalidJSON(t *testing.T) {
	// Create a temp file with invalid JSON
	tmp := filepath.Join(t.TempDir(), "bad.har")
	os.WriteFile(tmp, []byte("not json"), 0644)

	_, err := ParseFile(tmp)
	if err == nil {
		t.Error("expected error for invalid JSON")
	}
}
