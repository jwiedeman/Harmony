# SpecWatch — Analytics Validation Proxy & Parser

## Project Evolution

This repo started as **Harmony**, a Python/web-based HAR analysis tool for QA testing. We're evolving it into **SpecWatch** — a cross-platform, spec-driven analytics validation tool built in Go. The existing HAR files and test data in this repo serve as real-world test fixtures for the new engine.

## Project Overview

SpecWatch intercepts or ingests analytics network calls (Adobe Analytics, GA4, Tealium, Snowplow, etc.), validates them against a user-defined measurement spec, and reports pass/fail per event with detailed diagnostics.

**Core philosophy:** Markdown-native specs, zero config for devs, single binary, works everywhere.

---

## Operating Modes

### Mode 1: Local Proxy (Live Capture)
- Dev points browser/emulator/device at `localhost:8888`
- SpecWatch intercepts HTTPS traffic via local CA cert
- Pattern-matches collection endpoints in real time
- Validates and reports in terminal or local web UI

### Mode 2: HAR Parser (Offline Analysis)
- Ingest `.har` files exported from browser DevTools, Charles, etc.
- Parse all network entries, filter for analytics calls
- Run same validation pipeline against spec
- Output report as terminal, JSON, or HTML

### Mode 3: CI/CD Pipeline
- Accepts HAR or raw beacon payloads via stdin/file
- JSON output for automated test assertions
- Exit codes for pass/fail integration with build systems

---

## Spec Format (Markdown-Native)

All specs are plain Markdown files compatible with Obsidian, GitHub, and any MD editor. The directory structure IS the configuration.

```
specs/
├── _global/
│   ├── dimensions.md          # Master dimension definitions
│   ├── enums.md               # Allowed value enumerations
│   └── platforms.md           # Platform-specific considerations
├── events/
│   ├── page_view.md
│   ├── video_start.md
│   ├── video_complete.md
│   ├── link_click.md
│   ├── search.md
│   └── ...
├── packages/
│   ├── adobe_appmeasurement.md
│   ├── adobe_websdk.md
│   ├── adobe_launch.md
│   ├── ga4.md
│   ├── tealium.md
│   └── ...
└── mappings/
    ├── fox_corp.md            # Fox Corp RSID + eVar/prop mapping
    ├── fox_news.md            # FN/FB RSID + eVar/prop mapping
    └── umg.md                 # UMG mapping example
```

### Event Spec Example: `events/page_view.md`

```markdown
# page_view

Page load event fired on all full page navigations.

## Required Dimensions

| Dimension       | Type     | Validation              | Notes                    |
|----------------|----------|-------------------------|--------------------------|
| page_url       | string   | `^https?://`            | Full URL including query |
| page_title     | string   | `.{1,255}`              | Non-empty, max 255 char  |
| page_type      | enum     | @enums/page_types       | Reference global enum    |
| content_id     | string   | `^[a-zA-Z0-9\-]+$`     | CMS content identifier   |
| site_section   | enum     | @enums/site_sections    | Primary nav section      |

## Optional Dimensions

| Dimension       | Type     | Validation              | Notes                    |
|----------------|----------|-------------------------|--------------------------|
| author         | string   | `.+`                    | Article author if exists |
| publish_date   | datetime | ISO8601                 | Original publish date    |
| tags           | array    | `.+`                    | Content tags             |

## Platform Overrides

### adobe_appmeasurement
- `page_url` → `eVar75` (fox_news) | `eVar12` (fox_corp)
- `page_type` → `eVar3`
- Requires: `events=event1`
- Requires: `rsid` matches mapping

### ga4
- Maps to: `page_view` (native enhanced measurement)
- Custom dimensions sent via `ep.*` parameters

### adobe_websdk
- Maps to XDM: `web.webPageDetails.URL`
- Page type via: `_experience.analytics.customDimensions.eVars.eVar3`
```

### Dimension Enum Example: `_global/enums.md`

```markdown
# Enums

## page_types
- homepage
- article
- video
- gallery
- search_results
- section_front
- live_tv
- weather_forecast
- sports_scores

## site_sections
- news
- politics
- entertainment
- sports
- weather
- opinion
- business
- tech
- lifestyle
```

### Platform Package Example: `packages/adobe_appmeasurement.md`

```markdown
# Adobe AppMeasurement

## Endpoint Detection
- URL pattern: `/b/ss/`
- Method: GET (image request) or POST

## Beacon Parsing
- Query string encoded
- Key fields:
  - `rsid` — Report Suite ID
  - `pageName` — Page name
  - `g` or `r` — Page URL / Referrer
  - `c[n]` — Props (c1, c2, etc.)
  - `v[n]` — eVars (v1, v75, etc.)
  - `events` — Comma-separated event list
  - `pe` — Link type (lnk_o, lnk_d, lnk_e)
  - `pev2` — Custom link name
  - `mid` — Marketing Cloud ID
  - `aid` — Analytics ID

## RSID Validation
- Must match mapping file for current spec context
- Flag unknown RSIDs as warnings

## Version Detection
- `AQE` header or `apv` param indicates version
- Flag outdated versions based on package config
```

### Mapping Example: `mappings/fox_news.md`

```markdown
# Fox News & Fox Business Mapping

## Report Suite
- Production: `foxnewsglobal`
- Dev/QA: `foxnewsdev`

## Dimension Mapping

| Canonical Name    | eVar  | Prop  | Notes                       |
|-------------------|-------|-------|-----------------------------|
| page_url          | v75   | c75   | Duplicated to prop          |
| page_type         | v3    |       |                             |
| content_id        | v18   |       |                             |
| site_section      | v4    | c4    |                             |
| author            | v22   |       |                             |
| video_id          | v30   |       |                             |
| video_name        | v31   |       |                             |
| player_name       | v32   |       |                             |

## Event Mapping

| Canonical Event   | Adobe Event | Notes                     |
|-------------------|-------------|---------------------------|
| page_view         | event1      |                           |
| video_start       | event50     |                           |
| video_complete    | event51     |                           |
| video_milestone   | event52     | 25/50/75% markers         |
| link_click        | event10     | Custom link tracking      |

## Known Issues
- v75 sometimes receives truncated URLs on AMP pages
- event52 milestone percentage sent in eVar33 as string "25","50","75"
```

---

## Go Architecture

```
specwatch/
├── cmd/
│   └── specwatch/
│       └── main.go              # CLI entry point
├── internal/
│   ├── spec/
│   │   ├── loader.go            # Markdown spec parser
│   │   ├── event.go             # Event spec model
│   │   ├── dimension.go         # Dimension definitions
│   │   ├── enum.go              # Enum value sets
│   │   ├── mapping.go           # Platform/RSID mappings
│   │   └── package.go           # Platform package configs
│   ├── proxy/
│   │   ├── server.go            # HTTPS proxy server
│   │   ├── cert.go              # Local CA cert generation
│   │   └── intercept.go         # Request interception logic
│   ├── har/
│   │   ├── parser.go            # HAR file ingestion
│   │   └── models.go            # HAR JSON structures
│   ├── parsers/
│   │   ├── registry.go          # Parser registry/detection
│   │   ├── adobe_appmeas.go     # AppMeasurement beacon parser
│   │   ├── adobe_websdk.go      # Web SDK / XDM parser
│   │   ├── adobe_launch.go      # Launch / direct call rules
│   │   ├── ga4.go               # GA4 collect endpoint parser
│   │   ├── tealium.go           # Tealium iQ / EventStream
│   │   └── snowplow.go          # Snowplow tracker protocol
│   ├── validator/
│   │   ├── engine.go            # Core validation logic
│   │   ├── rules.go             # Rule types (regex, enum, required, type)
│   │   ├── results.go           # Validation result models
│   │   └── reporter.go          # Output formatting
│   └── ui/
│       ├── terminal.go          # Color-coded CLI output
│       ├── web.go               # Local web dashboard (localhost)
│       └── json.go              # JSON output for CI/CD
├── pkg/
│   └── specformat/
│       └── schema.go            # Public spec format definitions
├── testdata/
│   ├── sample.har               # Test HAR files
│   └── specs/                   # Example spec directories
├── go.mod
├── go.sum
├── Makefile                     # Cross-compile targets
└── README.md
```

---

## CLI Interface

```bash
# Live proxy mode
specwatch proxy --spec ./specs --port 8888

# HAR analysis mode
specwatch har --spec ./specs --input capture.har

# HAR analysis with specific mapping context
specwatch har --spec ./specs --input capture.har --mapping fox_news

# Validate a single beacon URL (useful for testing)
specwatch validate --spec ./specs --beacon "https://foxnews.112.2o7.net/b/ss/foxnewsglobal/1/..."

# Output formats
specwatch har --spec ./specs --input capture.har --format json
specwatch har --spec ./specs --input capture.har --format html
specwatch har --spec ./specs --input capture.har --format terminal  # default

# Show spec summary
specwatch spec --spec ./specs --summary

# Diff two specs (useful for migration planning)
specwatch diff --spec-a ./specs/mappings/fox_news.md --spec-b ./specs/mappings/fox_corp.md

# Generate spec template from live scan (reverse engineering)
specwatch scan --url https://foxnews.com --output ./specs/discovered/

# Web dashboard mode (persistent local UI)
specwatch dashboard --spec ./specs --port 9090
```

---

## Validation Output Example (Terminal)

```
SpecWatch v0.1.0 — Validating against: fox_news mapping
Source: capture.har (247 analytics calls detected)

═══════════════════════════════════════════════════════
 PAGE_VIEW — foxnews.com/politics/article-123
═══════════════════════════════════════════════════════
 ✓ RSID          foxnewsglobal (matches fox_news mapping)
 ✓ page_url      v75 = "https://foxnews.com/politics/article-123"
 ✓ page_type     v3 = "article" (valid enum)
 ✓ content_id    v18 = "article-123"
 ✓ site_section  v4 = "politics" (valid enum)
 ✓ author        v22 = "Jane Smith"
 ✓ events        event1 (required for page_view)
 ✗ page_title    MISSING — required dimension not found
 ⚠ publish_date  NOT SET — optional, but recommended

 Result: FAIL (1 error, 1 warning)

═══════════════════════════════════════════════════════
 VIDEO_START — foxnews.com/video/player-embed
═══════════════════════════════════════════════════════
 ✓ RSID          foxnewsglobal
 ✓ video_id      v30 = "vid-98765"
 ✓ video_name    v31 = "Breaking News Segment"
 ✓ player_name   v32 = "foxplayer-v3"
 ✗ events        MISSING event50 — required for video_start
 ✗ page_url      v75 = "" — fails regex ^https?://
 ⚠ UNKNOWN       v99 = "test123" — not in spec, possible debug value

 Result: FAIL (2 errors, 1 warning)

═══════════════════════════════════════════════════════
 SUMMARY
═══════════════════════════════════════════════════════
 Total calls:    247
 Matched specs:  198 (80.2%)
 Unmatched:      49 (19.8%) — no matching event spec

 Passed:         142 (71.7%)
 Failed:         56 (28.3%)

 Top issues:
  1. page_title missing          — 23 occurrences
  2. event50 missing on video    — 12 occurrences
  3. empty page_url              — 8 occurrences
  4. unknown eVars detected      — 15 occurrences

 Full report: ./specwatch-report.json
```

---

## Build & Release Phases

### Phase 1: Core Engine
- [ ] Markdown spec parser (events, dimensions, enums)
- [ ] Adobe AppMeasurement beacon parser
- [ ] HAR file ingestion
- [ ] Basic validation engine (required, regex, enum)
- [ ] Terminal output with color coding
- [ ] CLI framework with `har` and `validate` commands

**Milestone:** Can ingest a HAR, parse Adobe beacons, validate against MD spec, output results.

### Phase 2: Multi-Platform Parsers
- [ ] GA4 parser
- [ ] Adobe Web SDK / XDM parser
- [ ] Tealium parser
- [ ] Platform mapping files (RSID, eVar <-> canonical name translation)
- [ ] Mapping context flag (`--mapping fox_news`)
- [ ] JSON output format for CI/CD

**Milestone:** Validates Adobe (all variants) and GA4 against same canonical spec with platform-specific mappings.

### Phase 3: Live Proxy
- [ ] HTTPS proxy server with local CA cert generation
- [ ] Real-time interception and validation
- [ ] Terminal streaming output
- [ ] Certificate trust instructions per platform (Mac, Linux, iOS sim, Android emu)
- [ ] Proxy mode CLI command

**Milestone:** Dev runs `specwatch proxy`, points emulator at it, sees real-time validation.

### Phase 4: Reverse Engineering & Diff
- [ ] `scan` command — headless browser hits URL, captures all beacons, generates spec draft
- [ ] `diff` command — compare two mapping files side by side
- [ ] Spec template generation from discovered beacons
- [ ] Unknown/undocumented dimension detection and flagging

**Milestone:** Can scan a site and auto-generate a draft spec from live traffic.

### Phase 5: Dashboard & Polish
- [ ] Local web dashboard (localhost:9090)
- [ ] Historical validation runs with trend tracking
- [ ] HTML report export
- [ ] Cross-compilation and release binaries (Mac ARM, Mac Intel, Linux AMD64)
- [ ] README, docs, example specs

**Milestone:** Ship v0.1.0 — fully functional cross-platform binary.

### Phase 6: Product Features (Post-launch)
- [ ] Team spec management (Git-native workflow)
- [ ] Anomaly detection (event volume / dimension fill rate changes)
- [ ] Snowflake/BigQuery integration for server-side validation
- [ ] Slack/email alerting on spec drift
- [ ] SaaS dashboard for non-technical stakeholders

---

## Key Design Decisions

1. **Markdown-native specs** — No proprietary format. Specs live in Git, editable in Obsidian/VSCode/any editor. Portable between projects.

2. **Canonical event model** — Events are defined once in platform-agnostic terms. Platform-specific mappings translate to/from eVars, XDM paths, GA4 parameters. One source of truth, multiple outputs.

3. **Single binary, zero dependencies** — Go compiles to one file. No runtime, no Docker, no node_modules. Dev downloads, runs, done.

4. **HAR-first design** — Proxy is a convenience layer. The core engine works on parsed network data. This means any capture method works: Charles export, browser DevTools, Playwright HAR capture, mitmproxy dumps.

5. **Fail-open on unknowns** — Unrecognized events or dimensions are flagged as warnings, not errors. This prevents the tool from blocking dev work on new features before the spec is updated.

6. **Git-native workflow** — Spec changes are PRs. Validation runs can be triggered in CI against the spec in the repo. Spec drift detection compares live traffic against the committed spec.

---

## Competitive Landscape

| Tool             | Spec-Driven | Multi-Platform | Local/Free | HAR Support | CI/CD |
|-----------------|-------------|----------------|------------|-------------|-------|
| ObservePoint    | No          | Yes            | No (SaaS)  | No          | No    |
| Adobe Debugger  | No          | Adobe only     | Yes        | No          | No    |
| GA4 DebugView   | No          | GA4 only       | Yes        | No          | No    |
| Charles Proxy   | No          | Raw traffic    | Paid       | Export only | No    |
| Snowplow Micro  | Partial     | Snowplow only  | Yes        | No          | Yes   |
| **SpecWatch**   | **Yes**     | **Yes**        | **Yes**    | **Yes**     | **Yes** |

---

## Implementation Notes

When starting Phase 1, prioritize:
1. The Markdown parser — this is the foundation. Get the table parsing right for dimensions, the `@enums/` reference resolution, and the platform override sections.
2. Adobe AppMeasurement parser — most complex beacon format and covers the primary use case.
3. HAR parser — standard JSON format, straightforward.
4. Wire them together with the validation engine.

The spec format is a proposal. Iterate on it as edge cases are discovered in real specs. The format should serve the workflow, not the other way around.

## Existing Assets in This Repo

- `.har` and `.chls` files — Real analytics captures from Fox News, Fire TV, Roku, Samsung TV, etc. Use these as test fixtures.
- `harmony.py` / `helper_functions.py` — Original Python HAR parsing logic. Reference for beacon detection patterns.
- `test_cases.xlsx` / `test_groups.json` — Existing test case definitions that can inform spec structure.
- `frontend/` / `backend/` — Previous web UI. May inform dashboard design in Phase 5.
