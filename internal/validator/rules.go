package validator

import (
	"fmt"
	"regexp"

	"github.com/jwiedeman/specwatch/internal/spec"
)

// ValidateDimension checks a single dimension value against the spec.
func ValidateDimension(dim spec.Dimension, value string, enums map[string]*spec.EnumSet) DimensionResult {
	result := DimensionResult{
		Dimension: dim.Name,
		Value:     value,
	}

	// Check required presence
	if value == "" {
		if dim.Required {
			result.Status = Fail
			result.Message = "MISSING — required dimension not found"
		} else {
			result.Status = Warning
			result.Message = "NOT SET — optional, but recommended"
		}
		return result
	}

	// Enum validation
	if dim.Type == "enum" || isEnumRef(dim.Validation) {
		enumName := dim.Validation
		if isEnumRef(enumName) {
			enumName = enumName[len("@enums/"):]
		}
		if es, ok := enums[enumName]; ok {
			if es.Contains(value) {
				result.Status = Pass
				result.Message = fmt.Sprintf("%q (valid enum)", value)
			} else {
				result.Status = Fail
				result.Message = fmt.Sprintf("%q — not a valid %s value", value, enumName)
			}
			return result
		}
		// Enum set not found — pass with warning
		result.Status = Warning
		result.Message = fmt.Sprintf("enum set %q not found in spec", enumName)
		return result
	}

	// Regex validation
	if dim.Validation != "" {
		re, err := regexp.Compile(dim.Validation)
		if err != nil {
			result.Status = Warning
			result.Message = fmt.Sprintf("invalid regex %q in spec", dim.Validation)
			return result
		}
		if re.MatchString(value) {
			result.Status = Pass
			result.Message = fmt.Sprintf("%q", value)
		} else {
			result.Status = Fail
			result.Message = fmt.Sprintf("%q — fails regex %s", value, dim.Validation)
		}
		return result
	}

	// No validation rule — pass
	result.Status = Pass
	result.Message = fmt.Sprintf("%q", value)
	return result
}

func isEnumRef(s string) bool {
	return len(s) > 7 && s[:7] == "@enums/"
}
