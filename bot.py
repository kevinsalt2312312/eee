import discord
from discord.ext import commands
from discord import app_commands

TOKEN = "YOUR_BOT_TOKEN_HERE"

# IDs
TICKET_CATEGORY = 1518791516947087481
AUCTION_CATEGORY = 1519082989827657901
STAFF_ROLE_ID = 1506430627501703249

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# -----------------------------
# CHECK ROLE
# -----------------------------
def is_staff():
    async def predicate(interaction: discord.Interaction):
        role = interaction.guild.get_role(STAFF_ROLE_ID)
        return role in interaction.user.roles
    return app_commands.check(predicate)


# -----------------------------
# TICKET CREATOR
# -----------------------------
async def create_ticket(interaction: discord.Interaction, ticket_type: str):
    guild = interaction.guild
    user = interaction.user

    category_id = AUCTION_CATEGORY if ticket_type == "auction" else TICKET_CATEGORY
    category = guild.get_channel(category_id)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True)
    }

    channel = await guild.create_text_channel(
        name=f"{ticket_type}-{user.name}",
        category=category,
        overwrites=overwrites
    )

    if ticket_type == "buy":
        embed = discord.Embed(
            title="🛒 BUY TICKET",
            description="Welcome! A staff member will assist you shortly.\n\nPlease explain what you want to buy clearly.",
            color=discord.Color.green()
        )

    elif ticket_type == "sell":
        embed = discord.Embed(
            title="💸 SELL TICKET",
            description="Welcome! Please provide your item details and proof of ownership.",
            color=discord.Color.blue()
        )

    else:
        embed = discord.Embed(
            title="🏆 AUCTION TICKET",
            description="Submit your auction details below (item, starting bid, proof).",
            color=discord.Color.gold()
        )

    await channel.send(content=f"{user.mention}", embed=embed)
    await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)


# -----------------------------
# BUTTON VIEW
# -----------------------------
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Buy Ticket", style=discord.ButtonStyle.green, custom_id="buy_ticket")
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "buy")

    @discord.ui.button(label="Sell Ticket", style=discord.ButtonStyle.blurple, custom_id="sell_ticket")
    async def sell(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "sell")

    @discord.ui.button(label="Auction Ticket", style=discord.ButtonStyle.gold, custom_id="auction_ticket")
    async def auction(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "auction")


# -----------------------------
# PANEL COMMAND
# -----------------------------
@bot.tree.command(name="panel", description="Send ticket panel")
@is_staff()
async def panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎟️ TICKET SYSTEM",
        description=(
            "Choose an option below:\n\n"
            "🛒 Buy Items\n"
            "💸 Sell Items\n"
            "🏆 Start Auctions\n\n"
            "All transactions are handled securely inside tickets."
        ),
        color=discord.Color.dark_teal()
    )

    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Panel sent!", ephemeral=True)


# -----------------------------
# CLOSE COMMAND
# -----------------------------
@bot.tree.command(name="close", description="Close a ticket")
@is_staff()
async def close(interaction: discord.Interaction):
    await interaction.channel.send("Closing ticket...")
    await interaction.channel.delete()


# -----------------------------
# BAN COMMAND
# -----------------------------
@bot.tree.command(name="ban", description="Ban a user")
@is_staff()
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"🔨 {user} banned. Reason: {reason}")


# -----------------------------
# READY
# -----------------------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


bot.run(TOKEN)
