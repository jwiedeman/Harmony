package spec

// Dimension defines a single analytics dimension (variable).
type Dimension struct {
	Name       string // canonical name, e.g. "page_url"
	Type       string // string, enum, datetime, array
	Validation string // regex pattern or @enums/ref
	Notes      string
	Required   bool
}
