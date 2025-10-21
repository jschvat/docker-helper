# PostgreSQL Docker Configuration - The Correct Way

## Executive Summary

**You were absolutely right!** The previous configuration was treating `PGDATA` as a volume mount point, when it should be an environment variable that PostgreSQL uses internally. The PostgreSQL Docker image already sets this correctly - we just need to mount a volume at the right parent directory.

## The Key Insight

`PGDATA` is **not** a volume mount point - it's an **environment variable** that tells PostgreSQL where to store its data **inside the container**.

### What Changed in PostgreSQL 18+

**PostgreSQL 17 and below:**
```bash
PGDATA=/var/lib/postgresql/data
VOLUME /var/lib/postgresql/data
```

**PostgreSQL 18+ (current latest):**
```bash
PGDATA=/var/lib/postgresql/18/docker
VOLUME /var/lib/postgresql
```

## The Problem with the Old Configuration

### Old (Incorrect) postgresql.yml:
```yaml
variables:
  - name: PGDATA
    label: "Data Path"
    type: path
    default: "/var/lib/postgresql/data"
```

**What this did wrong:**
1. Treated PGDATA as a volume mount point
2. Tried to mount user's path to `/var/lib/postgresql/data`
3. Conflicted with PostgreSQL 18's default PGDATA of `/var/lib/postgresql/18/docker`
4. Caused initialization errors

**Generated (broken) command:**
```bash
docker run -d \
  -v /home/jason/postgres_backup:/var/lib/postgresql/data \
  postgres:latest
```

**Why it failed:**
- PostgreSQL 18 expects to write to `/var/lib/postgresql/18/docker` (PGDATA)
- But the volume is mounted at `/var/lib/postgresql/data` (wrong location!)
- The mount doesn't include the parent directory `/var/lib/postgresql`
- PostgreSQL can't create its data directory structure

## The Correct Configuration

### New (Correct) postgresql.yml:
```yaml
variables:
  - name: DATA_VOLUME
    label: "Data Directory"
    type: path
    default: "/var/lib/postgresql"
    description: "Host path to store PostgreSQL's data. (PostgreSQL 18+ mounts at /var/lib/postgresql)"
```

**What this does right:**
1. Mounts at the parent directory `/var/lib/postgresql`
2. Lets PostgreSQL use its default PGDATA environment variable
3. PostgreSQL creates `/var/lib/postgresql/18/docker` inside the mounted volume
4. Works correctly with PostgreSQL 18+

**Generated (correct) command:**
```bash
docker run -d \
  --name postgresql \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=mydb \
  -v /home/jason/postgres_data:/var/lib/postgresql \
  -p 5432:5432/tcp \
  postgres:latest
```

## How It Works

### PostgreSQL 18+ (current)

1. **Image sets** `PGDATA=/var/lib/postgresql/18/docker` (built-in)
2. **We mount** `/home/jason/postgres_data` → `/var/lib/postgresql`
3. **PostgreSQL creates** `/var/lib/postgresql/18/docker/` (inside the mount)
4. **Data is stored** in `/home/jason/postgres_data/18/docker/` on the host
5. **Everything works!**

### Directory Structure

**On Host:**
```
/home/jason/postgres_data/
└── 18/
    └── docker/
        ├── base/
        ├── global/
        ├── pg_wal/
        ├── pg_hba.conf
        └── postgresql.conf
```

**In Container:**
```
/var/lib/postgresql/    <- Mounted from host
└── 18/
    └── docker/         <- PGDATA points here
        ├── base/
        ├── global/
        ├── pg_wal/
        └── ...
```

## For PostgreSQL 17 and Below

If using an older PostgreSQL version, you have two options:

### Option 1: Use the New Mount Point (Recommended)
```yaml
# Same configuration works!
docker run -d \
  -v /home/jason/postgres_data:/var/lib/postgresql \
  postgres:17
```

PostgreSQL 17's `PGDATA=/var/lib/postgresql/data` will create:
```
/home/jason/postgres_data/
└── data/
    ├── base/
    ├── global/
    └── ...
```

### Option 2: Override PGDATA (Opt-in)
```bash
docker run -d \
  -e PGDATA=/var/lib/postgresql/17/docker \
  -v /home/jason/postgres_data:/var/lib/postgresql \
  postgres:17
```

This makes PostgreSQL 17 behave like PostgreSQL 18.

## Why This Matters

### Correct Approach Benefits:
✓ **Future-proof**: Works with PostgreSQL 18+ out of the box
✓ **Version-specific**: Each PostgreSQL version uses its own subdirectory
✓ **Clean upgrades**: Can run multiple versions side-by-side
✓ **No conflicts**: Doesn't override image defaults
✓ **Standard practice**: Follows official PostgreSQL Docker recommendations

### What We Learned:
- PGDATA is an **environment variable**, not a mount point
- The **image** sets PGDATA correctly - don't override it
- Mount at the **parent directory** (`/var/lib/postgresql`)
- Let PostgreSQL create its **subdirectory structure**

## Testing the Fix

### Step 1: Remove Old Container
```bash
docker rm -f postgresql
rm -rf /home/jason/postgres_backup
```

### Step 2: Install with New Configuration
Using docker_helper GUI:
1. Install PostgreSQL
2. **Data Directory (Host Path)**: `/home/jason/postgres_data`
3. Leave "Map as volume" enabled
4. **Container Path** will show: `/var/lib/postgresql` ✓

### Step 3: Verify It Works
```bash
# Check container is running
docker ps | grep postgresql

# Check data directory structure
ls -la /home/jason/postgres_data/
# Should show: 18/

ls -la /home/jason/postgres_data/18/docker/
# Should show: base/ global/ pg_wal/ etc.

# Connect to PostgreSQL
docker exec -it postgresql psql -U postgres
```

### Step 4: Verify Data Persistence
```bash
# Create a test database
docker exec -it postgresql psql -U postgres -c "CREATE DATABASE test;"

# Stop and remove container
docker stop postgresql
docker rm postgresql

# Reinstall with same data directory
# Your test database should still exist!
```

## Comparison Table

| Aspect | Old (Incorrect) | New (Correct) |
|--------|----------------|---------------|
| Variable Name | `PGDATA` | `DATA_VOLUME` |
| Type | path (confusing) | path (clear) |
| Mount Point | `/var/lib/postgresql/data` | `/var/lib/postgresql` |
| PGDATA Env | Overridden by mount | Uses image default |
| PostgreSQL 18 | ✗ Broken | ✓ Works |
| PostgreSQL 17 | ✓ Works (by accident) | ✓ Works |
| Multi-version | ✗ No | ✓ Yes |
| Official Docs | ✗ Conflicts | ✓ Matches |

## Update for Other Database Services

This same principle applies to other databases. They should mount at the parent directory, not override internal paths:

### MySQL/MariaDB
```yaml
# CORRECT
- name: DATA_VOLUME
  type: path
  default: "/var/lib/mysql"  # Parent directory
```

### MongoDB
```yaml
# CORRECT
- name: DATA_VOLUME
  type: path
  default: "/data/db"  # MongoDB's data directory
```

### Redis
```yaml
# CORRECT
- name: DATA_VOLUME
  type: path
  default: "/data"  # Redis data directory
```

## Key Takeaways

1. **Don't override `PGDATA`** - the image sets it correctly
2. **Mount the parent directory** - let PostgreSQL create subdirectories
3. **Type `path` means volume mount point**, not environment variable
4. **Trust the official image** - it knows what it's doing
5. **Test with latest version** - PostgreSQL 18 is current

## References

- [Docker Library PostgreSQL Issue #1259](https://github.com/docker-library/postgres/pull/1259) - PGDATA change in PostgreSQL 18
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres) - Official documentation
- [PostgreSQL 18 Release Notes](https://www.postgresql.org/docs/18/release-18.html) - Changes and improvements

## Credit

Thanks to the user for catching this! The insight that "PGDATA should be an environment variable like `PGDATA=/var/lib/postgresql/17/docker`" was absolutely correct and led to discovering the PostgreSQL 18 changes.
