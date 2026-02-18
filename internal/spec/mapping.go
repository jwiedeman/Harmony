package spec

// Mapping holds the eVar/prop/event mapping for a specific property (e.g. fox_news).
type Mapping struct {
	Name       string
	ProdRSID   string
	DevRSID    string
	DimMap     map[string]DimMapping   // canonical name -> eVar/prop mapping
	EventMap   map[string]string       // canonical event -> adobe event (e.g. "page_view" -> "event1")
}

// DimMapping maps a canonical dimension to its platform-specific field names.
type DimMapping struct {
	Canonical string
	EVar      string // e.g. "v75"
	Prop      string // e.g. "c75"
	Notes     string
}
