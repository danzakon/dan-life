# Hetzner Remote Development Server Setup

A complete guide to setting up a Hetzner cloud server for remote development, with SSH access from your Mac and mobile devices via Termius.

---

## Overview

```
┌─────────────────┐     SSH/Keys      ┌─────────────────┐
│   Your Mac      │─────────────────▶│  Hetzner VPS    │
│   (primary)     │                   │  (Ubuntu/Debian)│
└─────────────────┘                   └────────┬────────┘
                                               │
┌─────────────────┐     SSH/Keys               │
│   iPhone/iPad   │────────────────────────────┘
│   (Termius)     │
└─────────────────┘
```

**What you'll end up with:**
- A secure cloud server running Ubuntu or Debian
- SSH key-based authentication (no passwords)
- Development tools: zsh, neovim, tmux, git, etc.
- Mobile access via Termius on iPhone/iPad
- Persistent sessions with tmux

---

## Part 1: Create Your Hetzner Server

### 1.1 Create a Hetzner Cloud Account

1. Go to [https://console.hetzner.cloud/](https://console.hetzner.cloud/)
2. Sign up for an account (requires email verification)
3. Add a payment method

### 1.2 Create a New Project

1. Click **+ New Project** in the Hetzner Cloud Console
2. Name it something like "dev-server"

### 1.3 Generate SSH Keys (On Your Mac)

Before creating the server, generate an SSH key pair on your Mac:

```bash
ssh-keygen -t ed25519 -C "dan@hetzner-dev"
```

| Part | Meaning |
|------|---------|
| `ssh-keygen` | Tool to generate SSH key pairs |
| `-t ed25519` | **Type**—the cryptographic algorithm. `ed25519` is modern and secure. |
| `-C "dan@hetzner-dev"` | **Comment**—a label to help you identify this key later |

When prompted:
- **File location**: Enter `/Users/YOURNAME/.ssh/id_ed25519_hetzner` (use a specific name)
- **Passphrase**: Optional password that encrypts the key file itself (extra security)

This creates two files:
- `~/.ssh/id_ed25519_hetzner` — Private key (NEVER share this)
- `~/.ssh/id_ed25519_hetzner.pub` — Public key (goes on the server)

Copy your public key to clipboard:

```bash
cat ~/.ssh/id_ed25519_hetzner.pub | pbcopy
```

| Part | Meaning |
|------|---------|
| `cat` | Output file contents to terminal |
| `\|` | **Pipe**—send output to the next command |
| `pbcopy` | macOS command that copies input to clipboard |

### 1.4 Add SSH Key to Hetzner

1. In your project, go to **Security** → **SSH Keys**
2. Click **Add SSH Key**
3. Paste your public key
4. Name it (e.g., "macbook-main")

### 1.5 Create the Server

1. Click **Add Server**
2. **Location**: Choose closest to you (Falkenstein/Nuremberg for EU, Ashburn for US East)
3. **Image**: Ubuntu 24.04 or Debian 12 (both solid choices)
4. **Type**:
   - **CX22** (~€4/month) — 2 vCPU, 4GB RAM (good starting point)
   - **CX32** (~€8/month) — 4 vCPU, 8GB RAM (better for heavier work)
5. **Networking**: Enable both IPv4 and IPv6
6. **SSH Keys**: Select the key you just added
7. **Name**: Give it a memorable name (e.g., "dev-01")
8. Click **Create & Buy Now**

Note your server's IP address once it's created.

---

## Part 2: Initial SSH Connection (From Mac)

### 2.1 Configure SSH Client

Add the server to your SSH config for easy access:

```bash
nano ~/.ssh/config
```

| Part | Meaning |
|------|---------|
| `nano` | Simple terminal text editor |
| `~/.ssh/config` | SSH client config file—defines shortcuts for connecting to servers |

Add this block:

```
Host hetzner-dev
    HostName YOUR_SERVER_IP
    User root
    IdentityFile ~/.ssh/id_ed25519_hetzner
    IdentitiesOnly yes
```

| Setting | Meaning |
|---------|---------|
| `Host hetzner-dev` | The shortcut name you'll type (e.g., `ssh hetzner-dev`) |
| `HostName` | The actual IP address or domain |
| `User` | Username to log in as |
| `IdentityFile` | Path to the private key to use |
| `IdentitiesOnly yes` | Only use this specific key, don't try others |

Replace `YOUR_SERVER_IP` with the actual IP address.

### 2.2 First Connection

```bash
ssh hetzner-dev
```

You should connect directly without a password prompt (just your key passphrase if you set one).

If you see a host authenticity warning, type `yes` to accept.

---

## Part 3: Server Security Hardening

### 3.1 Update the System

```bash
apt update && apt upgrade -y
```

**Command breakdown:**

| Part | Meaning |
|------|---------|
| `apt` | **Advanced Package Tool**—Debian/Ubuntu's package manager for installing, updating, removing software |
| `update` | Refreshes the list of available packages from the internet (doesn't install anything yet) |
| `&&` | Run the next command only if the previous one succeeded |
| `upgrade` | Actually installs newer versions of packages you have |
| `-y` | Automatically answer "yes" to prompts (non-interactive) |

**Why both?** `update` fetches the latest package list; `upgrade` uses that list to install updates. You need both.

---

### 3.2 Create a Non-Root User

Running as root is risky—one wrong command can destroy everything. Create a regular user with sudo privileges:

```bash
adduser dan
```

| Part | Meaning |
|------|---------|
| `adduser` | Interactive tool to create a new user account (prompts for password, name, etc.) |
| `dan` | The username you're creating (use your own name) |

Then grant admin privileges:

```bash
usermod -aG sudo dan
```

| Part | Meaning |
|------|---------|
| `usermod` | **Modify user**—changes properties of an existing user account |
| `-a` | **Append**—add to group without removing from other groups |
| `-G sudo` | **Group**—the group to add them to (`sudo` = can run admin commands) |
| `dan` | The user to modify |

**Why `-aG` together?** Without `-a`, the `-G` flag would *replace* all groups. With `-a`, it *appends* to existing groups.

---

### 3.3 Set Up SSH Keys for New User

Switch to the new user:

```bash
su - dan
```

| Part | Meaning |
|------|---------|
| `su` | **Switch user**—become a different user |
| `-` | Load the user's full environment (home directory, shell config, etc.) |
| `dan` | The user to switch to |

Create the SSH directory structure:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
```

| Command | Meaning |
|---------|---------|
| `mkdir` | **Make directory** |
| `-p` | **Parents**—create parent directories if needed, no error if exists |
| `~/.ssh` | The `.ssh` folder in your home directory |
| `chmod` | **Change mode**—set file/folder permissions |
| `700` | Owner can read/write/execute; nobody else can access (required for SSH security) |

Create the authorized_keys file:

```bash
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

| Command | Meaning |
|---------|---------|
| `touch` | Create an empty file (or update timestamp if it exists) |
| `600` | Owner can read/write; nobody else can access |

Exit back to root:

```bash
exit
```

Now copy root's SSH key to the new user:

```bash
cat /root/.ssh/authorized_keys >> /home/dan/.ssh/authorized_keys
chown dan:dan /home/dan/.ssh/authorized_keys
```

| Command | Meaning |
|---------|---------|
| `cat` | Output file contents |
| `>>` | **Append redirect**—add output to end of file (vs `>` which overwrites) |
| `chown` | **Change owner**—transfer file ownership |
| `dan:dan` | New owner and group (format: `user:group`) |

### 3.4 Test New User Login

Before disabling root, verify you can log in as the new user.

Update your local SSH config on your Mac:

```
Host hetzner-dev
    HostName YOUR_SERVER_IP
    User dan
    IdentityFile ~/.ssh/id_ed25519_hetzner
    IdentitiesOnly yes
```

Test the connection:

```bash
ssh hetzner-dev
```

Verify sudo works:

```bash
sudo whoami
# Should output: root
```

### 3.5 Harden SSH Configuration

Back on the server, edit the SSH daemon config:

```bash
sudo nano /etc/ssh/sshd_config
```

| Part | Meaning |
|------|---------|
| `sudo` | **Superuser do**—run command as admin (required for system files) |
| `nano` | Simple terminal text editor |
| `/etc/ssh/sshd_config` | The SSH server's configuration file (`/etc` = system config directory) |

Make these changes (find and modify existing lines or add new ones):

```
# Disable root login
PermitRootLogin no

# Disable password authentication (key-only)
PasswordAuthentication no

# Disable empty passwords
PermitEmptyPasswords no

# Use only SSH Protocol 2
Protocol 2

# Optional: Change default port (adds obscurity, not real security)
# Port 2222

# Limit authentication attempts
MaxAuthTries 3

# Disconnect idle sessions after 10 minutes
ClientAliveInterval 300
ClientAliveCountMax 2
```

Restart SSH to apply changes:

```bash
sudo systemctl restart ssh
```

| Part | Meaning |
|------|---------|
| `systemctl` | **System control**—manages services (start, stop, restart, enable) |
| `restart` | Stop and start the service |
| `ssh` | The SSH daemon service |

**Important:** Keep your current SSH session open and test a new connection before closing it. If something is misconfigured, you could lock yourself out.

---

### 3.6 Set Up UFW Firewall

UFW = **Uncomplicated Firewall**. It controls which network connections are allowed in/out.

```bash
sudo apt install ufw -y
```

| Part | Meaning |
|------|---------|
| `apt install` | Install a package |
| `ufw` | The firewall package |
| `-y` | Auto-confirm installation |

Allow SSH connections (so you don't lock yourself out):

```bash
sudo ufw allow ssh
```

| Part | Meaning |
|------|---------|
| `ufw allow` | Permit incoming connections |
| `ssh` | Shorthand for port 22 (could also write `22/tcp`) |

Enable the firewall:

```bash
sudo ufw enable
```

Check what's allowed:

```bash
sudo ufw status
```

**Warning:** Always `allow ssh` before `enable`, or you'll lock yourself out.

---

### 3.7 Install Fail2Ban (Brute Force Protection)

Fail2Ban monitors login attempts and temporarily bans IPs that fail too many times.

```bash
sudo apt install fail2ban -y
```

Create a local config (so updates don't overwrite your changes):

```bash
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```

| Part | Meaning |
|------|---------|
| `cp` | **Copy** file |
| `jail.conf` | Default config (gets overwritten on updates) |
| `jail.local` | Your local overrides (preserved on updates) |

Edit the local config:

```bash
sudo nano /etc/fail2ban/jail.local
```

Find the `[sshd]` section and ensure it's enabled:

```
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
```

| Setting | Meaning |
|---------|---------|
| `enabled = true` | Turn on SSH protection |
| `maxretry = 3` | Ban after 3 failed attempts |
| `bantime = 3600` | Ban for 3600 seconds (1 hour) |

Restart and enable fail2ban:

```bash
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban
```

| Command | Meaning |
|---------|---------|
| `restart` | Apply new config now |
| `enable` | Start automatically on boot |

---

## Part 4: Development Environment Setup

### 4.1 Install Essential Packages

```bash
sudo apt update
sudo apt install -y \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    zsh \
    tmux \
    neovim \
    ripgrep \
    fzf \
    htop \
    tree \
    jq \
    bat
```

| Part | Meaning |
|------|---------|
| `\` | Line continuation—lets you split a long command across multiple lines |
| `-y` | Auto-confirm all prompts |

**What each package does:**

| Package | Purpose |
|---------|---------|
| `git` | Version control |
| `curl` | Transfer data from URLs (download files, make API calls) |
| `wget` | Download files from the web |
| `unzip` | Extract .zip files |
| `build-essential` | C/C++ compiler and build tools (needed to compile some packages) |
| `zsh` | A better shell than bash |
| `tmux` | Terminal multiplexer (persistent sessions) |
| `neovim` | Modern vim-based text editor |
| `ripgrep` | Super-fast code search (like grep but better) |
| `fzf` | Fuzzy finder for files and commands |
| `htop` | Interactive process viewer (like Task Manager) |
| `tree` | Display directory structure as a tree |
| `jq` | JSON processor for the command line |
| `bat` | `cat` with syntax highlighting |

---

### 4.2 Set Up Zsh with Oh My Zsh

Oh My Zsh is a framework that makes zsh easier to configure with themes and plugins.

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

| Part | Meaning |
|------|---------|
| `sh -c "..."` | Run the string inside quotes as a shell command |
| `curl` | Fetch content from a URL |
| `-f` | **Fail silently**—don't show error page HTML |
| `-s` | **Silent**—no progress bar |
| `-S` | **Show errors**—but still show errors if they happen |
| `-L` | **Follow redirects** |
| `$(...)` | Command substitution—run this command, use its output |

**In plain English:** Download the install script and run it.

Install useful plugins:

```bash
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
```

| Part | Meaning |
|------|---------|
| `git clone` | Download a git repository |
| `${ZSH_CUSTOM:-~/.oh-my-zsh/custom}` | Use `$ZSH_CUSTOM` if set, otherwise default to `~/.oh-my-zsh/custom` |

Edit `~/.zshrc` and update the plugins line:

```bash
plugins=(git zsh-autosuggestions zsh-syntax-highlighting)
```

Reload your shell config:

```bash
source ~/.zshrc
```

| Part | Meaning |
|------|---------|
| `source` | Execute a file in the current shell (applies changes without restarting) |
| `~/.zshrc` | Zsh's config file (runs every time you open a terminal) |

---

### 4.3 Configure Tmux

Tmux keeps your sessions alive even when you disconnect—essential for mobile use.

Create a basic tmux config:

```bash
nano ~/.tmux.conf
```

Add:

```
# Use Ctrl-a as prefix (easier than Ctrl-b)
unbind C-b
set -g prefix C-a
bind C-a send-prefix

# Enable mouse support
set -g mouse on

# Start window numbering at 1
set -g base-index 1
setw -g pane-base-index 1

# Increase scrollback buffer
set -g history-limit 10000

# Faster key repetition
set -s escape-time 0

# Easy split panes
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"

# Reload config
bind r source-file ~/.tmux.conf \; display "Reloaded!"

# Better colors
set -g default-terminal "screen-256color"
```

### 4.4 Tmux Basics

| Command | Action |
|---------|--------|
| `tmux` | Start new session |
| `tmux new -s work` | Start named session |
| `tmux attach` | Reattach to session |
| `tmux attach -t work` | Attach to named session |
| `tmux ls` | List sessions |
| `Ctrl-a d` | Detach from session |
| `Ctrl-a c` | New window |
| `Ctrl-a n/p` | Next/previous window |
| `Ctrl-a \|` | Split vertically |
| `Ctrl-a -` | Split horizontally |

### 4.5 Install Node.js (via nvm)

nvm = **Node Version Manager**. Lets you install and switch between Node.js versions.

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
```

| Part | Meaning |
|------|---------|
| `curl` | Download from URL |
| `-o-` | Output to stdout (the `-` means stdout) |
| `\|` | Pipe—send output to next command |
| `bash` | Run the downloaded script |

Reload your shell and install Node:

```bash
source ~/.zshrc
nvm install --lts
```

| Part | Meaning |
|------|---------|
| `nvm install` | Install a Node.js version |
| `--lts` | **Long Term Support**—the stable, recommended version |

---

### 4.6 Install Python + uv

uv is a modern, ultra-fast Python package manager (written in Rust). It replaces pip and venv.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

| Part | Meaning |
|------|---------|
| `curl` | Download from URL |
| `-L` | Follow redirects |
| `-s` | Silent (no progress bar) |
| `-S` | Show errors if they happen |
| `-f` | Fail silently on HTTP errors |
| `\| sh` | Pipe to shell and run |

Reload your shell:

```bash
source ~/.zshrc
```

**uv can manage Python versions directly:**

```bash
uv python install 3.12    # Install Python 3.12
uv python list            # See installed versions
```

**Common uv commands:**

| Task | Command |
|------|---------|
| Create virtual environment | `uv venv` |
| Install a package | `uv pip install package` |
| Install from requirements.txt | `uv pip install -r requirements.txt` |
| Run a script with dependencies | `uv run script.py` |

---

### 4.7 Configure Git

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git config --global init.defaultBranch main
```

| Part | Meaning |
|------|---------|
| `git config` | Set git configuration |
| `--global` | Apply to all repos for this user (vs just current repo) |
| `user.name` | Your name for commit messages |
| `user.email` | Your email for commit messages |
| `init.defaultBranch` | Name for the default branch when creating new repos |

---

## Part 5: Termius Setup (iPhone/iPad)

### 5.1 Install Termius

Download Termius from the App Store on your iPhone and iPad. The free version works fine for basic SSH.

### 5.2 Generate a Separate Key for Mobile (Recommended)

For better security, use a separate SSH key for mobile devices. You have two options:

**Option A: Generate on your Mac and transfer**

```bash
# On your Mac
ssh-keygen -t ed25519 -C "dan@mobile-termius"
# Save as: ~/.ssh/id_ed25519_termius
```

Then airdrop the private key (`id_ed25519_termius`) to your iPhone/iPad.

**Option B: Generate directly in Termius**

1. Open Termius
2. Go to **Keychain** (key icon)
3. Tap **+** → **Generate Key**
4. Choose **ED25519**
5. Name it (e.g., "mobile-key")
6. Copy the public key

### 5.3 Add Mobile Public Key to Server

On your server, add the mobile public key to authorized_keys:

```bash
nano ~/.ssh/authorized_keys
```

Paste the mobile public key on a new line. Save and exit.

### 5.4 Configure Termius Host

1. Open Termius
2. Tap **Hosts** → **+**
3. Fill in:
   - **Alias**: hetzner-dev
   - **Hostname**: YOUR_SERVER_IP
   - **Port**: 22 (or your custom port)
   - **Username**: dan
4. Under **Keys**, select your mobile SSH key
5. Save

### 5.5 Connect

Tap the host to connect. You should get a terminal session.

### 5.6 Termius Tips for Mobile

- **Keyboard shortcuts**: Termius has a customizable toolbar above the keyboard
- **Snippets**: Save frequently used commands (like `tmux attach`)
- **Sync**: Termius can sync hosts/keys across devices (requires account)
- **Always attach to tmux**: Make a snippet that runs `tmux attach || tmux new -s main`

---

## Part 6: Workflow Tips

### 6.1 Always Use Tmux

When you SSH in (from any device), always attach to or create a tmux session:

```bash
# Attach to existing or create new
tmux attach || tmux new -s main
```

This way:
- Your work persists if you disconnect
- You can pick up exactly where you left off on any device
- Long-running processes continue in the background

### 6.2 SSH Keep-Alive

If your connection drops frequently, add to your Mac's `~/.ssh/config`:

```
Host hetzner-dev
    # ... existing config ...
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### 6.3 Useful Aliases

Add to your server's `~/.zshrc`:

```bash
# Quick tmux attach
alias ta='tmux attach || tmux new -s main'

# System updates
alias update='sudo apt update && sudo apt upgrade -y'

# Quick directory navigation
alias ..='cd ..'
alias ...='cd ../..'
```

---

## Quick Reference

### SSH Commands

```bash
# Connect
ssh hetzner-dev

# Copy file to server
scp file.txt hetzner-dev:~/

# Copy file from server
scp hetzner-dev:~/file.txt ./

# Copy directory
scp -r folder/ hetzner-dev:~/
```

### Server Maintenance

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Check disk space
df -h

# Check memory
free -h

# Check running processes
htop

# View SSH login attempts
sudo tail -f /var/log/auth.log
```

### Firewall Management

```bash
# Check status
sudo ufw status

# Allow a port
sudo ufw allow 3000/tcp

# Remove a rule
sudo ufw delete allow 3000/tcp
```

---

## Troubleshooting

### Can't connect after changing SSH config

Use Hetzner's web console:
1. Go to your server in Hetzner Cloud Console
2. Click **Console** to get emergency access
3. Fix your SSH config

### Permission denied (publickey)

- Verify the correct key is specified
- Check `~/.ssh/authorized_keys` permissions (should be 600)
- Check `~/.ssh` directory permissions (should be 700)

### Connection timeout

- Check if firewall allows SSH: `sudo ufw status`
- Verify server is running in Hetzner console
- Try connecting with verbose mode: `ssh -v hetzner-dev`

### Tmux session lost

If tmux isn't preserving sessions after reboot, that's expected. Tmux sessions live in memory and don't survive server restarts. For persistent workspace state, consider tools like tmux-resurrect.

---

## Cost Summary

| Plan | vCPU | RAM | Storage | Monthly |
|------|------|-----|---------|---------|
| CX22 | 2 | 4 GB | 40 GB | ~€4 |
| CX32 | 4 | 8 GB | 80 GB | ~€8 |
| CX42 | 8 | 16 GB | 160 GB | ~€16 |

All plans include 20 TB traffic. Hetzner is significantly cheaper than AWS, DigitalOcean, or Azure for equivalent specs.

---

## Next Steps

- [ ] Set up your dotfiles repo and clone to server
- [ ] Configure Neovim with your preferred plugins
- [ ] Set up any language-specific toolchains
- [ ] Configure git SSH keys for GitHub/GitLab
- [ ] Consider adding a domain name and reverse proxy (nginx/caddy)
