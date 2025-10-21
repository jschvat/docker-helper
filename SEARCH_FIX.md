# Service Search Fix

## Issue
The service search bar in the GUI was not finding services correctly. For example, searching for "postgres" did not find "postgresql".

## Root Cause
The search filter function (`service_filter_func` in gui.py:365-403) was incorrectly accessing the widget hierarchy:

**Before (broken):**
```python
hbox = row.get_child()
label = hbox.get_children()[1]  # This was getting the vbox, not the label
service_name = label.get_label().lower()
```

The widget structure is:
```
ListBoxRow
  └─ HBox
       ├─ CheckButton (index 0)
       └─ VBox (index 1)
            ├─ Label (service name)
            └─ Label (description, optional)
```

So `hbox.get_children()[1]` was getting the VBox, not the Label.

## Fix Applied
Updated the filter function to correctly navigate the widget hierarchy and search both the service name AND description:

**After (fixed):**
```python
def service_filter_func(self, row, data):
    """Filter services based on search text (searches name and description)"""
    search_text = self.service_search_entry.get_text().lower()
    if not search_text:
        return True

    # Get the main hbox from the row
    hbox = row.get_child()
    if not hbox:
        return False

    # The structure is: hbox -> [checkbox, vbox]
    # vbox contains [name_label, desc_label (optional)]
    children = hbox.get_children()
    if len(children) < 2:
        return False

    vbox = children[1]  # Get the vbox (second child after checkbox)
    vbox_children = vbox.get_children()

    if not vbox_children:
        return False

    # Get service name from first label
    name_label = vbox_children[0]
    service_name = name_label.get_text().lower()

    # Check if search text is in service name
    if search_text in service_name:
        return True

    # Also check description if it exists
    if len(vbox_children) > 1:
        desc_label = vbox_children[1]
        description = desc_label.get_text().lower()
        if search_text in description:
            return True

    return False
```

## Improvements
1. **Correct widget navigation** - Now properly accesses the VBox and then the Labels inside it
2. **Description search** - Now searches both service name AND description
3. **Error handling** - Added safety checks to prevent crashes if widget structure changes
4. **Better documentation** - Added clear comments explaining the widget hierarchy

## Testing
A test script (`test_services.py`) was added to verify service loading and search functionality:

```bash
python3 test_services.py
```

**Test results for "postgres" search:**
- postgresql ✓
- pgadmin ✓
- pgbackup ✓

All services containing "postgres" in their name or description are now found correctly.

## Files Modified
- `gui.py` (lines 365-403) - Fixed `service_filter_func()`

## Usage
Now when you type in the search bar:
- **"postgres"** - Finds: postgresql, pgadmin, pgbackup
- **"postgresql"** - Finds: postgresql, pgadmin, pgbackup
- **"sql"** - Finds: mysql, mssql, postgresql, pgadmin, etc.
- **"database"** - Finds all services with "database" in name or description
- **"photo"** - Finds: photoprism, photostructure, piwigo, etc.

The search is case-insensitive and searches both the service name and description fields.
