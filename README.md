# Discord All-in-One Bot 🤖

A powerful Discord bot with moderation tools, invite tracking, and giveaway system. Features include auto-moderation, member tracking, and interactive giveaways with customizable requirements.

## ✨ Features

### 🛡️ Moderation Tools
- **Message Management**: Bulk delete messages
- **User Management**: Kick, ban, and timeout members
- **Warning System**: Track user warnings
- **Role-based Protection**: Respects role hierarchy

### 📊 Invite Tracking
- **Automatic Tracking**: Monitors who invites new members
- **Personal Stats**: Check your own or others' invite counts
- **Leaderboard**: See top inviters on your server

### 🎉 Giveaway System
- **Customizable Giveaways**: Set duration, requirements, and roles
- **Interactive Participation**: Join via button clicks
- **Smart Requirements**: Minimum invites and role requirements
- **Automatic Winner Selection**: Fair random selection

### ⚙️ Additional Features
- **Auto-Role**: Automatically assign roles to new members
- **Slash Commands**: Modern Discord slash command interface
- **Persistent Data**: All stats saved automatically

## 📋 Requirements

- Python 3.8 or higher
- Discord Bot Token
- Valid License Key

## 🚀 Installation

### Step 1: Download the Bot

Clone or download this repository:
```bash
git clone https://github.com/yourusername/discord-bot.git
cd discord-bot
```

### Step 2: Install Dependencies

Install required Python packages:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install discord.py python-dotenv aiohttp
```

### Step 3: Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Under "Privileged Gateway Intents", enable:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
6. Copy your bot token (keep it secret!)

### Step 4: Invite Bot to Your Server

1. Go to "OAuth2" → "URL Generator"
2. Select scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Select bot permissions:
   - ✅ Manage Messages
   - ✅ Kick Members
   - ✅ Ban Members
   - ✅ Moderate Members
   - ✅ Manage Roles
   - ✅ View Channels
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ Manage Server
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### Step 5: Configure the Bot

Create a `.env` file in the bot directory:

```env
# Your Discord Bot Token
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE

# Your License Key (contact bot developer)
LICENSE_KEY=YOUR_LICENSE_KEY_HERE

# License Server URL (provided by developer)
ADMIN_BOT_URL=https://license-server-url.com

# Optional: Auto-Role ID (right-click role → Copy ID)
AUTO_ROLE_ID=
```

**Important Notes:**
- Replace `YOUR_DISCORD_BOT_TOKEN_HERE` with your bot token
- Replace `YOUR_LICENSE_KEY_HERE` with your license key
- The `ADMIN_BOT_URL` will be provided when you purchase a license
- `AUTO_ROLE_ID` is optional - leave empty to disable auto-role feature

### Step 6: Enable Developer Mode in Discord

To copy role/user IDs:
1. Open Discord Settings
2. Go to "Advanced"
3. Enable "Developer Mode"
4. Now you can right-click roles/users and select "Copy ID"

### Step 7: Start the Bot

Run the bot:
```bash
python main.py
```

You should see:
```
🔍 Verifying license...
✅ License verified successfully!
✅ Licensed to: YourName
✅ Commands synced
✅ Bot logged in as YourBot#1234
```

## 📖 Commands Guide

### Moderation Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/purge <amount>` | Delete multiple messages (1-100) | `/purge 50` |
| `/kick @user [reason]` | Kick a user from the server | `/kick @Spammer Spamming` |
| `/ban @user [reason]` | Ban a user from the server | `/ban @Troll Harassment` |
| `/mute @user <duration>` | Timeout a user (format: 10m, 1h, 2d) | `/mute @User 30m` |
| `/warn @user [reason]` | Issue a warning to a user | `/warn @User Bad behavior` |

**Duration Formats:**
- `m` = minutes (e.g., `30m` = 30 minutes)
- `h` = hours (e.g., `2h` = 2 hours)
- `d` = days (e.g., `7d` = 7 days)

### Invite Tracking Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/invites` | Check your invite count | `/invites` |
| `/invites @user` | Check another user's invites | `/invites @Member` |
| `/topinvites` | Show top 10 inviters leaderboard | `/topinvites` |

### Giveaway Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/giveaway_start <duration> <min_invites> [role]` | Start a giveaway | `/giveaway_start 3600 5` |
| `/giveaway_end` | Manually end active giveaway | `/giveaway_end` |

**Giveaway Parameters:**
- `duration`: Time in seconds (3600 = 1 hour)
- `min_invites`: Minimum invites required to join
- `role`: Optional role requirement

**Examples:**
```
/giveaway_start 3600 0
→ 1 hour giveaway, no requirements

/giveaway_start 7200 5
→ 2 hour giveaway, 5 invites required

/giveaway_start 3600 10 @VIP
→ 1 hour giveaway, 10 invites + VIP role required
```

### Utility Commands

| Command | Description |
|---------|-------------|
| `/ping` | Check bot response time |
| `/help` | Show all available commands |

## ⚙️ Configuration

### Auto-Role Setup

To automatically assign a role to new members:

1. Create or choose a role in your server
2. Right-click the role → Copy ID
3. Add the ID to your `.env` file:
   ```env
   AUTO_ROLE_ID=1234567890123456789
   ```
4. Restart the bot

### Bot Permissions

Ensure the bot role has these permissions:
- ✅ Manage Messages (for `/purge`)
- ✅ Kick Members (for `/kick`)
- ✅ Ban Members (for `/ban`)
- ✅ Moderate Members (for `/mute`)
- ✅ Manage Roles (for auto-role)
- ✅ Manage Server (for invite tracking)

**Important:** The bot's role must be **higher** than roles it manages!

## 🔧 Troubleshooting

### Bot doesn't start

**Problem:** License verification fails
- **Solution:** Check your `LICENSE_KEY` in `.env` is correct
- **Solution:** Verify `ADMIN_BOT_URL` is correct
- **Solution:** Contact bot developer to verify license status

**Problem:** "Invalid token"
- **Solution:** Check your `DISCORD_TOKEN` is correct and copied properly
- **Solution:** Regenerate token in Discord Developer Portal if needed

### Commands don't appear

**Problem:** Slash commands not showing
- **Solution:** Wait up to 1 hour for Discord to sync commands globally
- **Solution:** Kick and re-invite the bot to force command sync
- **Solution:** Check bot has `applications.commands` scope

### Invite tracking not working

**Problem:** Invites not being tracked
- **Solution:** Ensure bot has "Manage Server" permission
- **Solution:** Bot must be online when new members join
- **Solution:** Restart bot to rebuild invite cache

### Moderation commands failing

**Problem:** "You cannot moderate this user"
- **Solution:** Check role hierarchy - bot role must be higher
- **Solution:** Bot cannot moderate server owner
- **Solution:** Verify bot has required permissions

### Giveaway issues

**Problem:** Can't start giveaway
- **Solution:** Only one giveaway can run at a time
- **Solution:** End current giveaway first with `/giveaway_end`

**Problem:** Button not working
- **Solution:** Check if user meets requirements (invites/role)
- **Solution:** User can only join once per giveaway

## 📁 Data Files

The bot creates these files automatically:
- `invites.json` - Stores invite counts
- `giveaway.json` - Stores active giveaway data
- `warnings.json` - Stores user warnings

**Don't delete these files** while the bot is running or you'll lose data!

## 🔒 Security & Privacy

- License keys are verified on every bot startup
- All data is stored locally on your server
- No data is sent to third parties (except license verification)
- Keep your `.env` file secret and never share it

## 📝 Getting a License

This bot requires a valid license to operate. 

**To purchase a license:**
1. Contact the bot developer
2. Receive your unique license key
3. Get the license server URL
4. Add both to your `.env` file

Licenses are tied to your Discord account and verified on startup.

## 🆘 Support

### Before Asking for Help

1. Check this README thoroughly
2. Verify all permissions are set correctly
3. Check the Troubleshooting section
4. Ensure your `.env` file is configured properly

### Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discord Support**: Join our support server (link in bio)
- **Email**: support@example.com

When reporting issues, include:
- Bot version
- Error messages (if any)
- Steps to reproduce the problem
- What you've already tried

## 📊 Bot Statistics

Once running, your bot will track:
- Total invites per member
- Active giveaway participants
- User warnings
- Command usage

## 🔄 Updates

To update your bot:
```bash
git pull
pip install -r requirements.txt --upgrade
```

Check the [Changelog](CHANGELOG.md) for version changes.

## ⚖️ License & Usage

This bot is licensed software. Each instance requires a valid license key.

**Allowed:**
- ✅ Use on your own Discord servers
- ✅ Customize settings via `.env`
- ✅ Share bot features with your community

**Not Allowed:**
- ❌ Redistribute the source code
- ❌ Share your license key
- ❌ Modify core bot functionality
- ❌ Use on multiple instances with one license

## 🙏 Credits

Developed with ❤️ for the Discord community

---

**Enjoy your bot!** If you encounter any issues, please refer to the troubleshooting section or contact support.
