package spec

// Package defines how to detect and parse a specific analytics platform's beacons.
type Package struct {
	Name            string
	EndpointPattern string            // URL pattern for detection, e.g. "/b/ss/"
	Method          string            // expected HTTP method
	Fields          map[string]string // key field descriptions
}
