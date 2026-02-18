package har

import (
	"encoding/json"
	"fmt"
	"net/url"
	"os"
)

// ParseFile reads a HAR file and returns a slice of NetworkEvents.
func ParseFile(path string) ([]NetworkEvent, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("reading HAR file: %w", err)
	}

	var h HAR
	if err := json.Unmarshal(data, &h); err != nil {
		return nil, fmt.Errorf("parsing HAR JSON: %w", err)
	}

	events := make([]NetworkEvent, 0, len(h.Log.Entries))
	for _, entry := range h.Log.Entries {
		ev := entryToEvent(entry)
		events = append(events, ev)
	}
	return events, nil
}

func entryToEvent(e Entry) NetworkEvent {
	ev := NetworkEvent{
		Method:      e.Request.Method,
		URL:         e.Request.URL,
		Headers:     make(map[string]string),
		QueryParams: make(map[string]string),
		PostParams:  make(map[string]string),
	}

	for _, h := range e.Request.Headers {
		ev.Headers[h.Name] = h.Value
	}

	// Use queryString array from HAR if available
	for _, q := range e.Request.QueryString {
		ev.QueryParams[q.Name] = q.Value
	}

	// Fallback: parse query params from URL if queryString array was empty
	if len(ev.QueryParams) == 0 {
		if parsed, err := url.Parse(e.Request.URL); err == nil {
			for k, v := range parsed.Query() {
				if len(v) > 0 {
					ev.QueryParams[k] = v[0]
				}
			}
		}
	}

	if e.Request.PostData != nil {
		ev.PostBody = e.Request.PostData.Text
		for _, p := range e.Request.PostData.Params {
			ev.PostParams[p.Name] = p.Value
		}
	}

	return ev
}
