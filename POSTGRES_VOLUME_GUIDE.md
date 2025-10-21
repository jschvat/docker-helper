# PostgreSQL Volume Mapping Guide

## Automatic Directory Creation (v2.0+)

**Good news!** As of version 2.0, docker_helper **automatically creates host directories** before mounting volumes. You no longer need to manually create directories!

When you install PostgreSQL (or any service with volume mappings):
1. Simply specify your desired host path (e.g., `/home/jason/postgres_data`)
2. docker_helper will automatically create the directory if it doesn't exist
3. PostgreSQL will initialize the directory on first startup

The system shows a confirmation message: `✓ Created directory: /home/jason/postgres_data`

## The Issue (Historical)

Before automatic directory creation, users encountered this error:
```
error mounting "/home/user/path" to rootfs at "/var/lib/postgresql/data":
no such file or directory
```

## Why This Happens

PostgreSQL's official Docker image has specific requirements for the data directory:

1. The directory `/var/lib/postgresql/data` must exist in the container
2. PostgreSQL needs to initialize this directory on first run
3. The host directory must exist and have proper permissions
4. Nested subdirectories (like `/path/data/subdir`) can cause initialization issues

## Solutions

### Solution 1: Use a Subdirectory (Recommended)

Instead of mapping directly to `/var/lib/postgresql/data`, use a subdirectory:

**Host Path**: `/home/jason/postgres_data`
**Container Path**: `/var/lib/postgresql/data/pgdata`

Then set the `PGDATA` environment variable (the postgres image looks for this):
**PGDATA**: `/var/lib/postgresql/data/pgdata`

This is actually already configured in the postgresql.yml!

### Solution 2: Let PostgreSQL Create the Structure

1. **Host Path**: `/home/jason/postgres_data` (empty directory)
2. **Container Path**: `/var/lib/postgresql/data`
3. Make sure the directory is empty and has proper permissions

PostgreSQL will initialize it on first startup.

### Solution 3: Use Named Volume

Instead of specifying a host path, you can let Docker manage it:

1. Disable volume mapping checkbox
2. Docker will create an internal named volume
3. Data persists but is managed by Docker

## Step-by-Step for PostgreSQL

### Option A: Using the GUI (Current Setup)

1. Click Install on postgresql
2. Fill in:
   - Container Name: `postgresql` or custom name
   - User: `postgres`
   - Password: **Choose a strong password!**
   - Database Name: `postgres`
   - **Data Path (Host Path)**: `/home/jason/postgres_data` (or your preferred location)

3. Volume Mapping section:
   - ☑ Map as volume (enabled)
   - Container Path: `/var/lib/postgresql/data`

4. Click Install

### Option B: Simpler Approach

If you keep getting errors, try this:

1. **Don't create any directories manually** - let Docker do it
2. When installing, enter a path that **doesn't exist yet**:
   - Data Path: `/home/jason/postgres-NEW`
3. Docker will create it automatically
4. PostgreSQL will initialize it

## Common Mistakes

### ❌ Don't Do This:
```
Host Path: /home/jason/postgres_backup/data
Container Path: /var/lib/postgresql/data
```
This creates: `/home/jason/postgres_backup/data` → `/var/lib/postgresql/data`

### ✓ Do This Instead:
```
Host Path: /home/jason/postgres_data
Container Path: /var/lib/postgresql/data
```
Just one level, clean and simple.

## Fixing Your Current Issue

Based on your error with `/home/jason/postgres_backup/data`, here's what to do:

### Quick Fix (Recommended):
1. Remove the existing failed container:
   ```bash
   docker rm postgresql
   ```

2. Remove the problematic nested directory:
   ```bash
   rm -rf /home/jason/postgres_backup
   ```

3. Install PostgreSQL again with a simple path:
   - Host Path: `/home/jason/postgres_data`
   - docker_helper will automatically create it
   - PostgreSQL will initialize it properly
   - No manual directory creation needed!

**Why this works:** The automatic directory creation ensures proper permissions, and using a simple path (without `/data` subdirectory) lets PostgreSQL initialize cleanly.

### Alternative Fix:
Use the directory you want but ensure it's empty:
```bash
# If directory exists, make sure it's empty
rm -rf /home/jason/postgres_backup/*

# Or start fresh
mkdir -p /home/jason/postgres_data
chmod 777 /home/jason/postgres_data  # Temporary, for testing
```

Then install PostgreSQL with:
- Host Path: `/home/jason/postgres_data`
- Container Path: `/var/lib/postgresql/data`

## Verifying It Works

After installation, check:

```bash
# Container is running
docker ps | grep postgres

# Data directory is populated
ls -la /home/jason/postgres_data
# You should see PostgreSQL files: base/, global/, pg_wal/, etc.

# Connect to verify
docker exec -it postgresql psql -U postgres
```

## For Other Databases

This applies to other databases too:

### MySQL
- Host Path: `/home/user/mysql_data`
- Container Path: `/var/lib/mysql`
- Let MySQL initialize it

### MariaDB
- Host Path: `/home/user/mariadb_data`
- Container Path: `/var/lib/mysql`
- Let MariaDB initialize it

### MongoDB
- Host Path: `/home/user/mongodb_data`
- Container Path: `/data/db`
- Let MongoDB initialize it

## Key Principles

1. **Empty host directory**: Start with an empty directory
2. **Let the app initialize**: Don't pre-populate the directory
3. **Simple paths**: Use one directory level, not nested subdirectories
4. **Proper permissions**: Ensure the directory is readable/writable

## If Still Not Working

Try the nuclear option - use Docker-managed volumes:

1. Install PostgreSQL
2. **Uncheck** "Map as volume"
3. Docker will create an internal volume
4. Data persists but you don't manage the path

To find where Docker stored it:
```bash
docker volume ls
docker volume inspect <volume_name>
```

This always works but gives you less control over where data is stored.
