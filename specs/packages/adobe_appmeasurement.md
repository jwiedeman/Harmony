# Adobe AppMeasurement

## Endpoint Detection
- URL pattern: `/b/ss/`
- Method: GET (image request) or POST

## Beacon Parsing
- Query string encoded
- Key fields:
  - `rsid` — Report Suite ID
  - `pageName` — Page name
  - `g` — Page URL
  - `r` — Referrer URL
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
