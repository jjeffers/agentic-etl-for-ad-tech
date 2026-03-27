# AdNetwork X - Reporting API v2

## Publisher Supply Performance Endpoint

Fetch aggregated reporting for Publisher Yield.

**Endpoint:** `https://api.adnetworkx.com/v2/yield/publisher`
**Method:** `GET`

### Response Data Fields
- `pub_id`: (Integer) The publisher identifier.
- `reqs`: (Integer) Count of ad requests.
- `imps`: (Integer) Count of successful ad impressions.
- `rev`: (Float) Total publisher revenue in USD.
- `operating_system`: (String) The operating system of the requesting user.
- `viewer_ip`: (String) The IPv4 address of the end user viewing the advertisement.
