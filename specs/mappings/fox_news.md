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
| page_title        | v1    |       |                             |
| link_name         | v40   |       |                             |
| link_url          | v41   |       |                             |
| link_region       | v42   |       |                             |

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
