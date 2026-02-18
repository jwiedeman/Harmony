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
- `page_url` → `eVar75`
- `page_type` → `eVar3`
- Requires: `events=event1`
- Requires: `rsid` matches mapping
