package parsers

// Beacon represents a parsed analytics call with vendor-specific fields normalized.
type Beacon struct {
	Vendor    string            // e.g. "adobe_appmeasurement", "ga4"
	RawURL    string            // original request URL
	RSID      string            // report suite ID (Adobe) or measurement ID (GA4)
	PageName  string            // page name if present
	PageURL   string            // page URL extracted from beacon
	EventList []string          // list of events (e.g. ["event1", "event50"])
	EVars     map[string]string // eVar values keyed by number: "75" -> "value"
	Props     map[string]string // prop values keyed by number: "4" -> "value"
	LinkType  string            // pe field: lnk_o, lnk_d, lnk_e
	LinkName  string            // pev2 field: custom link name
	Platform  string            // detected platform from User-Agent
	RawParams map[string]string // all raw query/post parameters
}
