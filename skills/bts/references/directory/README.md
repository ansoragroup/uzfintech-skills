# BTS directory (`directory/regions`, `directory/cities`, `directory/branches`, `status/index`)

Hand-written notes. Transport, auth and errors: [`../common/README.md`](../common/README.md).
Schemas: [`schemas/`](schemas/). Examples: [`examples/`](examples/).

- Source: https://docs.bts.uz/page/directory-regions, https://docs.bts.uz/page/directory-cities,
  https://docs.bts.uz/page/directory-branches, https://docs.bts.uz/page/status
- Fetched: 2026-11-06

## Flow

```
GET /v1/directory/regions                         -> data.items[{code, name}]
GET /v1/directory/cities?regionCode=70            -> data.items[{code "7001", name, regionCode}]
GET /v1/directory/branches?regionCode=70&cityCode=7001
                                                  -> data.items[{code "7017", address, lat_long, working_hours, ...}]
GET /v1/status/index                              -> data.items[{code, name, description, next_possible_statuses}]
```

## Rules

- Codes are strings; keep leading digits as given. The city code goes into the quote
  (`senderCityCode`, `receiverCityCode`) and into `order/add` (`city_code`); the branch
  code into `branch_code`.
- Cache the directory (it changes rarely) and refresh it daily or on a miss.
- Branch `lat_long` is one string `"lat,long"`; split it yourself.
- `working_hours` keys are `"1"` (Monday) to `"7"` (Sunday); `null` means closed.
- A production client also reads `office_exists`; the page does not show it.
- Replies wrap the list in `data.items`; accept a bare array too.
- Codes 900 and 1000 are missing from `status/index` (`bts.undocumented-codes`).
