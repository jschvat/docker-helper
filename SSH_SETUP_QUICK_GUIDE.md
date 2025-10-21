# Quick SSH Setup Guide for Remote Docker

## Why SSH Keys Are Required

Docker's remote SSH connection **does not support password authentication**. You must use SSH keys for passwordless authentication.

## Quick Setup (3 Steps)

### Option 1: Use the Setup Helper Script (Recommended)

```bash
cd /media/jason/Array21/Development/claude/docker_helper
./setup_remote_ssh.sh
```

This interactive script will:
- Check if you have SSH keys
- Generate keys if needed
- Copy your key to the remote server (will ask for password once)
- Verify Docker access on the remote
- Test the connection

### Option 2: Manual Setup

#### Step 1: Generate SSH Key (if you don't have one)

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Press Enter to accept defaults (don't set a passphrase for automated access).

#### Step 2: Copy Key to Remote Server

**Method A - Using ssh-copy-id:**
```bash
ssh-copy-id user@remote-host
# Or with custom port:
ssh-copy-id -p 2222 user@remote-host
```

**Method B - Manual copy:**
```bash
cat ~/.ssh/id_ed25519.pub | ssh user@remote-host "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

You'll be asked for your password **one time** during this step.

#### Step 3: Add User to Docker Group on Remote

SSH to the remote server:
```bash
ssh user@remote-host
```

Then run:
```bash
sudo usermod -aG docker $USER
```

**Important:** Log out and log back in for the group change to take effect!

## Test Your Setup

Test SSH connection (should work without password):
```bash
ssh user@remote-host exit
```

Test Docker access:
```bash
ssh user@remote-host docker ps
```

If both work, you're ready to connect!

## Using with docker_helper

### From GUI:

1. Click **Connection** button
2. Select **Manage Remote Hosts...**
3. Click **Add New Remote Host**
4. Fill in the details
5. Click **Test Connection** button
6. If successful, click **Add**

### From CLI:

```bash
# Add the remote host
python3 main.py remote add myserver 192.168.1.100 --user john

# Test connection
python3 main.py --host myserver status

# Launch GUI connected to remote
python3 main.py --gui --host myserver
```

## Common Issues

### "SSH connection failed. Set up SSH keys first"

**Problem:** SSH key authentication is not working.

**Solution:** Run the setup script or manually copy your SSH key:
```bash
ssh-copy-id user@remote-host
```

### "SSH works but Docker access denied"

**Problem:** User is not in the docker group on the remote server.

**Solution:** On the remote server:
```bash
sudo usermod -aG docker $USER
# Then log out and back in
```

### "Docker not installed on remote"

**Problem:** Docker is not installed on the remote server.

**Solution:** Copy install.sh to remote and run it:
```bash
scp install.sh user@remote-host:~/
ssh user@remote-host 'bash ~/install.sh'
```

### "Connection timeout"

**Problem:** Network/firewall issues or wrong hostname.

**Solution:**
1. Verify hostname/IP is correct
2. Check firewall allows SSH (port 22 or custom port)
3. Try: `ping remote-host`

### "Permission denied (publickey)"

**Problem:** SSH key not properly copied to remote.

**Solution:**
1. Make sure key is copied: `ssh-copy-id user@remote-host`
2. Check permissions on remote:
   ```bash
   ssh user@remote-host
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

## Video Tutorial Equivalent

Here's the flow step-by-step:

```
┌─────────────────────────────────────┐
│ 1. Generate SSH Key (one-time)     │
│    ssh-keygen -t ed25519            │
│    Press Enter 3 times              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. Copy Key to Remote (one-time)   │
│    ssh-copy-id user@remote-host     │
│    Enter password: ********         │ ◄─── Only time you enter password
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. Add User to Docker Group        │
│    ssh user@remote-host             │ ◄─── No password needed!
│    sudo usermod -aG docker $USER    │
│    logout                           │
│    ssh user@remote-host             │ ◄─── Log back in
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Test Everything                  │
│    ssh user@remote-host docker ps   │ ◄─── Should work!
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 5. Add to docker_helper             │
│    - Open GUI                       │
│    - Click "Connection" button      │
│    - Manage Remote Hosts            │
│    - Add New Remote Host            │
│    - Click "Test Connection"        │
│    - Should show green checkmark!   │
└─────────────────────────────────────┘
```

## Security Notes

1. **SSH Keys are safer than passwords** - They use public-key cryptography
2. **Never share your private key** (~/.ssh/id_ed25519)
3. **The public key is safe to share** (~/.ssh/id_ed25519.pub)
4. **Use different keys for different environments** (optional but recommended)

## What Happens Under the Hood

When you connect to `ssh://user@remote-host`:

1. docker_helper uses the Docker SDK
2. Docker SDK creates an SSH connection
3. SSH looks for your private key (~/.ssh/id_ed25519)
4. Remote server checks if your public key is in ~/.ssh/authorized_keys
5. If match found, connection is established (no password needed!)
6. Docker commands are sent over the SSH tunnel
7. Results come back through the same tunnel

## Need Help?

If you're still having issues:

1. Run the setup helper script: `./setup_remote_ssh.sh`
2. Check the detailed guide: `REMOTE_DOCKER.md`
3. Try the test connection in the GUI before saving

The GUI will show specific error messages to help troubleshoot!
