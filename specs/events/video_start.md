# video_start

Fired when a video begins playback.

## Required Dimensions

| Dimension       | Type     | Validation              | Notes                    |
|----------------|----------|-------------------------|--------------------------|
| video_id       | string   | `^[a-zA-Z0-9\-]+$`     | Video asset identifier   |
| video_name     | string   | `.{1,255}`              | Video title              |
| player_name    | string   | `.+`                    | Player identifier        |
| page_url       | string   | `^https?://`            | Page hosting the video   |

## Optional Dimensions

| Dimension       | Type     | Validation              | Notes                    |
|----------------|----------|-------------------------|--------------------------|
| content_id     | string   | `^[a-zA-Z0-9\-]+$`     | Parent content ID        |

## Platform Overrides

### adobe_appmeasurement
- `video_id` → `eVar30`
- `video_name` → `eVar31`
- `player_name` → `eVar32`
- Requires: `events=event50`
