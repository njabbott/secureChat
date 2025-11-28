# Chat Magic - Log Files

This directory contains log files for the Chat Magic application.

## Log Files

### 1. debug.log
- **Purpose**: Comprehensive debug logging
- **Level**: DEBUG and above (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Content**: All application events, detailed debugging information
- **Use**: Development, troubleshooting, detailed analysis
- **Format**: `YYYY-MM-DD HH:MM:SS - logger.name - LEVEL - [filename:line] - message`

### 2. application.log
- **Purpose**: General application logging
- **Level**: INFO and above (INFO, WARNING, ERROR, CRITICAL)
- **Content**: Normal application operations, important events
- **Use**: Production monitoring, audit trail
- **Format**: `YYYY-MM-DD HH:MM:SS - logger.name - LEVEL - [filename:line] - message`

### 3. error.log
- **Purpose**: Warnings and errors only
- **Level**: WARNING and above (WARNING, ERROR, CRITICAL)
- **Content**: Issues, exceptions, errors that need attention
- **Use**: Quick error identification, alerts
- **Format**: `YYYY-MM-DD HH:MM:SS - logger.name - LEVEL - [filename:line] - message`

## Log Rotation

All log files use rotating file handlers:
- **Max Size**: 10 MB per file
- **Backups**: 5 backup files retained
- **Pattern**: `logfile.log`, `logfile.log.1`, `logfile.log.2`, etc.

## Configuration

Logging is configured in `backend/app/logging_config.py`

The log level can be set via the `LOG_LEVEL` environment variable in `.env` file:
- DEBUG: Most verbose
- INFO: Standard (default)
- WARNING: Only warnings and errors
- ERROR: Only errors
- CRITICAL: Only critical errors

## Common Log Entries

### Successful Operations
```
2025-11-20 11:42:14 - app.main - INFO - [main.py:71] - Chat Magic application started successfully
2025-11-20 11:42:14 - app.services.confluence_service - INFO - [confluence_service.py:25] - Retrieved 2 Confluence spaces
```

### Errors
```
2025-11-20 11:42:12 - chromadb.telemetry.product.posthog - ERROR - [posthog.py:59] - Failed to send telemetry event
2025-11-20 20:57:08 - openai.RateLimitError - ERROR - Error code: 429 - You exceeded your current quota
```

### Warnings
```
2025-11-20 11:42:12 - presidio-analyzer - WARNING - [nlp_engine_provider.py:118] - configuration file not found. Using default config
```

## Monitoring Best Practices

1. **Regular Review**: Check error.log daily for issues
2. **Debug Mode**: Enable DEBUG level only when troubleshooting
3. **Disk Space**: Monitor logs directory size (auto-rotation helps)
4. **Alerts**: Set up monitoring for ERROR level entries
5. **Archive**: Backup old logs before they rotate out

## Troubleshooting

If logs are not being written:
1. Check directory permissions
2. Verify LOG_LEVEL setting in .env
3. Check disk space
4. Review logging_config.py configuration
