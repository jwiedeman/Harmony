package validator

import "encoding/json"

// Status represents the outcome of a single validation check.
type Status int

const (
	Pass Status = iota
	Fail
	Warning
)

func (s Status) String() string {
	switch s {
	case Pass:
		return "pass"
	case Fail:
		return "fail"
	case Warning:
		return "warning"
	default:
		return "unknown"
	}
}

func (s Status) MarshalJSON() ([]byte, error) {
	return json.Marshal(s.String())
}

// DimensionResult holds the validation result for a single dimension.
type DimensionResult struct {
	Dimension string `json:"dimension"`
	Field     string `json:"field"`
	Value     string `json:"value"`
	Status    Status `json:"status"`
	Message   string `json:"message"`
}

// BeaconResult holds all validation results for a single beacon.
type BeaconResult struct {
	URL        string            `json:"url"`
	Vendor     string            `json:"vendor,omitempty"`
	EventName  string            `json:"event_name"`
	RSID       string            `json:"rsid"`
	EventsFired []string         `json:"events_fired,omitempty"`
	Dimensions []DimensionResult `json:"dimensions"`
	Errors     int               `json:"errors"`
	Warnings   int               `json:"warnings"`
	Matched    bool              `json:"matched"`
}

// IssueSummary aggregates a recurring issue across beacons.
type IssueSummary struct {
	Message string `json:"message"`
	Count   int    `json:"count"`
}

// Report holds the complete validation run results.
type Report struct {
	TotalEntries int            `json:"total_entries"` // total HAR network entries before filtering
	TotalCalls   int            `json:"total_calls"`   // analytics beacons detected
	Matched      int            `json:"matched"`
	Unmatched    int            `json:"unmatched"`
	Passed       int            `json:"passed"`
	Failed       int            `json:"failed"`
	Beacons      []BeaconResult `json:"beacons"`
	TopIssues    []IssueSummary `json:"top_issues"`
	MappingName  string         `json:"mapping_name"`
}
