package validator

import (
	"testing"

	"github.com/jwiedeman/specwatch/internal/spec"
)

func TestValidateDimension_Required_Missing(t *testing.T) {
	dim := spec.Dimension{Name: "page_url", Required: true, Validation: `^https?://`}
	result := ValidateDimension(dim, "", nil)
	if result.Status != Fail {
		t.Errorf("expected Fail for missing required dim, got %v", result.Status)
	}
}

func TestValidateDimension_Optional_Missing(t *testing.T) {
	dim := spec.Dimension{Name: "author", Required: false, Validation: `.+`}
	result := ValidateDimension(dim, "", nil)
	if result.Status != Warning {
		t.Errorf("expected Warning for missing optional dim, got %v", result.Status)
	}
}

func TestValidateDimension_Regex_Pass(t *testing.T) {
	dim := spec.Dimension{Name: "page_url", Required: true, Validation: `^https?://`}
	result := ValidateDimension(dim, "https://foxnews.com/test", nil)
	if result.Status != Pass {
		t.Errorf("expected Pass for valid URL, got %v: %s", result.Status, result.Message)
	}
}

func TestValidateDimension_Regex_Fail(t *testing.T) {
	dim := spec.Dimension{Name: "page_url", Required: true, Validation: `^https?://`}
	result := ValidateDimension(dim, "", nil)
	if result.Status != Fail {
		t.Errorf("expected Fail for empty URL, got %v", result.Status)
	}

	result = ValidateDimension(dim, "not-a-url", nil)
	if result.Status != Fail {
		t.Errorf("expected Fail for non-URL, got %v", result.Status)
	}
}

func TestValidateDimension_Enum_Pass(t *testing.T) {
	enums := map[string]*spec.EnumSet{
		"page_types": {Name: "page_types", Values: map[string]bool{
			"article": true, "homepage": true, "video": true,
		}},
	}
	dim := spec.Dimension{Name: "page_type", Type: "enum", Validation: "@enums/page_types"}
	result := ValidateDimension(dim, "article", enums)
	if result.Status != Pass {
		t.Errorf("expected Pass for valid enum, got %v: %s", result.Status, result.Message)
	}
}

func TestValidateDimension_Enum_Fail(t *testing.T) {
	enums := map[string]*spec.EnumSet{
		"page_types": {Name: "page_types", Values: map[string]bool{
			"article": true, "homepage": true,
		}},
	}
	dim := spec.Dimension{Name: "page_type", Type: "enum", Validation: "@enums/page_types"}
	result := ValidateDimension(dim, "invalid_type", enums)
	if result.Status != Fail {
		t.Errorf("expected Fail for invalid enum, got %v: %s", result.Status, result.Message)
	}
}

func TestValidateDimension_NoValidation(t *testing.T) {
	dim := spec.Dimension{Name: "custom", Required: true}
	result := ValidateDimension(dim, "any value", nil)
	if result.Status != Pass {
		t.Errorf("expected Pass for dim with no validation, got %v", result.Status)
	}
}
