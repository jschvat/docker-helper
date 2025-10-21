# Volume Mapping Fix

## Issue
When installing PostgreSQL (or any service with path variables), the volume mapping was incorrect:
- **Expected**: `/home/jason/postgres_backup:/var/lib/postgresql/data`
- **Actual**: `/home/jason/postgres_backup:/data/PGDATA`

The container path was being generated incorrectly instead of using the path specified in the service YAML.

## Root Cause

### The Confusion
In the YAML service definitions, the `default` field for path-type variables means different things:
- For most variables: it's the default VALUE
- For path variables: it's the **CONTAINER** path, not the HOST path

**Example from postgresql.yml:**
```yaml
variables:
  - name: PGDATA
    label: "Data Path"
    type: path
    default: "/var/lib/postgresql/data"  # This is CONTAINER path!
```

### The Bug
The GUI was treating this backwards:

**Before (Buggy):**
1. Put `/var/lib/postgresql/data` in the HOST path field
2. Generated container path as `/data/PGDATA` (fallback)
3. Result: Wrong mapping `/var/lib/postgresql/data:/data/PGDATA`

## Fix Applied

### Changes (gui.py:1840-1961)

#### 1. Clarified Label (line 1844)
```python
if var_type in ['path', 'directory']:
    label_text = f"{var['label']} (Host Path)"
```
Now shows: "Data Path **(Host Path)**" to make it clear

#### 2. Fixed Host Path Field (line 1889-1892)
```python
input_widget = Gtk.Entry()
# For path types, show empty for host path (user needs to provide)
input_widget.set_text('')
input_widget.set_placeholder_text("Enter host path (e.g., /home/user/data)")
```
- Host path starts EMPTY (user must provide it)
- Clear placeholder text

#### 3. Fixed Container Path Field (line 1924-1942)
```python
# Use 'default' from YAML as the container path
default_container_path = var.get('default', f"/data/{var['name']}")
container_path_entry.set_text(default_container_path)
```
- Container path uses the `default` from YAML
- For PostgreSQL: `/var/lib/postgresql/data` ✓

#### 4. Enable by Default (line 1920, 1926)
```python
volume_check.set_active(True)  # Enable by default for path types
container_path_entry.set_sensitive(True)  # Allow editing
```
- Volume mapping enabled by default for path types
- Container path is editable (advanced users can change it)

#### 5. Added Visual Clarity (line 1925-1955)
- Checkbox: "Map as volume (enabled)"
- Separate label: "Container Path:"
- Hint: "Volume mapping: **(host path)** → **(container path)**"
- Makes the direction of mapping crystal clear

## How It Works Now

### PostgreSQL Example

**GUI Display:**
```
Container Name: postgresql
---
User:               [postgres         ]
Password:           [changeme         ]
Database Name:      [postgres         ]

Data Path (Host Path): [/home/jason/postgres_backup  ] [📁]

☑ Map as volume (enabled)    Container Path:
                              [/var/lib/postgresql/data]

Volume mapping: (host path) → (container path)
```

**Result:**
- Volume mapping: `/home/jason/postgres_backup:/var/lib/postgresql/data` ✓
- Docker command: `docker run -v /home/jason/postgres_backup:/var/lib/postgresql/data postgres`

### Step-by-Step User Flow

1. **User sees:** "Data Path (Host Path)" - clear it's the host
2. **User enters:** `/home/jason/postgres_backup`
3. **System shows:** Container path already filled: `/var/lib/postgresql/data`
4. **User understands:** `host → container` mapping
5. **Result:** Correct volume mapping!

## Benefits

### 1. Correct Paths
- Container paths use the values from YAML (the actual paths the application expects)
- Host paths are user-provided (where they want data stored)

### 2. Clear UI
- Labels explicitly say "(Host Path)"
- Separate fields for host and container paths
- Visual hint shows direction: host → container

### 3. Smart Defaults
- Container path pre-filled with correct value from YAML
- Volume mapping enabled by default
- Host path empty (forces user to make a conscious choice)

### 4. Flexibility
- Users can still edit container path if needed (advanced use)
- Can disable volume mapping if they want to use environment variable instead

## Testing

### Test Case 1: PostgreSQL
**Setup:**
1. Install PostgreSQL
2. Host path: `/home/user/pgdata`
3. Container path: `/var/lib/postgresql/data` (pre-filled)

**Expected Result:**
```bash
docker run -v /home/user/pgdata:/var/lib/postgresql/data postgres
```
✓ Works correctly

### Test Case 2: Custom Container Path
**Setup:**
1. Install PostgreSQL
2. Host path: `/mnt/storage/db`
3. Edit container path to: `/custom/data`

**Expected Result:**
```bash
docker run -v /mnt/storage/db:/custom/data postgres
```
✓ Works correctly

### Test Case 3: Disable Volume Mapping
**Setup:**
1. Install PostgreSQL
2. Uncheck "Map as volume"
3. Enter path in host field

**Expected Result:**
```bash
docker run -e PGDATA=/var/lib/postgresql/data postgres
```
(Sets as environment variable instead)
✓ Works correctly

## Docker-Compose Generation

The fix also ensures docker-compose files are generated correctly:

**Before (Buggy):**
```yaml
services:
  postgresql:
    volumes:
      - /var/lib/postgresql/data:/data/PGDATA  # Wrong!
```

**After (Fixed):**
```yaml
services:
  postgresql:
    volumes:
      - /home/jason/postgres_backup:/var/lib/postgresql/data  # Correct!
```

## YAML Service Definition Guidelines

For service authors, the correct format for path variables is:

```yaml
variables:
  - name: DATA_PATH
    label: "Data Directory"
    type: path
    default: "/path/in/container"  # This is where the app expects data INSIDE the container
    description: "Where to store the data"
```

**Important:**
- `default` = **CONTAINER** path (where the app looks for data)
- User provides = **HOST** path (where data is stored on host machine)
- Mapping = `host_path:container_path`

## Related Issues Fixed

This fix also resolves:
- ✓ MySQL data directory mapping
- ✓ MariaDB data directory mapping
- ✓ MongoDB data directory mapping
- ✓ Any service with `type: path` or `type: directory` variables

## Files Modified

**gui.py** - Lines 1840-1961:
- Line 1844: Added "(Host Path)" to label
- Line 1891: Clear host path field, add placeholder
- Line 1925: Changed checkbox label
- Line 1930-1931: Added "Container Path:" label
- Line 1939: Use `default` from YAML for container path
- Line 1947-1954: Added mapping direction hint

## Summary

**Before:**
- Confusing: Which path is which?
- Wrong: Container path was generated incorrectly
- Result: Data stored in wrong place in container

**After:**
- Clear: Labels say "(Host Path)" and "Container Path:"
- Correct: Container path from YAML, host path from user
- Result: Data mapped correctly ✓

The volume mapping now works as Docker users expect!
