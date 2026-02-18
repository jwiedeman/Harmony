package spec

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadSpec(t *testing.T) {
	specDir := filepath.Join("..", "..", "testdata", "specs")
	if _, err := os.Stat(specDir); os.IsNotExist(err) {
		t.Skip("testdata/specs not found")
	}

	s, err := LoadSpec(specDir)
	if err != nil {
		t.Fatalf("LoadSpec() error: %v", err)
	}

	// Check enums
	if len(s.Enums) == 0 {
		t.Error("expected enums to be loaded")
	}
	pt, ok := s.Enums["page_types"]
	if !ok {
		t.Fatal("expected page_types enum")
	}
	if !pt.Contains("article") {
		t.Error("expected page_types to contain 'article'")
	}
	if pt.Contains("nonexistent") {
		t.Error("page_types should not contain 'nonexistent'")
	}

	// Check events
	if len(s.Events) == 0 {
		t.Error("expected events to be loaded")
	}
	pv, ok := s.Events["page_view"]
	if !ok {
		t.Fatal("expected page_view event")
	}
	if len(pv.Required) < 2 {
		t.Errorf("expected at least 2 required dimensions, got %d", len(pv.Required))
	}
	if len(pv.Optional) < 1 {
		t.Errorf("expected at least 1 optional dimension, got %d", len(pv.Optional))
	}

	// Check platform overrides
	ov, ok := pv.Overrides["adobe_appmeasurement"]
	if !ok {
		t.Fatal("expected adobe_appmeasurement override")
	}
	if ov.RequiredEvent != "event1" {
		t.Errorf("expected RequiredEvent=event1, got %q", ov.RequiredEvent)
	}

	// Check mappings
	if len(s.Mappings) == 0 {
		t.Error("expected mappings to be loaded")
	}
	m, ok := s.Mappings["test_site"]
	if !ok {
		t.Fatal("expected test_site mapping")
	}
	if m.ProdRSID != "testsiteglobal" {
		t.Errorf("expected ProdRSID=testsiteglobal, got %q", m.ProdRSID)
	}
	if m.DevRSID != "testsitedev" {
		t.Errorf("expected DevRSID=testsitedev, got %q", m.DevRSID)
	}
	if dm, ok := m.DimMap["page_url"]; !ok || dm.EVar != "v75" {
		t.Errorf("expected page_url -> v75 mapping, got %+v", dm)
	}
	if ev, ok := m.EventMap["page_view"]; !ok || ev != "event1" {
		t.Errorf("expected page_view -> event1, got %q", ev)
	}
}

func TestLoadSpec_NonexistentDir(t *testing.T) {
	// Should return an empty spec, not error (directories are optional)
	s, err := LoadSpec("/nonexistent/dir")
	if err != nil {
		t.Fatalf("LoadSpec() should not error for missing dir: %v", err)
	}
	if len(s.Events) != 0 {
		t.Error("expected no events for missing dir")
	}
}

func TestParseEnumsFile(t *testing.T) {
	path := filepath.Join("..", "..", "testdata", "specs", "_global", "enums.md")
	if _, err := os.Stat(path); os.IsNotExist(err) {
		t.Skip("testdata enums.md not found")
	}

	enums, err := parseEnumsFile(path)
	if err != nil {
		t.Fatalf("parseEnumsFile() error: %v", err)
	}

	if len(enums) != 2 {
		t.Errorf("expected 2 enum sets, got %d", len(enums))
	}

	pt := enums["page_types"]
	if pt == nil {
		t.Fatal("expected page_types")
	}
	if !pt.Contains("homepage") {
		t.Error("expected homepage in page_types")
	}
	if len(pt.Values) != 3 {
		t.Errorf("expected 3 page_types values, got %d", len(pt.Values))
	}
}

func TestParseTableHelpers(t *testing.T) {
	if !isTableRow("| a | b | c |") {
		t.Error("should detect table row")
	}
	if isTableRow("not a table") {
		t.Error("should not detect non-table")
	}
	if !isTableSeparator("|---|---|---|") {
		t.Error("should detect separator")
	}
	if isTableSeparator("| a | b |") {
		t.Error("should not detect content row as separator")
	}

	cells := parseTableCells("| foo | bar | baz |")
	if len(cells) != 3 || cells[0] != "foo" || cells[1] != "bar" || cells[2] != "baz" {
		t.Errorf("unexpected cells: %v", cells)
	}
}

func TestExtractBacktickValue(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{"`eVar75`", "eVar75"},
		{"`eVar75` (fox_news) | `eVar12` (fox_corp)", "eVar75"},
		{"no backticks", ""},
		{"`unterminated", ""},
	}

	for _, tt := range tests {
		got := extractBacktickValue(tt.input)
		if got != tt.expected {
			t.Errorf("extractBacktickValue(%q) = %q, want %q", tt.input, got, tt.expected)
		}
	}
}
