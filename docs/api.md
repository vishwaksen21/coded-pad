# API Reference — Coded Pad

## Endpoints

### `GET /api/health`
Health and diagnostics endpoint for uptime monitors.

#### Response `200 OK`
```json
{
  "status": "ok",
  "database": "sqlite",
  "timestamp": "2026-10-31 12:00:00 UTC"
}
```

### Error Responses
- `400 Bad Request`: Missing or invalid secret code.
- `413 Payload Too Large`: Note exceeds 500,000 characters.
- `500 Internal Server Error`: Unexpected database persistence issue.

### `POST /api/save`
Save encrypted note.

#### Request Body
```json
{
  "secret_code": "my-secret-key",
  "note": "Encrypted text content"
}
```

## Client Usage Example (JavaScript)

```javascript
const res = await fetch('/api/save', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ secret_code: 'my-code', note: 'Secret content' })
});
const data = await res.json();
console.log(data);
```
