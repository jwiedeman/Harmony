package validator

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/jwiedeman/specwatch/internal/spec"

	// Register parsers
	_ "github.com/jwiedeman/specwatch/internal/parsers"
)

func loadTestSpec(t *testing.T) *spec.Spec {
	t.Helper()
	specDir := filepath.Join("..", "..", "testdata", "specs")
	s, err := spec.LoadSpec(specDir)
	if err != nil {
		t.Fatalf("LoadSpec() error: %v", err)
	}
	return s
}

func TestValidateHAR_AdobeBeacons(t *testing.T) {
	harPath := filepath.Join("..", "..", "testdata", "adobe_test.har")
	if _, err := os.Stat(harPath); os.IsNotExist(err) {
		t.Skip("testdata/adobe_test.har not found")
	}

	s := loadTestSpec(t)
	mapping := s.Mappings["test_site"]
	if mapping == nil {
		t.Fatal("test_site mapping not found")
	}

	engine := NewEngine(s, mapping)
	report, err := engine.ValidateHAR(harPath)
	if err != nil {
		t.Fatalf("ValidateHAR() error: %v", err)
	}

	// Should have detected Adobe beacons (5 Adobe + 1 GA4 unmatched by parsers)
	if report.TotalCalls < 1 {
		t.Errorf("expected at least 1 beacon, got %d", report.TotalCalls)
	}

	// Should have some matched and some that pass
	if report.Matched == 0 {
		t.Error("expected at least 1 matched beacon")
	}

	t.Logf("Total: %d, Matched: %d, Unmatched: %d, Passed: %d, Failed: %d",
		report.TotalCalls, report.Matched, report.Unmatched, report.Passed, report.Failed)
}

func TestValidateHAR_NoMapping(t *testing.T) {
	harPath := filepath.Join("..", "..", "testdata", "adobe_test.har")
	if _, err := os.Stat(harPath); os.IsNotExist(err) {
		t.Skip("testdata/adobe_test.har not found")
	}

	s := loadTestSpec(t)
	engine := NewEngine(s, nil)
	report, err := engine.ValidateHAR(harPath)
	if err != nil {
		t.Fatalf("ValidateHAR() error: %v", err)
	}

	// Without a mapping, beacons can't match event specs
	if report.Matched != 0 {
		t.Errorf("expected 0 matched without mapping, got %d", report.Matched)
	}
}

func TestValidateHAR_BadFile(t *testing.T) {
	s := loadTestSpec(t)
	engine := NewEngine(s, nil)
	_, err := engine.ValidateHAR("/nonexistent/file.har")
	if err == nil {
		t.Error("expected error for nonexistent file")
	}
}
