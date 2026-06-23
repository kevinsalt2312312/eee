import discord
from discord.ext import commands
from discord import app_commands

TOKEN = "YOUR_TOKEN"

BUYSELL_CATEGORY = 1518791516947087481
AUCTION_CATEGORY = 1519082989827657901
STAFF_ROLE_ID = 1506430627501703249

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# -----------------------------
# CHECK STAFF
# -----------------------------
def is_staff(member: discord.Member):
    return any(role.id == STAFF_ROLE_ID for role in member.roles)


# -----------------------------
# CREATE TICKET
# -----------------------------
async def create_ticket(interaction, t_type):
    guild = interaction.guild
    user = interaction.user

    category = guild.get_channel(
        AUCTION_CATEGORY if t_type == "auction" else BUYSELL_CATEGORY
    )

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(view_channel=True),
    }

    channel = await guild.create_text_channel(
        name=f"{t_type}-{user.name}",
        category=category,
        overwrites=overwrites
    )

    embed = discord.Embed(
        title=f"{t_type.upper()} TICKET",
        description=f"{user.mention} a staff member will assist you shortly.",
        color=discord.Color.green()
    )

    await channel.send(embed=embed, view=TicketControlView())
    await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)


# -----------------------------
# TICKET CONTROLS
# -----------------------------
class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.claimed_by = None

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.success)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not is_staff(interaction.user):
            return await interaction.response.send_message("❌ Staff only.", ephemeral=True)

        if self.claimed_by:
            return await interaction.response.send_message(
                f"Already claimed by {self.claimed_by.mention}",
                ephemeral=True
            )

        self.claimed_by = interaction.user
        await interaction.channel.send(f"👋 Claimed by {interaction.user.mention}")
        await interaction.response.send_message("Claimed.", ephemeral=True)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not is_staff(interaction.user):
            return await interaction.response.send_message("❌ Staff only.", ephemeral=True)

        await interaction.response.send_message("Closing ticket...", ephemeral=True)
        await interaction.channel.delete()


# -----------------------------
# PANELS (ONLY 1 BUTTON EACH)
# -----------------------------
class BuyPanel(discord.ui.View):
    @discord.ui.button(label="Request Buy", style=discord.ButtonStyle.success)
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "buy")


class SellPanel(discord.ui.View):
    @discord.ui.button(label="Request Sell", style=discord.ButtonStyle.primary)
    async def sell(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "sell")


class AuctionPanel(discord.ui.View):
    @discord.ui.button(label="Start Auction", style=discord.ButtonStyle.danger)
    async def auction(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "auction")


# -----------------------------
# SLASH COMMANDS
# -----------------------------
@bot.tree.command(name="buypanel")
@app_commands.checks.has_role(STAFF_ROLE_ID)
async def buypanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🛒 BUY PANEL",
        description="Click below to request a buy ticket.",
        color=discord.Color.green()
    )

    await interaction.channel.send(embed=embed, view=BuyPanel())
    await interaction.response.send_message("Buy panel sent.", ephemeral=True)


@bot.tree.command(name="sellpanel")
@app_commands.checks.has_role(STAFF_ROLE_ID)
async def sellpanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="💸 SELL PANEL",
        description="Click below to request a sell ticket.",
        color=discord.Color.blue()
    )

    await interaction.channel.send(embed=embed, view=SellPanel())
    await interaction.response.send_message("Sell panel sent.", ephemeral=True)


@bot.tree.command(name="auctionpanel")
@app_commands.checks.has_role(STAFF_ROLE_ID)
async def auctionpanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🏆 AUCTION PANEL",
        description="Click below to start an auction ticket.",
        color=discord.Color.gold()
    )

    await interaction.channel.send(embed=embed, view=AuctionPanel())
    await interaction.response.send_message("Auction panel sent.", ephemeral=True)


# -----------------------------
# READY
# -----------------------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


bot.run(TOKEN)
