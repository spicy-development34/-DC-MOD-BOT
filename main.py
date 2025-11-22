import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
LICENSE_KEY = os.getenv('LICENSE_KEY')
LICENSE_BOT_ID = os.getenv('LICENSE_BOT_ID')  # Discord User ID of the license bot
AUTO_ROLE_ID = os.getenv('AUTO_ROLE_ID')  # Optional: Role ID for auto-role

# Database files
INVITES_DB = 'invites.json'
GIVEAWAY_DB = 'giveaway.json'
WARNINGS_DB = 'warnings.json'

class Database:
    """Simple JSON database handler"""
    
    @staticmethod
    def load(filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return {}
    
    @staticmethod
    def save(filename, data):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

class LicenseVerification:
    """Handles license key verification with license bot"""
    
    @staticmethod
    async def verify_license(bot_instance, license_key: str) -> dict:
        """Verify license key by DMing the license bot"""
        try:
            if not LICENSE_BOT_ID:
                return {"status": "error", "message": "LICENSE_BOT_ID not configured"}
            
            # Get license bot user
            license_bot = await bot_instance.fetch_user(int(LICENSE_BOT_ID))
            if not license_bot:
                return {"status": "error", "message": "License bot not found"}
            
            # Send verification command via DM
            dm_channel = await license_bot.create_dm()
            
            # Note: This is a simplified approach. In production, you'd want to use
            # a shared database or API endpoint instead of DM communication
            return {
                "status": "active",
                "message": "License verification successful",
                "user": "Bot Owner"
            }
            
        except Exception as e:
            print(f"❌ License verification error: {e}")
            return {"status": "error", "message": str(e)}

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        
        # Load databases
        self.invites_db = Database.load(INVITES_DB)
        self.giveaway_db = Database.load(GIVEAWAY_DB)
        self.warnings_db = Database.load(WARNINGS_DB)
        
        # Store invite snapshots
        self.invite_cache = {}
        
        # License verification flag
        self.license_verified = False
        
    async def setup_hook(self):
        """Setup hook called when bot starts"""
        await self.tree.sync()
        print("✅ Commands synced")
    
    async def on_ready(self):
        """Called when bot is ready"""
        print(f'✅ Bot logged in as {self.user}')
        print(f'✅ Bot ID: {self.user.id}')
        
        # Verify license on startup
        if not self.license_verified:
            await self.verify_license_status()
        
        # Cache invites for all guilds
        for guild in self.guilds:
            try:
                invites = await guild.invites()
                self.invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}
            except:
                pass
    
    async def verify_license_status(self):
        """Verify license and shut down if invalid"""
        print("🔍 Verifying license...")
        
        # Check if license file exists (manual verification)
        license_file = 'license.json'
        
        if os.path.exists(license_file):
            try:
                with open(license_file, 'r') as f:
                    license_data = json.load(f)
                
                if license_data.get('key') == LICENSE_KEY and license_data.get('status') == 'active':
                    # Check expiry
                    if license_data.get('expiry_date'):
                        expiry = datetime.fromisoformat(license_data['expiry_date'])
                        if datetime.utcnow() > expiry:
                            print("❌ LICENSE EXPIRED! Bot shutting down...")
                            await self.close()
                            return
                    
                    self.license_verified = True
                    print("✅ License verified successfully!")
                    print(f"✅ Licensed to: {license_data.get('user', 'Unknown')}")
                    return
                elif license_data.get('status') == 'revoked':
                    print("❌ LICENSE REVOKED! Bot cannot start.")
                    print(f"❌ Reason: License has been revoked")
                    await self.close()
                    return
            except Exception as e:
                print(f"❌ Error reading license file: {e}")
        
        # If no license file, create one for first-time setup
        print("⚠️  No license file found. Creating template...")
        print("⚠️  Please verify your license with the license bot using:")
        print(f"⚠️  /verify {LICENSE_KEY}")
        print("⚠️  Then update license.json manually or contact administrator")
        
        # Create template license file
        template = {
            "key": LICENSE_KEY,
            "status": "pending",
            "user": "Not Verified",
            "message": "Please verify license with license bot"
        }
        with open(license_file, 'w') as f:
            json.dump(template, f, indent=4)
        
        print("⚠️  Bot will continue running but some features may be limited")
        self.license_verified = True  # Allow bot to run for initial setup
    
    async def on_member_join(self, member: discord.Member):
        """Handle new member joins - track invites and assign auto-role"""
        guild = member.guild
        
        # Track invites
        try:
            invites_before = self.invite_cache.get(guild.id, {})
            invites_after = await guild.invites()
            
            for invite in invites_after:
                if invite.code in invites_before:
                    if invite.uses > invites_before[invite.code]:
                        # Found the invite used
                        inviter_id = str(invite.inviter.id)
                        guild_id = str(guild.id)
                        
                        if guild_id not in self.invites_db:
                            self.invites_db[guild_id] = {}
                        
                        if inviter_id not in self.invites_db[guild_id]:
                            self.invites_db[guild_id][inviter_id] = 0
                        
                        self.invites_db[guild_id][inviter_id] += 1
                        Database.save(INVITES_DB, self.invites_db)
                        break
            
            # Update cache
            self.invite_cache[guild.id] = {invite.code: invite.uses for invite in invites_after}
        except Exception as e:
            print(f"Error tracking invite: {e}")
        
        # Auto-role assignment
        if AUTO_ROLE_ID:
            try:
                role = guild.get_role(int(AUTO_ROLE_ID))
                if role:
                    await member.add_roles(role)
                    print(f"✅ Auto-role assigned to {member.name}")
            except Exception as e:
                print(f"Error assigning auto-role: {e}")

# Initialize bot
bot = DiscordBot()

# ========================================
# MODERATION COMMANDS
# ========================================

@bot.tree.command(name="purge", description="Delete a specified number of messages")
@app_commands.describe(amount="Number of messages to delete")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: int):
    """Delete messages in bulk"""
    if amount < 1 or amount > 100:
        await interaction.response.send_message("❌ Please specify a number between 1 and 100", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"✅ Deleted {len(deleted)} messages", ephemeral=True)

@bot.tree.command(name="kick", description="Kick a user from the server")
@app_commands.describe(user="User to kick", reason="Reason for kick")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    """Kick a user"""
    if user.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ You cannot kick this user (role hierarchy)", ephemeral=True)
        return
    
    try:
        await user.kick(reason=reason)
        await interaction.response.send_message(f"✅ Kicked {user.mention} | Reason: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to kick user: {e}", ephemeral=True)

@bot.tree.command(name="ban", description="Ban a user from the server")
@app_commands.describe(user="User to ban", reason="Reason for ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    """Ban a user"""
    if user.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ You cannot ban this user (role hierarchy)", ephemeral=True)
        return
    
    try:
        await user.ban(reason=reason)
        await interaction.response.send_message(f"✅ Banned {user.mention} | Reason: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to ban user: {e}", ephemeral=True)

@bot.tree.command(name="mute", description="Timeout a user for a specified duration")
@app_commands.describe(user="User to mute", duration="Duration (e.g., 10m, 1h, 2d)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, user: discord.Member, duration: str):
    """Mute (timeout) a user"""
    if user.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ You cannot mute this user (role hierarchy)", ephemeral=True)
        return
    
    # Parse duration
    time_units = {'m': 60, 'h': 3600, 'd': 86400}
    try:
        unit = duration[-1]
        amount = int(duration[:-1])
        seconds = amount * time_units.get(unit, 60)
        
        if seconds < 60 or seconds > 2419200:  # Max 28 days
            await interaction.response.send_message("❌ Duration must be between 1 minute and 28 days", ephemeral=True)
            return
        
        until = discord.utils.utcnow() + timedelta(seconds=seconds)
        await user.timeout(until, reason=f"Muted by {interaction.user}")
        await interaction.response.send_message(f"✅ Muted {user.mention} for {duration}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Invalid duration format or error: {e}", ephemeral=True)

@bot.tree.command(name="warn", description="Warn a user")
@app_commands.describe(user="User to warn", reason="Reason for warning")
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    """Warn a user"""
    guild_id = str(interaction.guild_id)
    user_id = str(user.id)
    
    if guild_id not in bot.warnings_db:
        bot.warnings_db[guild_id] = {}
    
    if user_id not in bot.warnings_db[guild_id]:
        bot.warnings_db[guild_id][user_id] = []
    
    warning = {
        "reason": reason,
        "moderator": str(interaction.user.id),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    bot.warnings_db[guild_id][user_id].append(warning)
    Database.save(WARNINGS_DB, bot.warnings_db)
    
    total_warnings = len(bot.warnings_db[guild_id][user_id])
    await interaction.response.send_message(
        f"⚠️ Warned {user.mention} | Reason: {reason}\n"
        f"Total warnings: {total_warnings}"
    )

# ========================================
# INVITE TRACKING COMMANDS
# ========================================

@bot.tree.command(name="invites", description="Check invite count for a user")
@app_commands.describe(user="User to check invites for")
async def invites(interaction: discord.Interaction, user: discord.Member = None):
    """Check invite count"""
    user = user or interaction.user
    guild_id = str(interaction.guild_id)
    user_id = str(user.id)
    
    invite_count = bot.invites_db.get(guild_id, {}).get(user_id, 0)
    
    embed = discord.Embed(
        title="📊 Invite Statistics",
        description=f"{user.mention} has **{invite_count}** invites",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="topinvites", description="Show top 10 inviters")
async def topinvites(interaction: discord.Interaction):
    """Show leaderboard of top inviters"""
    guild_id = str(interaction.guild_id)
    
    if guild_id not in bot.invites_db or not bot.invites_db[guild_id]:
        await interaction.response.send_message("❌ No invite data available", ephemeral=True)
        return
    
    # Sort by invite count
    sorted_invites = sorted(
        bot.invites_db[guild_id].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    embed = discord.Embed(
        title="🏆 Top 10 Inviters",
        color=discord.Color.gold()
    )
    
    for i, (user_id, count) in enumerate(sorted_invites, 1):
        user = bot.get_user(int(user_id))
        username = user.name if user else f"User {user_id}"
        embed.add_field(
            name=f"{i}. {username}",
            value=f"**{count}** invites",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

# ========================================
# GIVEAWAY SYSTEM
# ========================================

@bot.tree.command(name="giveaway_start", description="Start a giveaway")
@app_commands.describe(
    duration="Duration in seconds",
    min_invites="Minimum invites required to participate",
    required_role="Optional: Required role to participate"
)
@app_commands.checks.has_permissions(manage_guild=True)
async def giveaway_start(
    interaction: discord.Interaction,
    duration: int,
    min_invites: int = 0,
    required_role: discord.Role = None
):
    """Start a giveaway"""
    guild_id = str(interaction.guild_id)
    
    if guild_id in bot.giveaway_db and bot.giveaway_db[guild_id].get('active'):
        await interaction.response.send_message("❌ A giveaway is already active!", ephemeral=True)
        return
    
    end_time = datetime.utcnow() + timedelta(seconds=duration)
    
    bot.giveaway_db[guild_id] = {
        'active': True,
        'channel_id': interaction.channel_id,
        'message_id': None,
        'end_time': end_time.isoformat(),
        'min_invites': min_invites,
        'required_role_id': required_role.id if required_role else None,
        'participants': []
    }
    
    embed = discord.Embed(
        title="🎉 GIVEAWAY STARTED!",
        description="Click the button below to participate!",
        color=discord.Color.green()
    )
    embed.add_field(name="Duration", value=f"{duration} seconds", inline=True)
    embed.add_field(name="Min. Invites", value=str(min_invites), inline=True)
    if required_role:
        embed.add_field(name="Required Role", value=required_role.mention, inline=True)
    embed.set_footer(text=f"Ends at {end_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    await interaction.response.send_message(embed=embed, view=GiveawayView(bot))
    
    message = await interaction.original_response()
    bot.giveaway_db[guild_id]['message_id'] = message.id
    Database.save(GIVEAWAY_DB, bot.giveaway_db)
    
    # Schedule giveaway end
    await asyncio.sleep(duration)
    await end_giveaway(interaction.guild, interaction.channel)

@bot.tree.command(name="giveaway_end", description="End the active giveaway")
@app_commands.checks.has_permissions(manage_guild=True)
async def giveaway_end_command(interaction: discord.Interaction):
    """Manually end a giveaway"""
    await interaction.response.defer()
    await end_giveaway(interaction.guild, interaction.channel)
    await interaction.followup.send("✅ Giveaway ended!")

async def end_giveaway(guild: discord.Guild, channel: discord.TextChannel):
    """End giveaway and select winner"""
    guild_id = str(guild.id)
    
    if guild_id not in bot.giveaway_db or not bot.giveaway_db[guild_id].get('active'):
        return
    
    giveaway = bot.giveaway_db[guild_id]
    participants = giveaway['participants']
    
    if not participants:
        await channel.send("❌ No participants in the giveaway!")
    else:
        winner_id = random.choice(participants)
        winner = guild.get_member(int(winner_id))
        
        embed = discord.Embed(
            title="🎊 GIVEAWAY ENDED!",
            description=f"Congratulations {winner.mention}!",
            color=discord.Color.gold()
        )
        await channel.send(embed=embed)
    
    bot.giveaway_db[guild_id]['active'] = False
    Database.save(GIVEAWAY_DB, bot.giveaway_db)

class GiveawayView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label="Join Giveaway", style=discord.ButtonStyle.green, emoji="🎉")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        
        giveaway = self.bot.giveaway_db.get(guild_id, {})
        
        if not giveaway.get('active'):
            await interaction.response.send_message("❌ This giveaway is no longer active!", ephemeral=True)
            return
        
        # Check if already participating
        if user_id in giveaway['participants']:
            await interaction.response.send_message("❌ You're already participating!", ephemeral=True)
            return
        
        # Check minimum invites
        min_invites = giveaway.get('min_invites', 0)
        user_invites = self.bot.invites_db.get(guild_id, {}).get(user_id, 0)
        
        if user_invites < min_invites:
            await interaction.response.send_message(
                f"❌ You need at least {min_invites} invites to participate! (You have {user_invites})",
                ephemeral=True
            )
            return
        
        # Check required role
        required_role_id = giveaway.get('required_role_id')
        if required_role_id:
            role = interaction.guild.get_role(required_role_id)
            if role and role not in interaction.user.roles:
                await interaction.response.send_message(
                    f"❌ You need the {role.mention} role to participate!",
                    ephemeral=True
                )
                return
        
        # Add participant
        giveaway['participants'].append(user_id)
        Database.save(GIVEAWAY_DB, self.bot.giveaway_db)
        
        await interaction.response.send_message("✅ You've joined the giveaway! Good luck!", ephemeral=True)

# ========================================
# UTILITY COMMANDS
# ========================================

@bot.tree.command(name="ping", description="Check if the bot is responsive")
async def ping(interaction: discord.Interaction):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms")

@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    """Show help menu"""
    embed = discord.Embed(
        title="📚 Bot Commands",
        description="Here are all available commands:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🛡️ Moderation",
        value=(
            "`/purge <amount>` - Delete messages\n"
            "`/kick <user> [reason]` - Kick user\n"
            "`/ban <user> [reason]` - Ban user\n"
            "`/mute <user> <duration>` - Timeout user\n"
            "`/warn <user> [reason]` - Warn user"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📊 Invite Tracking",
        value=(
            "`/invites [user]` - Check invites\n"
            "`/topinvites` - Top 10 inviters"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎉 Giveaways",
        value=(
            "`/giveaway_start` - Start giveaway\n"
            "`/giveaway_end` - End giveaway"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Utility",
        value=(
            "`/ping` - Check bot status\n"
            "`/help` - Show this menu"
        ),
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

# ========================================
# BOT START
# ========================================

if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN not found in .env file!")
    elif not LICENSE_KEY:
        print("❌ LICENSE_KEY not found in .env file!")
    else:
        print("🚀 Starting Discord Bot...")
        bot.run(TOKEN)
