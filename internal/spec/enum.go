package spec

// EnumSet holds a named set of allowed values.
type EnumSet struct {
	Name   string
	Values map[string]bool // set for O(1) lookup
}

// Contains checks if a value is in the enum set.
func (e *EnumSet) Contains(val string) bool {
	return e.Values[val]
}
