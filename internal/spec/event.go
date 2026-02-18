package spec

// EventSpec defines a single analytics event and its expected dimensions.
type EventSpec struct {
	Name        string
	Description string
	Required    []Dimension
	Optional    []Dimension
	Overrides   map[string]PlatformOverride // keyed by platform name
}

// PlatformOverride holds platform-specific mapping and requirements for an event.
type PlatformOverride struct {
	Platform      string
	DimMappings   map[string]string // canonical_name -> platform field (e.g. "page_url" -> "eVar75")
	RequiredEvent string            // e.g. "event1" for page_view on adobe
	Notes         []string
}
