package ui

import (
	"encoding/json"
	"fmt"

	"github.com/jwiedeman/specwatch/internal/validator"
)

// PrintJSON outputs the report as JSON for CI/CD consumption.
func PrintJSON(report *validator.Report) error {
	data, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		return fmt.Errorf("marshaling report: %w", err)
	}
	fmt.Println(string(data))
	return nil
}
