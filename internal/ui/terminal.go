package ui

import (
	"fmt"
	"strings"

	"github.com/jwiedeman/specwatch/internal/validator"
)

const (
	reset  = "\033[0m"
	green  = "\033[32m"
	red    = "\033[31m"
	yellow = "\033[33m"
	bold   = "\033[1m"
	dim    = "\033[2m"
)

// PrintReport outputs a color-coded terminal report.
func PrintReport(report *validator.Report) {
	mappingLabel := "no mapping"
	if report.MappingName != "" {
		mappingLabel = report.MappingName + " mapping"
	}
	fmt.Printf("%sSpecWatch v0.1.0%s — Validating against: %s\n", bold, reset, mappingLabel)
	fmt.Printf("Total analytics calls detected: %d\n\n", report.TotalCalls)

	for _, br := range report.Beacons {
		printBeaconResult(br)
	}

	printSummary(report)
}

func printBeaconResult(br validator.BeaconResult) {
	separator := strings.Repeat("═", 55)
	fmt.Println(separator)

	if !br.Matched {
		fmt.Printf(" %s⚠ UNMATCHED%s — %s\n", yellow, reset, truncateURL(br.URL))
		if br.Vendor != "" {
			detail := fmt.Sprintf("   vendor=%s", br.Vendor)
			if br.RSID != "" {
				detail += fmt.Sprintf("  rsid=%s", br.RSID)
			}
			if len(br.EventsFired) > 0 {
				detail += fmt.Sprintf("  events=[%s]", strings.Join(br.EventsFired, ","))
			}
			fmt.Printf(" %s%s%s\n", dim, detail, reset)
		}
		fmt.Println(separator)
		fmt.Println()
		return
	}

	fmt.Printf(" %s%s%s — %s\n", bold, strings.ToUpper(br.EventName), reset, truncateURL(br.URL))
	fmt.Println(separator)

	for _, dr := range br.Dimensions {
		printDimensionResult(dr)
	}

	resultLabel := fmt.Sprintf("%sPASS%s", green, reset)
	if br.Errors > 0 {
		resultLabel = fmt.Sprintf("%sFAIL%s", red, reset)
	}
	fmt.Printf("\n Result: %s (%d error(s), %d warning(s))\n\n", resultLabel, br.Errors, br.Warnings)
}

func printDimensionResult(dr validator.DimensionResult) {
	var icon, color string
	switch dr.Status {
	case validator.Pass:
		icon = "✓"
		color = green
	case validator.Fail:
		icon = "✗"
		color = red
	case validator.Warning:
		icon = "⚠"
		color = yellow
	}

	field := dr.Field
	if field == "" {
		field = dr.Dimension
	}
	fmt.Printf(" %s%s%s %-14s %s\n", color, icon, reset, field, dr.Message)
}

func printSummary(report *validator.Report) {
	separator := strings.Repeat("═", 55)
	fmt.Println(separator)
	fmt.Printf(" %sSUMMARY%s\n", bold, reset)
	fmt.Println(separator)

	fmt.Printf(" Total calls:    %d\n", report.TotalCalls)

	if report.TotalCalls > 0 {
		matchedPct := float64(report.Matched) / float64(report.TotalCalls) * 100
		unmatchedPct := float64(report.Unmatched) / float64(report.TotalCalls) * 100
		fmt.Printf(" Matched specs:  %d (%.1f%%)\n", report.Matched, matchedPct)
		fmt.Printf(" Unmatched:      %d (%.1f%%) — no matching event spec\n", report.Unmatched, unmatchedPct)
		fmt.Println()

		if report.Matched > 0 {
			passedPct := float64(report.Passed) / float64(report.Matched) * 100
			failedPct := float64(report.Failed) / float64(report.Matched) * 100
			fmt.Printf(" %sPassed:%s         %d (%.1f%%)\n", green, reset, report.Passed, passedPct)
			fmt.Printf(" %sFailed:%s         %d (%.1f%%)\n", red, reset, report.Failed, failedPct)
		}
	}

	if len(report.TopIssues) > 0 {
		fmt.Println()
		fmt.Printf(" %sTop issues:%s\n", bold, reset)
		for i, issue := range report.TopIssues {
			fmt.Printf("  %d. %-40s — %d occurrence(s)\n", i+1, issue.Message, issue.Count)
		}
	}

	fmt.Println()
}

func truncateURL(u string) string {
	if len(u) > 80 {
		return u[:77] + "..."
	}
	return u
}
