package validator

import (
	"fmt"
	"sort"
	"strings"

	"github.com/jwiedeman/specwatch/internal/har"
	"github.com/jwiedeman/specwatch/internal/parsers"
	"github.com/jwiedeman/specwatch/internal/spec"
)

// Engine performs validation of analytics beacons against a spec.
type Engine struct {
	Spec    *spec.Spec
	Mapping *spec.Mapping
}

// NewEngine creates a validation engine with the given spec and mapping context.
func NewEngine(s *spec.Spec, mapping *spec.Mapping) *Engine {
	return &Engine{Spec: s, Mapping: mapping}
}

// ValidateHAR runs the full validation pipeline on a HAR file.
func (e *Engine) ValidateHAR(path string) (*Report, error) {
	// 1. Parse HAR into network events
	events, err := har.ParseFile(path)
	if err != nil {
		return nil, fmt.Errorf("parsing HAR: %w", err)
	}

	// 2. Run all events through beacon parsers
	beacons := parsers.ParseAll(events)

	report := &Report{
		TotalCalls: len(beacons),
	}
	if e.Mapping != nil {
		report.MappingName = e.Mapping.Name
	}

	issueCounts := make(map[string]int)

	// 3. Validate each beacon
	for _, beacon := range beacons {
		br := e.validateBeacon(beacon, issueCounts)
		report.Beacons = append(report.Beacons, br)
		if br.Matched {
			report.Matched++
			if br.Errors == 0 {
				report.Passed++
			} else {
				report.Failed++
			}
		} else {
			report.Unmatched++
		}
	}

	// 4. Build top issues
	report.TopIssues = buildTopIssues(issueCounts)

	return report, nil
}

func (e *Engine) validateBeacon(beacon parsers.Beacon, issueCounts map[string]int) BeaconResult {
	br := BeaconResult{
		URL:         beacon.RawURL,
		Vendor:      beacon.Vendor,
		RSID:        beacon.RSID,
		EventsFired: beacon.EventList,
	}

	// Match beacon to event spec via mapping's EventMap
	eventSpec := e.matchEvent(beacon)
	if eventSpec == nil {
		br.Matched = false
		return br
	}

	br.Matched = true
	br.EventName = eventSpec.Name

	// Validate RSID if mapping is available
	if e.Mapping != nil {
		rsidResult := e.validateRSID(beacon.RSID)
		br.Dimensions = append(br.Dimensions, rsidResult)
		if rsidResult.Status == Fail {
			br.Errors++
			issueCounts[rsidResult.Message]++
		}
	}

	// Validate required dimensions
	for _, dim := range eventSpec.Required {
		value := e.resolveValue(beacon, dim.Name)
		field := e.resolveFieldName(dim.Name)
		result := ValidateDimension(dim, value, e.Spec.Enums)
		result.Field = field
		br.Dimensions = append(br.Dimensions, result)
		switch result.Status {
		case Fail:
			br.Errors++
			issueCounts[dim.Name+" "+result.Message]++
		case Warning:
			br.Warnings++
		}
	}

	// Validate optional dimensions
	for _, dim := range eventSpec.Optional {
		value := e.resolveValue(beacon, dim.Name)
		if value == "" {
			// Optional and not set — just a warning
			br.Dimensions = append(br.Dimensions, DimensionResult{
				Dimension: dim.Name,
				Field:     e.resolveFieldName(dim.Name),
				Status:    Warning,
				Message:   "NOT SET — optional, but recommended",
			})
			br.Warnings++
			continue
		}
		field := e.resolveFieldName(dim.Name)
		result := ValidateDimension(dim, value, e.Spec.Enums)
		result.Field = field
		br.Dimensions = append(br.Dimensions, result)
		switch result.Status {
		case Fail:
			br.Errors++
			issueCounts[dim.Name+" "+result.Message]++
		case Warning:
			br.Warnings++
		}
	}

	// Validate required events from platform overrides
	if override, ok := eventSpec.Overrides[beacon.Vendor]; ok {
		if override.RequiredEvent != "" {
			found := false
			for _, ev := range beacon.EventList {
				if ev == override.RequiredEvent {
					found = true
					break
				}
			}
			result := DimensionResult{
				Dimension: "events",
				Value:     strings.Join(beacon.EventList, ","),
			}
			if found {
				result.Status = Pass
				result.Message = fmt.Sprintf("%s (required for %s)", override.RequiredEvent, eventSpec.Name)
			} else {
				result.Status = Fail
				result.Message = fmt.Sprintf("MISSING %s — required for %s", override.RequiredEvent, eventSpec.Name)
				br.Errors++
				issueCounts[result.Message]++
			}
			br.Dimensions = append(br.Dimensions, result)
		}
	}

	// Check for unknown eVars (not in mapping)
	if e.Mapping != nil {
		knownEvars := make(map[string]bool)
		for _, dm := range e.Mapping.DimMap {
			if dm.EVar != "" {
				knownEvars[strings.TrimPrefix(dm.EVar, "v")] = true
			}
		}
		for num, val := range beacon.EVars {
			if !knownEvars[num] {
				br.Dimensions = append(br.Dimensions, DimensionResult{
					Dimension: "UNKNOWN",
					Field:     "v" + num,
					Value:     val,
					Status:    Warning,
					Message:   fmt.Sprintf("v%s = %q — not in spec, possible debug value", num, val),
				})
				br.Warnings++
			}
		}
	}

	return br
}

// matchEvent finds the event spec that matches this beacon.
func (e *Engine) matchEvent(beacon parsers.Beacon) *spec.EventSpec {
	if e.Mapping == nil {
		return nil
	}

	// Check which events fired in this beacon and match against EventMap
	for canonicalEvent, adobeEvent := range e.Mapping.EventMap {
		for _, fired := range beacon.EventList {
			if fired == adobeEvent {
				if es, ok := e.Spec.Events[canonicalEvent]; ok {
					return es
				}
			}
		}
	}

	// If no event match and it has a pageName, try page_view as default
	if beacon.PageName != "" && beacon.LinkType == "" {
		if es, ok := e.Spec.Events["page_view"]; ok {
			return es
		}
	}

	return nil
}

// resolveValue extracts the value for a canonical dimension from a beacon using the mapping.
func (e *Engine) resolveValue(beacon parsers.Beacon, dimName string) string {
	if e.Mapping != nil {
		if dm, ok := e.Mapping.DimMap[dimName]; ok {
			// Try eVar first
			if dm.EVar != "" {
				num := strings.TrimPrefix(dm.EVar, "v")
				if val, ok := beacon.EVars[num]; ok && val != "" {
					return val
				}
			}
			// Try prop
			if dm.Prop != "" {
				num := strings.TrimPrefix(dm.Prop, "c")
				if val, ok := beacon.Props[num]; ok && val != "" {
					return val
				}
			}
		}
	}

	// Fallback: check raw params by dimension name
	if val, ok := beacon.RawParams[dimName]; ok {
		return val
	}

	// Special cases
	switch dimName {
	case "page_url":
		return beacon.PageURL
	case "page_title":
		return beacon.RawParams["pageName"]
	}

	return ""
}

// resolveFieldName returns the platform-specific field name for a canonical dimension.
func (e *Engine) resolveFieldName(dimName string) string {
	if e.Mapping != nil {
		if dm, ok := e.Mapping.DimMap[dimName]; ok {
			if dm.EVar != "" {
				return dm.EVar
			}
			if dm.Prop != "" {
				return dm.Prop
			}
		}
	}
	return dimName
}

// validateRSID checks the beacon's RSID against the mapping.
func (e *Engine) validateRSID(rsid string) DimensionResult {
	result := DimensionResult{
		Dimension: "RSID",
		Value:     rsid,
	}

	if rsid == "" {
		result.Status = Fail
		result.Message = "MISSING — no RSID found"
		return result
	}

	if rsid == e.Mapping.ProdRSID {
		result.Status = Pass
		result.Message = fmt.Sprintf("%s (matches %s mapping)", rsid, e.Mapping.Name)
	} else if rsid == e.Mapping.DevRSID {
		result.Status = Pass
		result.Message = fmt.Sprintf("%s (dev/QA — matches %s mapping)", rsid, e.Mapping.Name)
	} else {
		result.Status = Fail
		result.Message = fmt.Sprintf("%s — does not match %s mapping (expected %s or %s)",
			rsid, e.Mapping.Name, e.Mapping.ProdRSID, e.Mapping.DevRSID)
	}

	return result
}

func buildTopIssues(counts map[string]int) []IssueSummary {
	issues := make([]IssueSummary, 0, len(counts))
	for msg, count := range counts {
		issues = append(issues, IssueSummary{Message: msg, Count: count})
	}
	sort.Slice(issues, func(i, j int) bool {
		return issues[i].Count > issues[j].Count
	})
	if len(issues) > 10 {
		issues = issues[:10]
	}
	return issues
}
