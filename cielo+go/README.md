# Cielo Finance Scraper - Go Implementation

This is an experimental Go implementation of the Cielo Finance leaderboard scraper, focusing on high performance and modern HTTP features.

## Features

- HTTP/3 support
- JA3 fingerprint customization
- TLS configuration
- High-performance networking
- Custom header management

## Project Structure

```
cielo+go/
├── main.go   # Main application logic
├── go.mod    # Go module definition
└── go.sum    # Module dependency checksums
```

## Setup

1. Install Go (1.21 or later recommended)

2. Install dependencies:
```bash
go mod download
```

## Configuration

The application uses the following configurable parameters in `main.go`:

```go
clientOptions := requests.ClientOption{
    H3:                    true,
    Ja3:                   true,
    ForceHttp1:            false,
    DisCookie:             false,
    DisDecode:             false,
    DisUnZip:              false,
    DisAlive:              false,
    Timeout:               30 * time.Second,
    ResponseHeaderTimeout: 15 * time.Second,
    TlsHandshakeTimeout:   10 * time.Second,
    KeepAlive:             10 * time.Second,
}
```

## Running the Application

```bash
go run main.go
```

## Network Features

- HTTP/3 protocol support
- Custom TLS configuration
- JA3 fingerprint manipulation
- Connection pooling
- Keep-alive connections
- Custom timeout settings

## Error Handling

- TLS error management
- Network timeout handling
- Response validation
- Header inspection

## Future Improvements

1. Database integration
2. Multi-threaded page fetching
3. Rate limit handling
4. Token auto-renewal
5. CSV export functionality

## Performance Considerations

- Uses HTTP/3 for improved performance
- Custom TLS configuration for security
- Efficient header handling
- Response body management
- Connection pooling
