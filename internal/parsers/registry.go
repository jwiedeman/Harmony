package parsers

import "github.com/jwiedeman/specwatch/internal/har"

// Parser detects and parses analytics beacons from network events.
type Parser interface {
	// Detect returns true if this parser can handle the given network event.
	Detect(ev har.NetworkEvent) bool
	// Parse extracts a Beacon from the network event.
	Parse(ev har.NetworkEvent) Beacon
}

var registry []Parser

// Register adds a parser to the global registry. Called from init() in parser files.
func Register(p Parser) {
	registry = append(registry, p)
}

// ParseAll runs all registered parsers against the given network events.
// Returns only events that matched a parser.
func ParseAll(events []har.NetworkEvent) []Beacon {
	var beacons []Beacon
	for _, ev := range events {
		for _, p := range registry {
			if p.Detect(ev) {
				beacons = append(beacons, p.Parse(ev))
				break // first match wins
			}
		}
	}
	return beacons
}
