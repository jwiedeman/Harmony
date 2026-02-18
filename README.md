# SpecWatch

Spec-driven analytics validation engine. Validates Adobe Analytics, GA4, and other analytics beacons against markdown-native measurement specs.

## Quick Start

```bash
# Build
make build

# Validate a HAR file against a spec
./specwatch har --spec ./specs --input capture.har --mapping fox_news

# JSON output for CI/CD
./specwatch har --spec ./specs --input capture.har --mapping fox_news --format json
```

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

## Build

Requires Go 1.22+.

```bash
make build          # Build binary
make test           # Run tests
make test-cover     # Tests with coverage report
make cross-compile  # Darwin arm64/amd64, Linux amd64
```

## Operating Modes

- **HAR Analysis** (Phase 1 - implemented): Parse HAR files, validate beacons against spec
- **Live Proxy** (Phase 3 - planned): Intercept HTTPS traffic in real time
- **CI/CD** (Phase 2 - planned): JSON output with exit codes for build systems
