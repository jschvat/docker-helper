# Container Logs Feature

## Overview
Added a comprehensive logs viewer to the Docker Container Manager GUI, accessible via a new action button (📋) in the Running Containers view.

## Features

### Access
- **Location**: Actions column in Running Containers view
- **Button**: 📋 (clipboard icon) - 4th button from the left
- **Tooltip**: "View container logs"
- **Position**: ▶ ↻ ⏹ **📋** 💾 🗑

### Logs Dialog Options

1. **Tail Lines Control**
   - Adjustable spinner (10 - 10,000 lines)
   - Default: 100 lines
   - Shows most recent N lines from container output

2. **Timestamps Toggle**
   - Checkbox: "Show timestamps"
   - Default: Enabled
   - Displays Docker's native timestamps with each log entry

3. **Follow Logs** (UI only - not implemented)
   - Checkbox: "Follow logs (live)"
   - Placeholder for future live streaming feature

### Dialog Layout

```
┌─────────────────────────────────────────────┐
│ Logs: container-name               [Refresh]│
│                                      [Close] │
├─────────────────────────────────────────────┤
│ Tail lines: [100▼]  ☑ Follow logs (live)   │
│                      ☑ Show timestamps       │
├─────────────────────────────────────────────┤
│                                             │
│  [Monospace log output view]               │
│  Scrollable, selectable text               │
│  Auto-scrolls to bottom on load            │
│                                             │
└─────────────────────────────────────────────┘
```

### Functionality

#### Load Logs
- **Initial Load**: Automatically fetches logs when dialog opens
- **Parameters**:
  - `tail`: Number of lines from spinner control
  - `timestamps`: Boolean from checkbox
- **Output**: UTF-8 decoded text with error handling for invalid characters

#### Refresh Logs
- **Button**: "Refresh" in dialog header
- **Action**: Reloads logs with current settings
- **Use Case**: Check for new log entries without closing dialog

#### Auto-Scroll
- Automatically scrolls to the bottom of logs after loading
- Shows most recent entries first

## Implementation Details

### Code Location
- **Method**: `view_container_logs()` in gui.py:1102-1200
- **Called from**: `on_container_button_press()` when 4th button clicked

### Docker API Usage
```python
logs = container.logs(
    tail=tail_lines,      # Number of lines
    timestamps=show_timestamps  # Include timestamps
).decode('utf-8', errors='replace')
```

### Dialog Specifications
- **Size**: 900x600 pixels
- **Font**: Monospace 9pt
- **Margins**: 8px all sides
- **Word Wrap**: Enabled
- **Selection**: Enabled (users can copy log text)

## Testing

### Test Container
A log-generating test container has been created:
```bash
docker run -d --name test-logs-container alpine sh -c \
  'while true; do echo "Log entry at $(date)"; sleep 2; done'
```

### Test Cases

1. **Basic Viewing**
   - Click 📋 button on any running container
   - Verify logs appear in monospace font
   - Check timestamps are displayed

2. **Tail Lines Control**
   - Change spinner value to 50
   - Click "Refresh"
   - Verify only 50 lines shown

3. **Toggle Timestamps**
   - Uncheck "Show timestamps"
   - Click "Refresh"
   - Verify timestamps removed

4. **Text Selection**
   - Click and drag in log view
   - Verify text can be selected and copied

5. **Auto-Scroll**
   - Open logs dialog
   - Verify view scrolls to bottom automatically

## UI Changes Summary

### Actions Column
- **Previous**: 5 buttons (70px width)
  - ▶ ↻ ⏹ 💾 🗑

- **Current**: 6 buttons (84px width)
  - ▶ ↻ ⏹ 📋 💾 🗑

### Button Specifications
| Button | Symbol | Color | Size | Function |
|--------|--------|-------|------|----------|
| Start  | ▶      | Green (#10b981) | 12pt | Start container |
| Restart | ↻     | Blue (#667eea) | 12pt | Restart container |
| Stop   | ⏹      | Orange (#f59e0b) | 12pt | Stop container |
| **Logs** | **📋** | **Cyan (#06b6d4)** | **11pt** | **View logs** |
| Backup | 💾     | Purple (#8b5cf6) | 11pt | Backup container |
| Remove | 🗑      | Red (#ef4444) | 11pt | Remove container |

## Future Enhancements

### Planned Features
1. **Live Log Streaming**
   - Implement "Follow logs (live)" checkbox
   - Auto-refresh with configurable interval
   - Stop/Start streaming button

2. **Log Filtering**
   - Search/filter text input
   - Regex support
   - Highlight matches

3. **Log Export**
   - Save logs to file
   - Copy all to clipboard
   - Export with/without timestamps

4. **Since/Until Time Range**
   - Date/time pickers
   - Relative time options (last hour, last day, etc.)

5. **Log Level Filtering**
   - If container uses structured logging
   - Filter by ERROR, WARN, INFO, DEBUG

6. **Color Coding**
   - Syntax highlighting for common log formats
   - Error/warning colors
   - Timestamp dimming

## Keyboard Shortcuts (Future)

Potential shortcuts for future implementation:
- `Ctrl+F`: Find in logs
- `Ctrl+R`: Refresh logs
- `Ctrl+C`: Copy selected text
- `Ctrl+A`: Select all
- `Esc`: Close dialog

## Error Handling

The dialog handles several error cases:
- Container not found
- Container has no logs
- Invalid UTF-8 characters (replaced with '�')
- Docker API errors

All errors display in the log view with clear error message.

## Comparison to CLI

### CLI Equivalent
```bash
# Basic view
docker logs container-name

# With options (matching dialog defaults)
docker logs --tail 100 --timestamps container-name

# Live following (not yet implemented in GUI)
docker logs --follow container-name
```

### GUI Advantages
- No need to remember container IDs/names
- Visual controls for common options
- Persistent dialog for multiple refreshes
- Text selection and scrolling
- Integrated with container management workflow

## Code Statistics

- Lines added: ~100
- Methods added: 1 (`view_container_logs`)
- Buttons added: 1 (logs button)
- Dialog width: 84px total for Actions column
- Minimal performance impact (on-demand loading)
