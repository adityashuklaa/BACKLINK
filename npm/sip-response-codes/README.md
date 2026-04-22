# sip-response-codes

Complete reference for SIP (RFC 3261 and extensions) response codes, with structured metadata for every 1xx/2xx/3xx/4xx/5xx/6xx response.

Zero dependencies, TypeScript types included, frozen dataset.

```bash
npm install sip-response-codes
```

## Why this exists

Every SIP stack has its own internal table of response codes. Application code on top of SIP libraries (SBCs, dialer software, billing systems, monitoring, test suites) keeps reinventing the same lookup. This package is that lookup, done once, with citations against the actual RFC sections.

We use this internally at [DialPhone](https://dialphone.com) for call-quality monitoring and SIP trunk health checks. Publishing the data module so other telephony developers don't have to rewrite it.

## Usage

```js
const { getCode, isError, isRetryable, byClass } = require('sip-response-codes');

getCode(486);
// {
//   code: 486,
//   name: 'Busy Here',
//   class: 'client_error',
//   retryable: true,
//   rfc: 'RFC 3261 §21.4.24',
//   description: "Callee is busy at this location; try another."
// }

isError(486);      // true
isError(200);      // false
isRetryable(486);  // true
isRetryable(403);  // false

byClass('server_error').map(c => c.code);
// [ 500, 501, 502, 503, 504, 505, 513, 555, 580 ]
```

### TypeScript

```ts
import { getCode, SipResponseCode, SipResponseClass } from 'sip-response-codes';

const entry: SipResponseCode | null = getCode(603);
if (entry) {
  console.log(entry.class); // "global_error"
  console.log(entry.rfc);   // "RFC 3261 §21.6.2"
}
```

## API

### `codes`
Frozen object mapping numeric code → entry. Use when you need the whole dataset.

### `getCode(code)`
Returns the entry for a numeric or string code, or `null` for unknown codes.

### `getClass(code)`
Returns one of `"provisional"`, `"success"`, `"redirection"`, `"client_error"`, `"server_error"`, `"global_error"`, or `null`.

### Class predicates
- `isProvisional(code)` — 1xx
- `isSuccess(code)` — 2xx
- `isRedirect(code)` — 3xx
- `isClientError(code)` — 4xx
- `isServerError(code)` — 5xx
- `isGlobalError(code)` — 6xx
- `isError(code)` — any of 4xx/5xx/6xx

### `isRetryable(code)`
Returns whether our dataset flags the code as retryable. Retry semantics vary by code and by context (registration retry vs dialog retry vs INVITE retry). Always consult the RFC linked in the entry before implementing retry logic.

### `byClass(className)`
Returns every entry whose `class` equals `className`.

### `allCodes`
Array of all numeric codes, ascending.

### `allEntries`
Array of all entries.

## What's covered

SIP codes defined across the following RFCs:

| RFC | Topic |
|-----|-------|
| RFC 3261 | Base SIP (most 4xx/5xx/6xx codes) |
| RFC 3265 / 6665 | Event notification |
| RFC 3312 | Preconditions |
| RFC 3329 | Security agreements |
| RFC 3892 | REFER referred-by |
| RFC 3903 | PUBLISH method |
| RFC 4028 | Session timers |
| RFC 4412 | Resource priority |
| RFC 4474 / 8224 | SIP identity |
| RFC 5079 | Anonymity disallowed |
| RFC 5360 | Consent-based communications |
| RFC 5393 | Max-Breadth |
| RFC 5626 | Outbound / flow failure |
| RFC 5839 | No notification |
| RFC 6086 | INFO method |
| RFC 6228 | 199 Early Dialog Terminated |
| RFC 6442 | Location conveyance |
| RFC 8197 | 607 Unwanted |
| RFC 8599 | SIP push notification service |
| RFC 8688 | 608 Rejected (anti-abuse) |

If a code is missing, open an issue with the RFC reference and we'll add it.

## Size

- Source: one data file (~70 entries), one index file. Under 20 KB unpacked, no dependencies.

## Tests

```bash
npm test
```

## Contributing

PRs welcome. New entries must cite the RFC section. Data-only changes only — this package intentionally doesn't do any parsing, retry orchestration, or SIP stack work; it's a reference dataset.

## License

MIT

## Credits

Maintained by the VoIP operations team at [DialPhone Limited](https://dialphone.com), a UK business phone provider. We built this library for internal SIP trunk monitoring and published it because it was useful to us and might be useful to you.
