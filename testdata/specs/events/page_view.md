# page_view

Test page view event.

## Required Dimensions

| Dimension       | Type     | Validation              | Notes          |
|----------------|----------|-------------------------|----------------|
| page_url       | string   | `^https?://`            | Full URL       |
| page_type      | enum     | @enums/page_types       | Content type   |

## Optional Dimensions

| Dimension       | Type     | Validation              | Notes          |
|----------------|----------|-------------------------|----------------|
| author         | string   | `.+`                    | Author name    |

## Platform Overrides

### adobe_appmeasurement
- `page_url` → `eVar75`
- `page_type` → `eVar3`
- Requires: `events=event1`
