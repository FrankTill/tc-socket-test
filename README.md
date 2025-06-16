# Terminal WebSocket Client

A Python-based Socket.IO client for load testing and monitoring terminal gateway connections. This tool connects multiple terminals to a WebSocket server and maintains persistent connections with real-time status monitoring.

## Features

- **Multi-terminal support**: Connect multiple terminals simultaneously from CSV configuration
- **Real-time monitoring**: Track connection status and active terminals
- **Automatic reconnection**: Handles connection drops with retry logic
- **Secure connections**: SSL/TLS support with certificate verification
- **Load testing**: Simulate multiple terminal connections for testing purposes
- **Clean logging**: Structured logs with MID/TID identification and token masking

## Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

## Installation

1. **Clone or download the project files**

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### 1. Environment Variables (.env file)

Create a `.env` file in the project root with the following variables:

```env
TOKEN=your_authentication_token_here
LOG_LEVEL=INFO
```

- `TOKEN`: Authentication token for the WebSocket server (required)
- `LOG_LEVEL`: Logging level (optional, default: INFO). Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

**Tip**: Copy `.env.example` to `.env` and update the values:
```bash
cp .env.example .env
```

### 2. Terminal Configuration (terminals.csv)

Create a `terminals.csv` file with your terminal configurations:

```csv
mid,tid
mid1,test-mid1
mid2,test-mid2
mid2,test-mid2-2
```

- `mid`: Merchant ID
- `tid`: Terminal ID

## Usage

### Basic Usage

```bash
python websocket_client.py
```

### What the script does:

1. **Reads configuration** from `.env` and `terminals.csv`
2. **Establishes connections** to the WebSocket server for each terminal
3. **Maintains connections** with automatic ping/pong handling
4. **Logs activity** including connection status and events
5. **Handles reconnections** automatically if connections drop

### Sample Output

```
2025-06-16 10:03:50,680 - INFO - Starting Socket.IO clients for 3 terminals...
2025-06-16 10:03:50,681 - INFO - [MID:mid1 TID:test-mid1] Connecting to wss://api-terminal-gateway.tillpayments.dev/socket.io/?tid=test-mid1&mid=mid1&token=*** (attempt 1)...
2025-06-16 10:03:50,682 - INFO - [MID:mid2 TID:test-mid2] Connecting to wss://api-terminal-gateway.tillpayments.dev/socket.io/?tid=test-mid2&mid=mid2&token=*** (attempt 1)...
2025-06-16 10:03:51,829 - INFO - [MID:mid1 TID:test-mid1] Connected to server
2025-06-16 10:03:51,830 - INFO - Connected terminals: [['mid1', 'test-mid1']] (Total: 1)
2025-06-16 10:03:51,912 - INFO - [MID:mid2 TID:test-mid2] Connected to server
2025-06-16 10:03:51,913 - INFO - Connected terminals: [['mid1', 'test-mid1'], ['mid2', 'test-mid2']] (Total: 2)
2025-06-16 10:04:16,832 - INFO - STATUS: 2 terminals connected: [['mid1', 'test-mid1'], ['mid2', 'test-mid2']]
```

## Project Structure

```
tc-socket-test/
├── websocket_client.py    # Main client application
├── terminals.csv          # Terminal configuration
├── .env                   # Environment variables (create from .env.example)
├── .env.example          # Environment variables template
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── venv/                 # Virtual environment (created after setup)
```

## Features Explained

### Connection Management
- **Automatic SSL handling**: Uses system certificates for secure connections
- **Retry logic**: 3 connection attempts with 5-second delays
- **Graceful disconnection**: Proper cleanup on exit

### Monitoring
- **Real-time status**: Shows connected terminals every 25 seconds
- **Event logging**: Captures all server events and messages
- **Connection tracking**: Maintains list of active connections

### Security
- **Token masking**: Sensitive tokens are hidden in logs as `***`
- **SSL verification**: Secure connections with certificate validation

## Troubleshooting

### SSL Certificate Issues
If you encounter SSL certificate errors on macOS:
```bash
/Applications/Python\ 3.12/Install\ Certificates.command
```

### Connection Failures
- Verify your `TOKEN` is correct and not expired
- Check that the server endpoint is accessible
- Ensure your network allows WebSocket connections on port 443

### CSV Format Issues
- Ensure `terminals.csv` has proper headers: `mid,tid`
- Check for extra spaces or special characters
- Verify file encoding is UTF-8

## Dependencies

- `python-socketio[asyncio_client]`: Socket.IO client library
- `aiohttp`: Async HTTP client for WebSocket connections
- `pandas`: CSV file processing
- `python-dotenv`: Environment variable management
- `certifi`: SSL certificate bundle

## Development

### Adding New Features
The main client class is `TerminalSocketIOClient` in `websocket_client.py`. Key methods:
- `_register_handlers()`: Define event handlers
- `connect()`: Connection logic with retry
- `custom_ping_loop()`: Custom ping functionality

### Logging Configuration
Logging level is configured via the `LOG_LEVEL` environment variable in your `.env` file:
```env
LOG_LEVEL=DEBUG  # For verbose debugging
LOG_LEVEL=INFO   # For normal operation (default)
LOG_LEVEL=ERROR  # For errors only
```

## License

This project is for internal use and testing purposes.

## Support

For issues or questions, please check:
1. Your `.env` configuration
2. Terminal CSV format
3. Network connectivity
4. SSL certificate installation (macOS) 