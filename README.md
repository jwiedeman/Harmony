# SpecWatch

Spec-driven analytics validation engine. Validates Adobe Analytics, GA4, and other analytics beacons against markdown-native measurement specs.

Single binary, zero dependencies, markdown-native specs that live in Git.

## Install

```bash
# From source
go install github.com/jwiedeman/specwatch/cmd/specwatch@latest

# Or clone and build
git clone https://github.com/jwiedeman/Harmony.git
cd Harmony
make build
```

## Quick Start

```bash
# Validate a HAR file
./specwatch har --spec ./specs --input ./testdata/adobe_test.har --mapping fox_news

# Validate a single beacon URL (paste from browser DevTools)
./specwatch validate --spec ./specs --mapping fox_news \
  --beacon "https://foxnews.112.2o7.net/b/ss/foxnewsglobal/1/JS-2.22.0/s1234?events=event1&v75=https://foxnews.com&v3=article"

# See what specs are loaded
./specwatch spec --spec ./specs

# JSON output for CI/CD
./specwatch har --spec ./specs --input capture.har --mapping fox_news --format json
```

Exit code 1 when validation failures are found (CI/CD friendly).

## Spec Format

Specs are plain Markdown files organized by convention:

```
specs/
├── _global/
│   ├── enums.md          # Allowed value enumerations
│   └── dimensions.md     # Master dimension reference
├── events/
│   ├── page_view.md      # Event definitions with required/optional dimensions
│   ├── video_start.md
│   └── link_click.md
├── packages/
│   └── adobe_appmeasurement.md  # Platform beacon format
└── mappings/
    └── fox_news.md        # Property-specific eVar/event mappings
```

Mapping names are derived from filenames (e.g. `fox_news.md` -> `--mapping fox_news`).

## Commands

| Command | Description |
|---------|-------------|
| `specwatch har` | Validate analytics beacons in a HAR file |
| `specwatch validate` | Validate a single beacon URL |
| `specwatch spec` | Inspect and summarize a spec directory |

## Build

Requires Go 1.21+.

```bash
make build          # Build binary
make test           # Run tests
make test-cover     # Tests with coverage report
make cross-compile  # Darwin arm64/amd64, Linux amd64
```

## Currently Supported

- **Adobe AppMeasurement** (`/b/ss/` beacons) — eVars, props, events, RSID validation, multi-suite tagging
- HAR file ingestion (browser DevTools, Charles Proxy export, Playwright)
- Markdown spec parsing with enum validation, regex rules, platform overrides

## Roadmap

- GA4, Adobe Web SDK, Tealium parsers
- HTTPS proxy for live capture
- Spec diff and reverse engineering from live traffic
- Local web dashboard
