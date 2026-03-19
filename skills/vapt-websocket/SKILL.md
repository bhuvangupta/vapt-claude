# WebSocket Security Testing

## When Invoked

The user runs `/vapt websocket <url>` for WebSocket-specific security testing.

## Phase 1: WebSocket Discovery

### 1.1 Endpoint Detection

```bash
# Check for WebSocket upgrade support
curl -sI -H "Upgrade: websocket" -H "Connection: Upgrade" \
    -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
    -H "Sec-WebSocket-Version: 13" <url>

# Common WebSocket paths
for path in /ws /wss /websocket /socket /socket.io /sockjs /cable /hub /realtime /live /stream /events; do
    code=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Upgrade: websocket" -H "Connection: Upgrade" \
        -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
        -H "Sec-WebSocket-Version: 13" <url>$path)
    [ "$code" = "101" ] && echo "WebSocket: $path (101 Switching Protocols)"
    [ "$code" = "200" ] && echo "Socket.IO/SockJS candidate: $path (200)"
done
```

### 1.2 Protocol Detection

Identify the WebSocket framework:
- Raw WebSocket (ws://)
- Socket.IO (transport negotiation, JSON-wrapped messages)
- SockJS (HTTP fallback, iframe transport)
- ActionCable (Rails WebSocket)
- SignalR (.NET real-time)

### 1.3 Transport Analysis

```bash
# Check if Socket.IO is in use
curl -s "<url>/socket.io/?EIO=4&transport=polling"

# Check SockJS
curl -s "<url>/sockjs/info"
```

## Phase 2: Authentication & Authorization

### 2.1 Unauthenticated Connection

Attempt to establish a WebSocket connection without any authentication:

```python
# Python test script (using websockets library if available)
# Alternatively describe the manual test with websocat or wscat
```

Using `websocat` (if installed):
```bash
echo '{"type":"ping"}' | websocat ws://<domain>/ws
```

Using `wscat` (if installed):
```bash
wscat -c ws://<domain>/ws
```

If connection succeeds without auth -> finding.

### 2.2 Token Validation

Test if the WebSocket validates tokens after initial connection:
1. Connect with valid token
2. Wait for token expiration
3. Check if messages still flow (should be disconnected)

### 2.3 Origin Validation

```bash
# Connect with spoofed Origin header
curl -sI -H "Upgrade: websocket" -H "Connection: Upgrade" \
    -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
    -H "Sec-WebSocket-Version: 13" \
    -H "Origin: https://evil.com" <url>/ws
```

If 101 is returned with a foreign origin -> Cross-Site WebSocket Hijacking (CSWSH) possible.

### 2.4 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| No authentication on WebSocket | High | 7.5 |
| Cross-Site WebSocket Hijacking | High | 8.1 |
| Token not validated after expiration | Medium | 5.5 |
| Missing Origin validation | Medium | 6.5 |

## Phase 3: Message Security

### 3.1 Message Interception

Analyze WebSocket messages for:
- Sensitive data in plaintext (credentials, tokens, PII)
- Session identifiers
- Internal system information
- Debug/verbose messages

### 3.2 Message Injection

Test if the server validates message structure:
- Send malformed JSON/messages
- Send oversized messages
- Send unexpected message types
- Inject SQL/NoSQL payloads in message fields
- Inject XSS payloads (if messages render in other clients)

### 3.3 Message Replay

1. Capture a valid message (e.g., a transfer or action)
2. Replay the exact same message
3. Check if the server processes it again

### 3.4 Rate Limiting

Send rapid messages to check for server-side throttling:
- Flood with valid messages
- Flood with invalid messages
- Check if client gets disconnected or rate-limited

### 3.5 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Sensitive data in WebSocket messages | Medium | 5.0 |
| SQL injection via WebSocket message | Critical | 9.8 |
| XSS via WebSocket message (stored) | High | 8.1 |
| Message replay accepted | Medium | 5.5 |
| No message rate limiting | Medium | 4.5 |

## Phase 4: Encryption & Transport

### 4.1 WSS vs WS

Check if WebSocket uses secure transport:
- `wss://` (encrypted) -> Good
- `ws://` (plaintext) -> Finding

### 4.2 Mixed Content

If the main page is HTTPS but WebSocket connects via ws:// -> Mixed content vulnerability.

### 4.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| ws:// used instead of wss:// | Medium | 5.9 |
| Mixed content (HTTPS page, WS connection) | Medium | 4.5 |

## Phase 5: Denial of Service

### 5.1 Connection Flooding

Test server behavior under many simultaneous connections:
- Open 50+ concurrent WebSocket connections
- Check if server degrades or crashes
- Check if there's a per-IP connection limit

### 5.2 Slowloris-Style Attack

Open a WebSocket connection and send data very slowly:
- Send partial frames
- Keep connection alive without completing handshake

### 5.3 Large Frame Attack

Send extremely large WebSocket frames:
- 10MB+ single message
- Fragmented frames with total size exceeding limits

### 5.4 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| No connection limit per IP | Medium | 5.3 |
| Large frame accepted (no size limit) | Low | 3.5 |
| Slow connection not timed out | Low | 3.0 |

## Phase 6: Output

### Terminal Output

**Dev mode:** Explain WebSocket security model, how CSWSH works, why Origin checking matters, difference between ws:// and wss://.

**Pro mode:** Connection analysis + findings table.

### VAPT-WEBSOCKET.md

```markdown
# VAPT WebSocket Security Report

## Target: <url>
## Endpoint: <ws_path>
## Protocol: <ws/wss>
## Framework: <detected framework>
## Date: <timestamp>

## Connection Security
| Check | Status |
|-------|--------|
| Transport (wss://) | ... |
| Authentication required | ... |
| Origin validation | ... |
| Token expiration check | ... |

## Message Security
| Check | Status |
|-------|--------|
| Sensitive data exposure | ... |
| Input validation | ... |
| Injection vulnerabilities | ... |
| Replay protection | ... |
| Rate limiting | ... |

## DoS Resistance
| Check | Status |
|-------|--------|
| Connection limits | ... |
| Frame size limits | ... |
| Timeout on slow connections | ... |

## Findings
<scored findings with CVSS>

## Suggested Next Steps
- /vapt auth <url> -- test authentication mechanisms
- /vapt inject <url> -- test HTTP endpoints for injections
- /vapt report <url> -- compile full report
```

## Cross-Skill Integration

- WebSocket findings contribute to the authentication and API categories in Security Posture Score
- Injection findings via WebSocket count toward injection category
- Origin validation issues relate to vapt-headers CORS findings
