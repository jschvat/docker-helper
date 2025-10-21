# Docker-Compose Generation Bug Fix

## Issue
When clicking "Save as docker-compose.yml" for a service (e.g., PostgreSQL), the system was:
1. Saving the file with a wrong name (like `duckdns.yml` instead of `postgresql-compose.yml`)
2. Showing deployment dialog with wrong service name ("Deploy duckdns" instead of "Deploy postgresql")

## Root Cause
The `save_service_as_compose()` function was using `service_name` from the service configuration instead of the user's custom `container_name` from config_values.

### Before (Buggy Behavior)
```python
service_name = service_config.get('name', 'service')  # Always "postgresql"
# Used service_name everywhere

compose = {
    'services': {
        service_name: {}  # Wrong - always uses service name
    }
}
service_def['container_name'] = service_name  # Wrong

save_dialog.set_current_name("docker-compose.yml")  # Wrong - generic name
deploy_dialog.text = f"Deploy '{service_name}' now?"  # Wrong
```

**Example Problem:**
- User installs PostgreSQL with custom name "postgres-prod"
- Clicks "Save as docker-compose.yml"
- File is saved as `docker-compose.yml` (generic)
- Dialog says "Deploy 'postgresql' now?" (ignores custom name)
- docker-compose.yml contains `container_name: postgresql` (wrong!)

## Fix Applied

### Changes Made (gui.py:3519-3677)

1. **Get custom container name** (line 3521):
   ```python
   container_name = config_values.get('container_name', service_name)
   ```

2. **Use container_name in compose structure** (line 3527, 3539):
   ```python
   compose = {
       'services': {
           container_name: {}  # Now uses custom name
       }
   }
   service_def['container_name'] = container_name  # Correct
   ```

3. **Suggest proper filename** (line 3613):
   ```python
   save_dialog.set_current_name(f"{container_name}-compose.yml")
   # Now suggests: "postgres-prod-compose.yml"
   ```

4. **Update dialog titles** (line 3604, 3651):
   ```python
   title=f"Save docker-compose.yml for '{container_name}'"
   text=f"Deploy '{container_name}' now?"
   ```

5. **Update output messages** (line 3641, 3677):
   ```python
   f"✓ Saved docker-compose.yml for '{container_name}'\n"
   f"✓ Deployed '{container_name}' successfully!\n"
   ```

6. **Add service name to header comment** (line 3597):
   ```python
   header = f"# docker-compose.yml for {container_name}\n"
   header += f"# Service: {service_name}\n"
   # Shows both container name and service type
   ```

### After (Fixed Behavior)

**Example Fixed Flow:**
1. User installs PostgreSQL with custom name "postgres-prod"
2. Clicks "Save as docker-compose.yml"
3. File dialog suggests: `postgres-prod-compose.yml` ✓
4. Dialog says: "Deploy 'postgres-prod' now?" ✓
5. Generated file contains:
   ```yaml
   # docker-compose.yml for postgres-prod
   # Service: postgresql

   version: '3.8'
   services:
     postgres-prod:
       image: postgres:latest
       container_name: postgres-prod
       # ... rest of config
   ```
6. Success message: "✓ Deployed 'postgres-prod' successfully!" ✓

## Testing

### Test Case 1: Default Name
1. Install postgresql without changing name
2. Click "Save as docker-compose.yml"
3. Expected: `postgresql-compose.yml`, dialog says "Deploy 'postgresql'"
4. Result: ✓ Works correctly

### Test Case 2: Custom Name
1. Install postgresql, change name to "db-prod"
2. Click "Save as docker-compose.yml"
3. Expected: `db-prod-compose.yml`, dialog says "Deploy 'db-prod'"
4. Result: ✓ Works correctly

### Test Case 3: Multiple Instances
1. Install postgresql-1, save compose
2. Install postgresql-2, save compose
3. Expected: Two separate files with different names
4. Result: ✓ Works correctly

## Files Modified

**gui.py** - Lines 3519-3677:
- Line 3521: Added container_name extraction
- Line 3527: Use container_name in services dict
- Line 3539: Use container_name for container_name field
- Line 3596-3598: Updated header comments
- Line 3604: Updated dialog title
- Line 3613: Changed filename suggestion
- Line 3641: Updated output message
- Line 3651: Updated deploy dialog text
- Line 3677: Updated success message

## Benefits

1. **Correct filenames**: Each instance gets its own meaningful filename
2. **Clear dialogs**: User knows exactly what's being deployed
3. **Proper compose files**: Generated files use the correct container name
4. **Multiple instances**: Can save compose files for multiple instances of same service
5. **Better organization**: Files named after containers, not generic "docker-compose.yml"

## Examples

### Before Fix:
```bash
# User creates postgres-dev and postgres-test
# Both suggest saving as "docker-compose.yml"
# Both say "Deploy 'postgresql'"
# Confusing!
```

### After Fix:
```bash
# User creates postgres-dev
File: postgres-dev-compose.yml
Dialog: "Deploy 'postgres-dev' now?"

# User creates postgres-test
File: postgres-test-compose.yml
Dialog: "Deploy 'postgres-test' now?"

# Clear and organized!
```

## Backward Compatibility

✓ Fully backward compatible:
- If no custom name provided, uses service name (original behavior)
- Existing functionality preserved
- No breaking changes

## Related Features

This fix complements:
- Container name field in install dialog
- Auto-generate unique name button
- Container name validation
- Multiple instance support
