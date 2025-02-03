# Configuration Guide

This guide covers configuration options for all components of the Binance Futures WebSocket library.

## Default Configurations

Each service component comes with sensible defaults that work well for most use cases.

### WebSocket API Defaults

```python
WEBSOCKET_DEFAULTS = {
    'return_rate_limits': True,      # Return rate limit info in responses
    'connection_timeout': 30,        # Connection timeout in seconds
    'request_timeout': 30,           # Individual request timeout
    'ping_interval': 180,           # WebSocket ping interval
    'reconnect_delay': 5,           # Initial reconnection delay
    'max_reconnect_delay': 300,     # Maximum reconnection delay
    'max_reconnect_attempts': 5      # Maximum reconnection attempts
}
```

### User Data Stream Defaults

```python
USER_STREAM_DEFAULTS = {
    'connection_timeout': 30,
    'request_timeout': 30,
    'ping_interval': 3300,          # 55 minutes (listen key keepalive)
    'reconnect_delay': 5,
    'max_reconnect_delay': 300,
    'max_reconnect_attempts': 5,
    'health_check_interval': 60     # Stream health check interval
}
```

### Market Stream Defaults

```python
MARKET_STREAM_DEFAULTS = {
    'connection_timeout': 30,
    'request_timeout': 30,
    'ping_interval': 180,
    'reconnect_delay': 5,
    'max_reconnect_delay': 300,
    'max_reconnect_attempts': 5
}
```

## Customizing Configurations

You can override any default configuration when initializing services.

### WebSocket API Configuration

```python
from binance_futures_async import BinanceClient

async def main():
    client = BinanceClient()
    
    # Custom configuration
    config = {
        'return_rate_limits': False,     # Disable rate limit info
        'connection_timeout': 60,        # Longer timeout
        'request_timeout': 15,           # Shorter request timeout
        'ping_interval': 120             # More frequent pings
    }
    
    ws_service = await client.websocket_service(
        api_key='your_api_key',
        private_key_path='path/to/your/key',
        enable_validation=True,           # Enable order validation
        config=config
    )
```

### Market Streams Configuration

```python
# Custom market streams configuration
market_config = {
    'ping_interval': 300,            # Longer ping interval
    'max_reconnect_attempts': 10,    # More reconnection attempts
    'connection_timeout': 45         # Longer connection timeout
}

market_service = await client.market_service(
    message_handler=handle_market_data,
    config=market_config
)
```

### User Data Stream Configuration

```python
# Custom user stream configuration
user_config = {
    'health_check_interval': 30,     # More frequent health checks
    'ping_interval': 3000,           # More frequent listen key refresh
    'max_reconnect_attempts': 15     # More reconnection attempts
}

user_stream = await client.user_stream(
    api_key='your_api_key',
    message_handler=handle_user_data,
    config=user_config
)
```

## Configuration Parameters Explained

### Common Parameters

| Parameter | Description | Default | Use Case |
|-----------|-------------|---------|----------|
| `connection_timeout` | Maximum time to establish connection | 30s | Adjust for slower networks |
| `request_timeout` | Maximum time to wait for response | 30s | Balance between reliability and latency |
| `ping_interval` | Interval between ping messages | 180s | Keep connection alive |
| `reconnect_delay` | Initial wait time before reconnecting | 5s | Control reconnection behavior |
| `max_reconnect_delay` | Maximum wait time between attempts | 300s | Prevent aggressive reconnections |
| `max_reconnect_attempts` | Maximum number of reconnection tries | 5 | Control recovery behavior |

### WebSocket API Specific

| Parameter | Description | Default | Use Case |
|-----------|-------------|---------|----------|
| `return_rate_limits` | Include rate limit info in responses | True | Monitor API usage |
| `enable_validation` | Enable order parameter validation | False | Catch errors before sending |

### User Stream Specific

| Parameter | Description | Default | Use Case |
|-----------|-------------|---------|----------|
| `health_check_interval` | Interval for checking stream health | 60s | Ensure reliable streams |
| `ping_interval` | Listen key refresh interval | 3300s | Keep listen key active |

## Best Practices

### High-Performance Trading

For low-latency trading applications:
```python
config = {
    'return_rate_limits': False,    # Reduce response payload
    'request_timeout': 10,          # Fast timeout for HFT
    'connection_timeout': 15,       # Quick connection detection
    'ping_interval': 60            # Frequent connection checks
}
```

### Reliable Long-Running Systems

For stable, long-running applications:
```python
config = {
    'max_reconnect_attempts': 15,   # More reconnection attempts
    'health_check_interval': 30,    # Frequent health checks
    'connection_timeout': 60,       # Longer connection timeout
    'request_timeout': 45           # Longer request timeout
}
```

### Poor Network Conditions

For unreliable network environments:
```python
config = {
    'connection_timeout': 90,       # Longer connection timeout
    'request_timeout': 60,          # Longer request timeout
    'reconnect_delay': 10,         # Longer initial reconnect delay
    'max_reconnect_attempts': 20    # More reconnection attempts
}
```

## Order Validation

Enable order validation to catch common errors before sending to Binance:

```python
ws_service = await client.websocket_service(
    api_key='your_api_key',
    private_key_path='path/to/your/key',
    enable_validation=True          # Enable validation
)
```

This validates:
- Required parameters
- Parameter types and formats
- Value ranges
- Enum values (order types, time in force, etc.)

## Next Steps

- Check out the [Examples](examples.md) for practical usage scenarios
- View the [API Reference](../api/client.md) for detailed method documentation
- Return to the [Getting Started](getting_started.md) guide