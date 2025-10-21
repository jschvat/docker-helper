# Container Name Feature

## Overview
Added the ability to specify custom container names when installing services through the GUI. This allows users to create multiple instances of the same service with unique names.

## What Was Added

### 1. Container Name Field in Install Dialog (gui.py:1785-1821)

When you click "Install" on a service, the dialog now includes:

**Field Components:**
- **Text Entry**: Editable field with the default service name pre-filled
- **Auto-Generate Button**: Refresh icon button that generates a unique name
- **Hint Text**: Explains naming rules

**Default Behavior:**
- Pre-filled with the service name (e.g., "postgresql")
- Can be edited to any valid Docker container name
- Must be unique among existing containers

### 2. Auto-Generate Unique Name Button

Click the refresh icon button to automatically generate a unique name:
- Checks all existing container names
- Appends a number if the name exists (e.g., postgresql-1, postgresql-2, etc.)
- Increments until it finds an available name
- Updates the text field automatically

### 3. Validation (gui.py:2010-2061)

**Format Validation:**
Container names must follow Docker naming rules:
- ✓ Start with a letter or number
- ✓ Contain only: letters, numbers, hyphens (-), underscores (_), periods (.)
- ✗ No spaces
- ✗ No special characters

**Examples:**
- ✓ Valid: `postgresql`, `postgres-1`, `my_db`, `db.prod`
- ✗ Invalid: `my database`, `db#1`, `@postgres`, `-db`

**Duplicate Detection:**
If a container with that name already exists:
1. Shows warning dialog
2. Offers to remove the existing container
3. If you choose "Yes": Stops and removes the old container, then installs new one
4. If you choose "No": Returns to config dialog so you can change the name

### 4. Backend Support (core.py:74-79)

The `install_service()` function now:
- Accepts `container_name` in `config_values`
- Uses custom name if provided
- Falls back to service name if not provided
- Generates proper `docker run --name <container_name>` command

## Usage Examples

### Example 1: Multiple PostgreSQL Instances

**Scenario:** You want to run two PostgreSQL databases, one for development and one for testing.

1. Select **postgresql** service
2. Click **Install**
3. Change container name from "postgresql" to "**postgres-dev**"
4. Configure settings (ports, passwords, etc.)
5. Click **Install**

Then repeat:
1. Select **postgresql** service again
2. Click **Install**
3. Change container name to "**postgres-test**"
4. Use different port (e.g., 5433 instead of 5432)
5. Click **Install**

Result: Two PostgreSQL containers running with different names and ports!

### Example 2: Using Auto-Generate Button

**Scenario:** You want to quickly create multiple instances without thinking of names.

1. Select service
2. Click **Install**
3. Click the **refresh icon** button next to container name
4. Name automatically changes to "service-name-1" (or -2, -3, etc.)
5. Click **Install**

### Example 3: Replacing Existing Container

**Scenario:** You want to replace a container with a fresh installation.

1. Select service
2. Click **Install**
3. Keep the existing name (or enter a name that already exists)
4. Configure settings
5. Click **Install**
6. Dialog appears: "Container 'name' already exists"
7. Click **Yes** to remove old and install new
8. Old container is stopped, removed, and replaced

## Benefits

### 1. Multiple Service Instances
Run multiple instances of the same service:
- Multiple databases for different projects
- Test and production versions
- Blue-green deployments

### 2. Organized Naming
Give meaningful names to your containers:
- `postgres-wordpress`
- `postgres-nextcloud`
- `mysql-dev`
- `mysql-prod`

### 3. Easy Identification
Find containers easily:
- Container lists are sorted alphabetically
- Named containers are easier to identify than UUIDs
- Meaningful names help with troubleshooting

### 4. Prevents Accidents
Validation prevents:
- Overwriting containers accidentally
- Invalid Docker names
- Naming conflicts

## Technical Details

### Data Flow

```
User Input → Validation → config_values → core.install_service() → Docker Command
```

1. **User enters name** in GUI dialog
2. **GUI validates** format and uniqueness
3. **Stored in** `config_values["container_name"]`
4. **Passed to** `core.install_service(service_config, config_values)`
5. **Used in** `docker run --name <container_name>` command

### Validation Rules

**Python Regex:** `^[a-zA-Z0-9][a-zA-Z0-9_.-]*$`

Breakdown:
- `^` - Start of string
- `[a-zA-Z0-9]` - First character must be letter or number
- `[a-zA-Z0-9_.-]*` - Remaining characters can be letters, numbers, underscore, period, or hyphen
- `$` - End of string

### Auto-Generate Algorithm

```python
base_name = "service"
existing = ["service", "service-1", "service-2"]
counter = 1
new_name = base_name

while new_name in existing:
    new_name = f"{base_name}-{counter}"
    counter += 1

# Result: new_name = "service-3"
```

## Files Modified

1. **gui.py** (lines 1785-1821, 1960-1965, 2010-2061)
   - Added container name field to install dialog
   - Added auto-generate button
   - Added validation logic
   - Added duplicate handling

2. **core.py** (lines 74-79)
   - Updated `install_service()` to accept custom container name
   - Falls back to service name if not provided

## Backward Compatibility

✓ Fully backward compatible
- If no container name is provided, uses service name (original behavior)
- CLI installations still work as before
- Existing scripts and workflows unaffected

## Future Enhancements

Potential improvements:
- **Label/tag support**: Add Docker labels to containers
- **Name templates**: Use variables like {service}-{date} or {service}-{user}
- **Naming conventions**: Enforce organization-specific naming patterns
- **Bulk naming**: When installing multiple services, auto-append numbers
- **Name validation indicator**: Real-time green/red indicator as you type
- **Recent names**: Dropdown showing recently used names
