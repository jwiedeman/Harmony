# Master Dimension Reference

All canonical dimension names used across event specs.

| Dimension       | Type     | Description                        |
|----------------|----------|------------------------------------|
| page_url       | string   | Full page URL including query      |
| page_title     | string   | HTML page title                    |
| page_type      | enum     | Content type classification        |
| content_id     | string   | CMS content identifier             |
| site_section   | enum     | Primary navigation section         |
| author         | string   | Content author name                |
| publish_date   | datetime | Original publish date (ISO8601)    |
| tags           | array    | Content tags                       |
| video_id       | string   | Video asset identifier             |
| video_name     | string   | Video title/name                   |
| player_name    | string   | Video player identifier            |
| link_url       | string   | Destination URL for link clicks    |
| link_name      | string   | Link text or identifier            |
| link_region    | string   | Page region where link appears     |
