package spec

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// Spec holds the complete parsed specification.
type Spec struct {
	Enums    map[string]*EnumSet   // enum name -> set
	Events   map[string]*EventSpec // event name -> spec
	Mappings map[string]*Mapping   // mapping name -> mapping
	Packages map[string]*Package   // package name -> package
}

// LoadSpec reads a spec directory and returns a fully resolved Spec.
func LoadSpec(dir string) (*Spec, error) {
	s := &Spec{
		Enums:    make(map[string]*EnumSet),
		Events:   make(map[string]*EventSpec),
		Mappings: make(map[string]*Mapping),
		Packages: make(map[string]*Package),
	}

	// 1. Parse enums from _global/enums.md
	enumPath := filepath.Join(dir, "_global", "enums.md")
	if _, err := os.Stat(enumPath); err == nil {
		enums, err := parseEnumsFile(enumPath)
		if err != nil {
			return nil, fmt.Errorf("parsing enums: %w", err)
		}
		s.Enums = enums
	}

	// 2. Parse event specs from events/*.md
	eventsDir := filepath.Join(dir, "events")
	if entries, err := os.ReadDir(eventsDir); err == nil {
		for _, e := range entries {
			if e.IsDir() || !strings.HasSuffix(e.Name(), ".md") {
				continue
			}
			ev, err := parseEventFile(filepath.Join(eventsDir, e.Name()))
			if err != nil {
				return nil, fmt.Errorf("parsing event %s: %w", e.Name(), err)
			}
			s.Events[ev.Name] = ev
		}
	}

	// 3. Parse mappings from mappings/*.md
	mappingsDir := filepath.Join(dir, "mappings")
	if entries, err := os.ReadDir(mappingsDir); err == nil {
		for _, e := range entries {
			if e.IsDir() || !strings.HasSuffix(e.Name(), ".md") {
				continue
			}
			m, err := parseMappingFile(filepath.Join(mappingsDir, e.Name()))
			if err != nil {
				return nil, fmt.Errorf("parsing mapping %s: %w", e.Name(), err)
			}
			s.Mappings[m.Name] = m
		}
	}

	// 4. Parse packages from packages/*.md
	packagesDir := filepath.Join(dir, "packages")
	if entries, err := os.ReadDir(packagesDir); err == nil {
		for _, e := range entries {
			if e.IsDir() || !strings.HasSuffix(e.Name(), ".md") {
				continue
			}
			pkg, err := parsePackageFile(filepath.Join(packagesDir, e.Name()))
			if err != nil {
				return nil, fmt.Errorf("parsing package %s: %w", e.Name(), err)
			}
			s.Packages[pkg.Name] = pkg
		}
	}

	// 5. Resolve @enums/ references in dimensions
	for _, ev := range s.Events {
		resolveEnumRefs(ev.Required, s.Enums)
		resolveEnumRefs(ev.Optional, s.Enums)
	}

	return s, nil
}

// resolveEnumRefs replaces @enums/name references with the actual enum values for validation.
func resolveEnumRefs(dims []Dimension, enums map[string]*EnumSet) {
	for i, d := range dims {
		if strings.HasPrefix(d.Validation, "@enums/") {
			enumName := strings.TrimPrefix(d.Validation, "@enums/")
			if _, ok := enums[enumName]; ok {
				dims[i].Type = "enum"
			}
		}
	}
}

// parseEnumsFile parses _global/enums.md into a map of EnumSets.
// Format: ## heading = enum name, - value = entry
func parseEnumsFile(path string) (map[string]*EnumSet, error) {
	lines, err := readLines(path)
	if err != nil {
		return nil, err
	}

	enums := make(map[string]*EnumSet)
	var current *EnumSet

	for _, line := range lines {
		trimmed := strings.TrimSpace(line)
		if strings.HasPrefix(trimmed, "## ") {
			name := strings.TrimSpace(strings.TrimPrefix(trimmed, "## "))
			current = &EnumSet{Name: name, Values: make(map[string]bool)}
			enums[name] = current
		} else if strings.HasPrefix(trimmed, "- ") && current != nil {
			val := strings.TrimSpace(strings.TrimPrefix(trimmed, "- "))
			current.Values[val] = true
		}
	}

	return enums, nil
}

// parseEventFile parses an event spec markdown file.
func parseEventFile(path string) (*EventSpec, error) {
	lines, err := readLines(path)
	if err != nil {
		return nil, err
	}

	ev := &EventSpec{
		Overrides: make(map[string]PlatformOverride),
	}

	// Extract name from # heading
	section := ""
	var overridePlatform string

	for i := 0; i < len(lines); i++ {
		trimmed := strings.TrimSpace(lines[i])

		if strings.HasPrefix(trimmed, "# ") && !strings.HasPrefix(trimmed, "## ") && !strings.HasPrefix(trimmed, "### ") {
			ev.Name = strings.TrimSpace(strings.TrimPrefix(trimmed, "# "))
			continue
		}

		if strings.HasPrefix(trimmed, "## ") && !strings.HasPrefix(trimmed, "### ") {
			section = strings.TrimSpace(strings.TrimPrefix(trimmed, "## "))
			overridePlatform = ""
			continue
		}

		if strings.HasPrefix(trimmed, "### ") {
			if section == "Platform Overrides" {
				overridePlatform = strings.TrimSpace(strings.TrimPrefix(trimmed, "### "))
				ev.Overrides[overridePlatform] = PlatformOverride{
					Platform:    overridePlatform,
					DimMappings: make(map[string]string),
				}
			}
			continue
		}

		// Parse dimension tables in Required/Optional sections
		if (section == "Required Dimensions" || section == "Optional Dimensions") && isTableRow(trimmed) && !isTableSeparator(trimmed) {
			dim := parseTableRowAsDimension(trimmed)
			if dim.Name == "" || dim.Name == "Dimension" {
				continue // skip header row
			}
			dim.Required = section == "Required Dimensions"
			if dim.Required {
				ev.Required = append(ev.Required, dim)
			} else {
				ev.Optional = append(ev.Optional, dim)
			}
		}

		// Parse platform override bullet points
		if section == "Platform Overrides" && overridePlatform != "" && strings.HasPrefix(trimmed, "- ") {
			ov := ev.Overrides[overridePlatform]
			bullet := strings.TrimPrefix(trimmed, "- ")

			if strings.HasPrefix(bullet, "Requires: `events=") {
				// Extract required event
				event := strings.TrimSuffix(strings.TrimPrefix(bullet, "Requires: `events="), "`")
				ov.RequiredEvent = event
			} else if strings.Contains(bullet, "→") {
				// Dimension mapping: `page_url` → `eVar75`
				parts := strings.SplitN(bullet, "→", 2)
				if len(parts) == 2 {
					dimName := extractBacktickValue(strings.TrimSpace(parts[0]))
					fieldName := extractBacktickValue(strings.TrimSpace(parts[1]))
					if dimName != "" && fieldName != "" {
						ov.DimMappings[dimName] = fieldName
					}
				}
			} else {
				ov.Notes = append(ov.Notes, bullet)
			}

			ev.Overrides[overridePlatform] = ov
		}

		// Description: text between # heading and first ## heading
		if ev.Name != "" && section == "" && trimmed != "" && !strings.HasPrefix(trimmed, "#") {
			if ev.Description != "" {
				ev.Description += " "
			}
			ev.Description += trimmed
		}
	}

	if ev.Name == "" {
		ev.Name = strings.TrimSuffix(filepath.Base(path), ".md")
	}

	return ev, nil
}

// parseMappingFile parses a mapping markdown file.
func parseMappingFile(path string) (*Mapping, error) {
	lines, err := readLines(path)
	if err != nil {
		return nil, err
	}

	m := &Mapping{
		DimMap:   make(map[string]DimMapping),
		EventMap: make(map[string]string),
	}

	section := ""

	for _, line := range lines {
		trimmed := strings.TrimSpace(line)

		if strings.HasPrefix(trimmed, "# ") && !strings.HasPrefix(trimmed, "## ") {
			m.Name = strings.ToLower(strings.ReplaceAll(
				strings.TrimSpace(strings.TrimPrefix(trimmed, "# ")),
				" ", "_",
			))
			// Also handle multi-word names: "Fox News & Fox Business Mapping" -> "fox_news"
			// Use filename as fallback
			continue
		}

		if strings.HasPrefix(trimmed, "## ") {
			section = strings.TrimSpace(strings.TrimPrefix(trimmed, "## "))
			continue
		}

		// Report suite bullets
		if section == "Report Suite" && strings.HasPrefix(trimmed, "- ") {
			bullet := strings.TrimPrefix(trimmed, "- ")
			if strings.HasPrefix(bullet, "Production:") {
				m.ProdRSID = extractBacktickValue(strings.TrimPrefix(bullet, "Production:"))
				if m.ProdRSID == "" {
					m.ProdRSID = strings.TrimSpace(strings.TrimPrefix(bullet, "Production:"))
				}
			} else if strings.HasPrefix(bullet, "Dev/QA:") || strings.HasPrefix(bullet, "Dev:") {
				m.DevRSID = extractBacktickValue(strings.TrimPrefix(bullet, "Dev/QA:"))
				if m.DevRSID == "" {
					m.DevRSID = strings.TrimSpace(strings.TrimPrefix(bullet, "Dev/QA:"))
				}
			}
		}

		// Dimension mapping table
		if section == "Dimension Mapping" && isTableRow(trimmed) && !isTableSeparator(trimmed) {
			cells := parseTableCells(trimmed)
			if len(cells) >= 3 && cells[0] != "Canonical Name" {
				dm := DimMapping{
					Canonical: cells[0],
					EVar:      cells[1],
					Prop:      cells[2],
				}
				if len(cells) >= 4 {
					dm.Notes = cells[3]
				}
				m.DimMap[cells[0]] = dm
			}
		}

		// Event mapping table
		if section == "Event Mapping" && isTableRow(trimmed) && !isTableSeparator(trimmed) {
			cells := parseTableCells(trimmed)
			if len(cells) >= 2 && cells[0] != "Canonical Event" {
				m.EventMap[cells[0]] = cells[1]
			}
		}
	}

	// Use filename as name if heading was complex
	if m.Name == "" || len(m.Name) > 30 {
		m.Name = strings.TrimSuffix(filepath.Base(path), ".md")
	}

	return m, nil
}

// parsePackageFile parses a package markdown file (minimal for Phase 1).
func parsePackageFile(path string) (*Package, error) {
	lines, err := readLines(path)
	if err != nil {
		return nil, err
	}

	pkg := &Package{
		Fields: make(map[string]string),
	}

	section := ""

	for _, line := range lines {
		trimmed := strings.TrimSpace(line)

		if strings.HasPrefix(trimmed, "# ") && !strings.HasPrefix(trimmed, "## ") {
			pkg.Name = strings.TrimSpace(strings.TrimPrefix(trimmed, "# "))
			continue
		}

		if strings.HasPrefix(trimmed, "## ") {
			section = strings.TrimSpace(strings.TrimPrefix(trimmed, "## "))
			continue
		}

		if section == "Endpoint Detection" && strings.HasPrefix(trimmed, "- URL pattern:") {
			pkg.EndpointPattern = extractBacktickValue(strings.TrimPrefix(trimmed, "- URL pattern:"))
			if pkg.EndpointPattern == "" {
				pkg.EndpointPattern = strings.TrimSpace(strings.TrimPrefix(trimmed, "- URL pattern:"))
			}
		}

		if section == "Endpoint Detection" && strings.HasPrefix(trimmed, "- Method:") {
			pkg.Method = strings.TrimSpace(strings.TrimPrefix(trimmed, "- Method:"))
		}

		if section == "Beacon Parsing" && strings.HasPrefix(trimmed, "  - `") {
			// Parse field definitions like "  - `rsid` — Report Suite ID"
			content := strings.TrimPrefix(trimmed, "  - ")
			if idx := strings.Index(content, "` — "); idx > 0 {
				key := strings.Trim(content[:idx], "`")
				val := content[idx+len("` — "):]
				pkg.Fields[key] = val
			} else if idx := strings.Index(content, "` - "); idx > 0 {
				key := strings.Trim(content[:idx], "`")
				val := content[idx+len("` - "):]
				pkg.Fields[key] = val
			}
		}
	}

	if pkg.Name == "" {
		pkg.Name = strings.TrimSuffix(filepath.Base(path), ".md")
	}

	return pkg, nil
}

// --- Markdown table parsing helpers ---

func isTableRow(line string) bool {
	return strings.HasPrefix(line, "|") && strings.HasSuffix(line, "|")
}

func isTableSeparator(line string) bool {
	cleaned := strings.ReplaceAll(strings.ReplaceAll(line, "|", ""), "-", "")
	cleaned = strings.ReplaceAll(cleaned, ":", "")
	return strings.TrimSpace(cleaned) == ""
}

func parseTableCells(line string) []string {
	line = strings.Trim(line, "|")
	parts := strings.Split(line, "|")
	cells := make([]string, len(parts))
	for i, p := range parts {
		cells[i] = strings.TrimSpace(p)
	}
	return cells
}

func parseTableRowAsDimension(line string) Dimension {
	cells := parseTableCells(line)
	d := Dimension{}
	if len(cells) >= 1 {
		d.Name = cells[0]
	}
	if len(cells) >= 2 {
		d.Type = cells[1]
	}
	if len(cells) >= 3 {
		d.Validation = strings.Trim(cells[2], "`")
	}
	if len(cells) >= 4 {
		d.Notes = cells[3]
	}
	return d
}

func extractBacktickValue(s string) string {
	s = strings.TrimSpace(s)
	// Handle values that may contain pipe for multiple mappings: `eVar75` (fox_news) | `eVar12` (fox_corp)
	// Return first backtick value
	start := strings.Index(s, "`")
	if start < 0 {
		return ""
	}
	end := strings.Index(s[start+1:], "`")
	if end < 0 {
		return ""
	}
	return s[start+1 : start+1+end]
}

func readLines(path string) ([]string, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	var lines []string
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		lines = append(lines, scanner.Text())
	}
	return lines, scanner.Err()
}
