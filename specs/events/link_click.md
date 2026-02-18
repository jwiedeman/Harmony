# link_click

Custom link tracking event for user interactions.

## Required Dimensions

| Dimension       | Type     | Validation              | Notes                    |
|----------------|----------|-------------------------|--------------------------|
| link_name      | string   | `.+`                    | Link text or identifier  |
| page_url       | string   | `^https?://`            | Page where click occurred|

## Optional Dimensions

| Dimension       | Type     | Validation              | Notes                    |
|----------------|----------|-------------------------|--------------------------|
| link_url       | string   | `^https?://`            | Destination URL          |
| link_region    | string   | `.+`                    | Page region              |
| site_section   | enum     | @enums/site_sections    | Section context          |

## Platform Overrides

### adobe_appmeasurement
- `link_name` → `pev2`
- Requires: `events=event10`
