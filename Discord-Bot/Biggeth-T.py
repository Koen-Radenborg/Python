import nextcord
from nextcord.ext import commands
from nextcord import Activity, ActivityType
import json
import time
import random
from datetime import datetime, timedelta, timezone
import asyncio
import os

# Load and save JSON functions (same as before)
def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"players": {}}
    except json.JSONDecodeError:
        return {"players": {}}

def save_json(file_path, data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")

# Example of loading and saving with a custom file path
DATA_FILE = os.path.join(os.getcwd(), 'data.json')

# Ensure the path is correct
if not os.path.exists(DATA_FILE):
    print(f"File {DATA_FILE} does not exist. It will be created.")

# Load existing data
config = load_json(DATA_FILE)

intents = nextcord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)
farming_cooldowns = {}

def get_player_data(user_id, interaction=None):
    data = load_json(DATA_FILE)
    user_id_str = str(user_id)

    # Default stats for a new player
    default_stats = {
        "wheat": 0, "wood": 0, "money": 0,
        "stone": 0, "hardwood": 0, "iron_ore": 0, "silver_ore": 0, "gold_ore": 0, 
        "rebirths": 0, "rebirth_multiplier": 1,
        "farming_cooldown_level": 0, "wheat_upgrade_level": 0, "wood_upgrade_level": 0,
        "wheat_price_upgrade_level": 0, "wood_price_upgrade_level": 0,
        "stone_upgrade_level": 0, "hardwood_upgrade_level": 0, "iron_ore_upgrade_level": 0,
        "silver_ore_upgrade_level": 0, "gold_ore_upgrade_level": 0,
        "stone_price_upgrade_level": 0, "hardwood_price_upgrade_level": 0,
        "iron_ore_price_upgrade_level": 0, "silver_ore_price_upgrade_level": 0,
        "gold_ore_price_upgrade_level": 0, "milk_price_upgrade_level": 0, 
    }

    if user_id_str not in data["players"]:
        # Create new data for the user
        data["players"][user_id_str] = default_stats
        
        if interaction:
            data["players"][user_id_str]["username"] = interaction.user.display_name
    else:
        # Ensure all default stats are present
        for key, value in default_stats.items():
            if key not in data["players"][user_id_str]:
                data["players"][user_id_str][key] = value
        if "username" not in data["players"][user_id_str] and interaction:
            data["players"][user_id_str]["username"] = interaction.user.display_name

    # Save the updated data
    save_json(DATA_FILE, data)
    return data["players"][user_id_str], data


@client.event
async def on_ready():
    print(f"Bot is connected as {client.user}")
    activity = Activity(type=ActivityType.playing, name="Farming the lands!")
    await client.change_presence(activity=activity)

@client.slash_command(name="help", description="Show all available commands.")
async def help_command(interaction: nextcord.Interaction):
    user_id = interaction.user.id
    data = load_json("data.json")
    
    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return
    help_message = """
    **🌟 Bot Commands:**
    📝 **/register** - Register to create your account!  

    🆘 **/help** - Show this help menu!  

    👤 **/profile** - View your profile and stats!  
    💰 **/sell** - Sell your inventory items for coins!  
    📦 **/inventory** - View your inventory!  
    🏺 **/treasuresell** - ???  
    🛒 **/shop** - Buy upgrades in the shop!  
    🔧 **/upgrades** - Check out your purchased upgrades!  
    🔄 **/rebirth** - Rebirth to reset progress and get a buff!

    🌾 **/farm** - Farm to gather resources!  
    🌾 **/cow** - Check if you own a cow and produce milk!  
    🐄 **/cowshop** - Buy a cow and related upgrades in the cow shop!  
    🥛 **/milksell** - Sell your milk for coins!  

    🔥 **/streak** - Check your current and highest streak!  
    🏆 **/leaderboard** - See the top players with the most rebirths, money, or highest daily streak! 

    🎰 **/plinko** - Gamble your money for a chance to win big! (7 rebirths required to use.) 
    🪙 **/coinflip** - Flip a coin and and have a chance to win alot of money! (12 rebirths required to use.)
 

    _Use the commands wisely and have fun!_ ✨
    """
    await interaction.response.send_message(help_message)


@client.slash_command(name="register", description="Register a new player and add your stats to the game")
async def register(interaction: nextcord.Interaction):
    """Register a new player and add their default stats to the data.json file"""
    
    # Default stats for a new player (inside the /register command)
    default_stats = {
    # General player information
    "has_registered": True,
    "username": "",  # Display name, can be added later
    "total_earnings": 0,

    # Resources and upgrades
    "wheat": 0,
    "wood": 0,
    "stone": 0,
    "hardwood": 0,
    "iron_ore": 0,
    "silver_ore": 0,
    "gold_ore": 0,
    "money": 0,
    "debt": 0,
    
    # Upgrade levels
    "wheat_upgrade_level": 0,
    "wood_upgrade_level": 0,
    "stone_upgrade_level": 0,
    "hardwood_upgrade_level": 0,
    "iron_ore_upgrade_level": 0,
    "silver_ore_upgrade_level": 0,
    "gold_ore_upgrade_level": 0,
    "wheat_price_upgrade_level": 0,
    "wood_price_upgrade_level": 0,
    "stone_price_upgrade_level": 0,
    "hardwood_price_upgrade_level": 0,
    "iron_ore_price_upgrade_level": 0,
    "silver_ore_price_upgrade_level": 0,
    "gold_ore_price_upgrade_level": 0,
    
    # Rebirth & multipliers
    "rebirths": 0,
    "rebirth_multiplier": 1,

    # Rare items
    "candy": 0,
    "weed": 0,
    "rare_artifacts": 0,
    "cucumber": 0,
    "total_candy": 0,
    "total_weed": 0,
    "total_rare_artifacts": 0,
    "total_cucumber": 0,
    
    # Farming stats
    "farm_usage_count": 0,
    "farming_cooldown_level": 0,
    
    # Daily streaks and claims
    "daily_streak": 0,
    "longest_streak": 0,
    "total_claims": 0,
    "last_daily_claim": None,

    # Milk stats
    "milk": 0,
    "stored_milk": 0,
    "total_milk": 0,
    "milk_price_upgrade_level": 0,

    # Cow ownership & production status
    "cow_owned": False,
    "production_on": False,
    "cow_time_started": None,

    # Gambling stats
    "total_gambled": 0,
    "total_earned_or_lost": 0,
    "coinflip_uses": 0,

}

    user_id_str = str(interaction.user.id)  # Get the user's ID as a string

    # Load the existing data from the JSON file
    data = load_json(DATA_FILE)

    # Check if the player is already registered
    if user_id_str in data["players"]:
        player_data = data["players"][user_id_str]

        # If the player is registered but missing key data, treat it as incomplete
        if "has_registered" in player_data and player_data["has_registered"]:
            # Check if the player is fully registered (has necessary keys)
            missing_keys = [key for key, value in default_stats.items() if key not in player_data]
            
            if missing_keys:
                # Update missing keys
                for key in missing_keys:
                    player_data[key] = default_stats[key]
                
                # Save the updated data back to the JSON file
                save_json(DATA_FILE, data)
                await interaction.response.send_message(f"{interaction.user.display_name}, your data has been updated!", ephemeral=True)
            else:
                await interaction.response.send_message(f"{interaction.user.display_name}, you are already fully registered.", ephemeral=True)
        else:
            # If the player is not fully registered, update their data
            for key, value in default_stats.items():
                if key not in player_data:
                    player_data[key] = value
            player_data["username"] = interaction.user.display_name  # Ensure the username is set

            # Save the updated data back to the JSON file
            save_json(DATA_FILE, data)
            await interaction.response.send_message(f"{interaction.user.display_name}, you have been successfully registered!", ephemeral=True)
        return

    # If the player is not in the data at all, add them as a new player
    data["players"][user_id_str] = default_stats
    data["players"][user_id_str]["username"] = interaction.user.display_name  # Store their display name as the username

    # Save the updated data back to the JSON file
    save_json(DATA_FILE, data)

    # Confirm registration to the player
    await interaction.response.send_message(f"Welcome {interaction.user.display_name}! You have been successfully registered.", ephemeral=True)


# Enforce user registration check for all commands
def is_registered(user_id, data):
    """Check if a user has registered."""
    user_id_str = str(user_id)
    if user_id_str in data["players"]:
        return data["players"][user_id_str].get("has_registered", False)
    return False

# Enforce user isn't banned for all commands
# To ban a user, add the key below to the user's data.
# "banned": true
def is_banned(user_id, data):
    """Check if a user is banned."""
    user_id_str = str(user_id)
    return data["players"].get(user_id_str, {}).get("banned", False)


# Farm command
@client.slash_command(name="farm", description="Farm resources!")
async def farm(interaction: nextcord.Interaction):
    user_id = interaction.user.id
    data = load_json("data.json")
    
    # Check if the user is registered
    if not is_registered(user_id, data):
        await interaction.response.send_message("⚠️ You need to register first! Please use `/register` to create an account.", ephemeral=True)
        return
    
    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return
    
   
    
    player_data = data["players"][str(user_id)]
    current_time = int(time.time())

    # Track farm usage
    player_data["farm_usage_count"] = player_data.get("farm_usage_count", 0) + 1

    cooldown_time = max(1, 5 - (player_data["farming_cooldown_level"] * 0.2))

    if user_id in farming_cooldowns and current_time - farming_cooldowns[user_id] < cooldown_time:
        time_left = round(cooldown_time - (current_time - farming_cooldowns[user_id]), 1)
        await interaction.response.send_message(f"⏳ Wait {time_left}s before farming again.", ephemeral=True)
        return
    
    wheat = int((random.randint(1, 10) + player_data["wheat_upgrade_level"] // 5) * player_data["rebirth_multiplier"]) + (player_data["wheat_upgrade_level"] * 2)
    wood = int((random.randint(0, 4) + player_data["wood_upgrade_level"] // 5) * player_data["rebirth_multiplier"]) + (player_data["wood_upgrade_level"] * 2)

    # Apply multiplier and upgrade levels to resources that are unlocked based on rebirth count
    stone = int((random.randint(0, 2) + player_data["stone_upgrade_level"] // 5) * player_data["rebirth_multiplier"]) + (player_data["stone_upgrade_level"] * 2) if player_data["rebirths"] >= 5 else 0
    hardwood = int((random.randint(0, 2) + player_data["hardwood_upgrade_level"] // 5) * player_data["rebirth_multiplier"]) + (player_data["hardwood_upgrade_level"] * 2) if player_data["rebirths"] >= 10 else 0
    iron_ore = int((random.randint(0, 2) + player_data["iron_ore_upgrade_level"] // 5) * player_data["rebirth_multiplier"]) + (player_data["iron_ore_upgrade_level"] * 2) if player_data["rebirths"] >= 15 else 0
    silver_ore = int((random.randint(0, 1) + player_data["silver_ore_upgrade_level"] // 5) * player_data["rebirth_multiplier"]) + (player_data["silver_ore_upgrade_level"] * 2) if player_data["rebirths"] >= 20 else 0
    gold_ore = int((random.randint(0, 1) + player_data["gold_ore_upgrade_level"] // 5) * player_data["rebirth_multiplier"]) + (player_data["gold_ore_upgrade_level"] * 2) if player_data["rebirths"] >= 25 else 0



    # Rare item drops
    rare_artifact = 1 if random.randint(1, 1000) == 1 else 0
    candy = 1 if random.randint(1, 250) == 1 else 0
    weed = 1 if random.randint(1, 500) == 1 else 0
    cucumber = 1 if random.randint(1, 100) == 1 else 0

    # Update rare items in player data
    if rare_artifact:
        player_data["total_rare_artifacts"] = player_data.get("total_rare_artifacts", 0) + 1
    if candy:
        player_data["total_candy"] = player_data.get("total_candy", 0) + 1
    if weed:
        player_data["total_weed"] = player_data.get("total_weed", 0) + 1
    if cucumber:
        player_data["total_cucumber"] = player_data.get("total_cucumber", 0) + 1

    player_data["rare_artifacts"] = player_data.get("rare_artifacts", 0) + rare_artifact
    player_data["candy"] = player_data.get("candy", 0) + candy
    player_data["weed"] = player_data.get("weed", 0) + weed
    player_data["cucumber"] = player_data.get("cucumber", 0) + cucumber

    # Update resources in player data
    player_data["wheat"] += wheat
    player_data["wood"] += wood
    player_data["stone"] += stone
    player_data["hardwood"] += hardwood
    player_data["iron_ore"] += iron_ore
    player_data["silver_ore"] += silver_ore
    player_data["gold_ore"] += gold_ore

    farming_cooldowns[user_id] = current_time
    save_json("data.json", data)

    # Construct response message dynamically
    resources = {
        "🌾 Wheat": (wheat, player_data["wheat"]),
        "🪵 Wood": (wood, player_data["wood"]),
        "🪨 Stone": (stone, player_data["stone"]),
        "🌲 Hardwood": (hardwood, player_data["hardwood"]),
        "⛏️ Iron Ore": (iron_ore, player_data["iron_ore"]),
        "🥈 Silver Ore": (silver_ore, player_data["silver_ore"]),
        "🥇 Gold Ore": (gold_ore, player_data["gold_ore"]),
    }

    resource_message = "\n".join(
    [f"**{name}:** {amount} (*Total:* {total})" for name, (amount, total) in resources.items() if amount > 0]
)

    # Handle rare item drops with both current and total amounts
    rare_items = []
    if cucumber:
        rare_items.append(f"🥒 **Wow! You found Larry the Cucumber! How the fuck can he talk..** \n   **Current Amount:** {player_data['cucumber']} | **Total cucumber Found:** {player_data['total_cucumber']}")
    if candy:
        rare_items.append(f"🍬 **Nice!! You found some Candy!** \n   **Current Amount:** {player_data['candy']} | **Total Candy Found:** {player_data['total_candy']}")
    if weed:
        rare_items.append(f"🍃 **Congratulations!!! You found some Weed!** \n   **Current Amount:** {player_data['weed']} | **Total Weed Found:** {player_data['total_weed']}")
    if rare_artifact:
        rare_items.append(f"🎉 **OH MY GOD!!!!! You found a Rare Artifact!** 🏺 \n   **Current Amount:** {player_data['rare_artifacts']} | **Total Rare Artifacts Found:** {player_data['total_rare_artifacts']}")

    # Track total farming usage
    total_farmed_message = f"\n🚜 **Total Times Farmed:** {player_data['farm_usage_count']}"

    # Construct final message
    message = "🚜 **You gathered:**\n\n" + resource_message if resource_message else "😢 You didn't gather any resources!"
    if rare_items:
        message += "\n\n" + "\n".join(rare_items)


    # Append total times farmed at the bottom
    message += "\n" + total_farmed_message

    await interaction.response.send_message(message, ephemeral=True)


# Cow command
@client.slash_command(name="cow", description="Collect milk from your cow!")
async def cow(interaction: nextcord.Interaction):
    user_id = interaction.user.id
    data = load_json("data.json")
    
    # Check if the user is registered
    if not is_registered(user_id, data):
        await interaction.response.send_message("⚠️ You need to register first! Please use `/register` to create an account.", ephemeral=True)
        return
    
    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return

    player_data = data["players"][str(user_id)]

    # Initialize total_milk if it doesn't exist
    if "total_milk" not in player_data:
        player_data["total_milk"] = 0

    if not player_data.get("cow_owned", False):
        await interaction.response.send_message("❌ You don't have a cow! It costs 50,000 coins.", ephemeral=True)
        return

    # Ensure "stored_milk" exists
    if "stored_milk" not in player_data:
        player_data["stored_milk"] = 0

    # Ensure "production_on" exists
    if "production_on" not in player_data:
        player_data["production_on"] = False

    # Ensure "cow_time_started" exists
    if "cow_time_started" not in player_data:
        player_data["cow_time_started"] = time.time()

    save_json("data.json", data)  # Save updates

    class MilkCollectView(nextcord.ui.View):
        def __init__(self):
            super().__init__()

            # Update button color and text dynamically
            button_label = "Stop Production" if player_data["production_on"] else "Start Producing"
            button_style = nextcord.ButtonStyle.red if player_data["production_on"] else nextcord.ButtonStyle.blurple

            self.start_stop_button = nextcord.ui.Button(label=button_label, style=button_style, row=0)
            self.start_stop_button.callback = self.start_stop_production  # Bind button action

            self.collect_button = nextcord.ui.Button(label="Collect Milk", style=nextcord.ButtonStyle.green, row=1)
            self.collect_button.callback = self.collect_milk  # Bind button action

            self.add_item(self.start_stop_button)
            self.add_item(self.collect_button)

        async def start_stop_production(self, interaction: nextcord.Interaction):
            player_data["production_on"] = not player_data["production_on"]
            save_json("data.json", data)

            if player_data["production_on"]:
                player_data["cow_time_started"] = time.time()  # Reset timer when starting
                await interaction.response.send_message("✅ Milk production has started!", ephemeral=True)
                asyncio.create_task(produce_milk(user_id))  # Start background task
            else:
                await interaction.response.send_message("❌ Milk production has been stopped.", ephemeral=True)

            # Instead of editing interaction.message, send a new response
            await interaction.followup.send(
                content=f"🥛 Your cow has produced {player_data['stored_milk']} milk. Click the button to collect or stop production.",
                view=MilkCollectView(),
                ephemeral=True
            )

        async def collect_milk(self, interaction: nextcord.Interaction):
            await interaction.response.defer()  # Acknowledge the interaction first

            collected_milk = player_data["stored_milk"]
            player_data["milk"] += collected_milk
            player_data["total_milk"] += collected_milk  # Increment total milk collected
            player_data["stored_milk"] = 0
            player_data["cow_time_started"] = time.time()

            save_json("data.json", data)

            # Send a follow-up message with the updated milk count and no buttons (view=None)
            await interaction.followup.send(
                content=f"✅ You collected {collected_milk} milk! Now you have {player_data['milk']} milk.",
                ephemeral=True
            )

            # Send another follow-up with updated status and the buttons again
            await interaction.followup.send(
                content=f"🥛 Your cow has produced {player_data['stored_milk']} milk. Click the button to collect or start production.",
                view=MilkCollectView(),  # This will display the buttons again
                ephemeral=True
            )

    # ⏳ Background Milk Production Task (defined inside the command)
    async def produce_milk(user_id):
        while True:
            await asyncio.sleep(30)  # Wait 30 seconds

            player_data, data = get_player_data(user_id)

            if not player_data["production_on"]:
                break  # Stop if production is turned off

            if player_data["stored_milk"] >= 300:
                player_data["production_on"] = False  # Stop when full
                save_json("data.json", data)
                break  

            player_data["stored_milk"] += 1
            save_json("data.json", data)  # Save progress

    # Create the MilkCollectView instance and display the buttons to the user
    await interaction.response.send_message(
        content=f"🥛 Your cow has produced {player_data['stored_milk']} milk. Click the button to collect or start production.",
        view=MilkCollectView(),
        ephemeral=True
    )


@client.slash_command(name="inventory", description="Check your current resources.")
async def inventory(interaction: nextcord.Interaction):
    user_id = interaction.user.id

    # Check if the user has registered
    data = load_json("data.json")
    if not is_registered(user_id, data):
        await interaction.response.send_message(
            "⚠️ You need to register first! Please use `/register` to create an account.",
            ephemeral=True
        )
        return
    
    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return

    # Fetch the player data
    player_data, _ = get_player_data(user_id)

    inventory_items = {
        "🌾 **Wheat:**": player_data.get("wheat", 0),
        "🪵 **Wood:**": player_data.get("wood", 0),
        "🪨 **Stone:**": player_data.get("stone", 0),
        "🌳 **Hardwood:**": player_data.get("hardwood", 0),
        "⛏ **Iron Ore:**": player_data.get("iron_ore", 0),
        "🥈 **Silver Ore:**": player_data.get("silver_ore", 0),
        "🏆 **Gold Ore:**": player_data.get("gold_ore", 0),
    }

    # Filter out items with a value of 0 (excluding money)
    filtered_items = [f"{icon} {amount}" for icon, amount in inventory_items.items() if amount > 0]

    # Always show milk if player has it
    if player_data.get("milk", 0) > 0:
        filtered_items.append(f"\n🥛 **Milk:** {player_data['milk']} \n")

    # Always show money
    money_display = f"💰 **Money:** {player_data.get('money', 0)}"

    # Always show debt if player has any
    if player_data.get("debt", 0) > 0:
        money_display += f" | 💸 **Debt:** {player_data['debt']}"
    
    # Check for rare artifacts
    if player_data.get("rare_artifacts", 0) > 0:
        filtered_items.append(f"🏺 **Rare Artifacts:** {player_data['rare_artifacts']}")

    # Check for cucumber
    if player_data.get("cucumber", 0) > 0:
        filtered_items.append(f"🥒 **Larry the MF Cucumbers:** {player_data['cucumber']}")
        
    # Check for candy
    if player_data.get("candy", 0) > 0:
        filtered_items.append(f"🍬 **Candy:** {player_data['candy']}")

    # Check for weed
    if player_data.get("weed", 0) > 0:
        filtered_items.append(f"🍃 **Weed:** {player_data['weed']}")

    # If no resources but money exists
    if not filtered_items:
        await interaction.response.send_message(
            f"📦 **Inventory** 📦\n\n🛑 Your inventory is empty! Try using `/farm` to gather some resources.\n\n{money_display}",
            ephemeral=True
        )
        return

    # Construct the message with a title, resources, and money
    message = f"📦 **Inventory** 📦\n\n" + "\n".join(filtered_items) + f"\n\n{money_display}"
    await interaction.response.send_message(message, ephemeral=True)


@client.slash_command(name="profile", description="View your profile or look up another player's stats.")
async def profile(interaction: nextcord.Interaction, user: str = None):
    try:
        data = load_json("data.json")  # Load data.json at the start
        user_id = interaction.user.id


        if is_banned(user_id, data):
            await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
            return

        # Determine the target user
        if user is None:
            target_user = interaction.user
            user_id = target_user.id
        else:
            if user.isdigit():
                user_id = int(user)
                target_user = None
            else:
                target_user = await client.fetch_user(int(user.strip("<@!>")))
                user_id = target_user.id if target_user else None

        if user_id is None:
            await interaction.response.send_message("⚠️ Invalid user! Please mention a user or enter a valid Discord ID.", ephemeral=True)
            return

        # Check if the user is registered
        if not is_registered(user_id, data):
            await interaction.response.send_message("⚠️ You need to register first! Please use `/register` to create an account.", ephemeral=True)
            return

        # Fetch player data
        player_data = data["players"][str(user_id)]

        # Extract values safely to prevent missing key errors
        player_data.setdefault("total_earnings", 0)
        player_data.setdefault("milk", 0)
        player_data.setdefault("milk_price_upgrade_level", 0)
        player_data.setdefault("rare_artifacts", 0)
        player_data.setdefault("total_rare_artifacts", 0)
        player_data.setdefault("cucumber", 0)
        player_data.setdefault("total_cucumber", 0)
        player_data.setdefault("candy", 0)
        player_data.setdefault("total_candy", 0)
        player_data.setdefault("weed", 0)
        player_data.setdefault("total_weed", 0)
        player_data.setdefault("daily_streak", 0)
        player_data.setdefault("longest_streak", 0)
        player_data.setdefault("total_claims", 0)
        player_data.setdefault("farm_usage_count", 0)
        player_data.setdefault("debt", 0)
        player_data.setdefault("total_earned_or_lost", 0)
        player_data.setdefault("total_gambled", 0)
        player_data.setdefault("coinflip_uses", 0)

        # Calculate total upgrades
        total_upgrades = sum([
            player_data.get("farming_cooldown_level", 0),
            player_data.get("wheat_upgrade_level", 0),
            player_data.get("wood_upgrade_level", 0),
            player_data.get("stone_upgrade_level", 0),
            player_data.get("hardwood_upgrade_level", 0),
            player_data.get("iron_ore_upgrade_level", 0),
            player_data.get("silver_ore_upgrade_level", 0),
            player_data.get("gold_ore_upgrade_level", 0),
            player_data.get("wheat_price_upgrade_level", 0),
            player_data.get("wood_price_upgrade_level", 0),
            player_data.get("stone_price_upgrade_level", 0),
            player_data.get("hardwood_price_upgrade_level", 0),
            player_data.get("iron_ore_price_upgrade_level", 0),
            player_data.get("silver_ore_price_upgrade_level", 0),
            player_data.get("gold_ore_price_upgrade_level", 0),
            player_data.get("milk_price_upgrade_level", 0),
        ])

        if player_data.get("cow_owned", False):
            total_upgrades += 1

        # Upgrade formatting function
        def format_upgrade(name, level, effect):
            return f"🔹 **{name}:** {level} ({effect})" if level > 0 else ""

        # List of upgrades, divided into categories
        cow_upgrades = [
            f"🐄 **Cow Purchased:** Yes" if player_data.get("cow_owned", False) else "",
        ]
        farming_cooldown_upgrades = [
            format_upgrade("Farming Cooldown", player_data.get("farming_cooldown_level", 0), f"-{0.2 * player_data.get('farming_cooldown_level', 0):.1f}s cooldown"),
        ]
        normal_upgrades = [
            format_upgrade("Wheat Upgrade", player_data.get("wheat_upgrade_level", 0), f"+{player_data.get('wheat_upgrade_level', 0) * 2} wheat per farm"),
            format_upgrade("Wood Upgrade", player_data.get("wood_upgrade_level", 0), f"+{player_data.get('wood_upgrade_level', 0) * 2} wood per farm"),
            format_upgrade("Stone Upgrade", player_data.get("stone_upgrade_level", 0), f"+{player_data.get('stone_upgrade_level', 0) * 2} stone per farm"),
            format_upgrade("Hardwood Upgrade", player_data.get("hardwood_upgrade_level", 0), f"+{player_data.get('hardwood_upgrade_level', 0) * 2} hardwood per farm"),
            format_upgrade("Iron Ore Upgrade", player_data.get("iron_ore_upgrade_level", 0), f"+{player_data.get('iron_ore_upgrade_level', 0) * 2} iron ore per farm"),
            format_upgrade("Silver Ore Upgrade", player_data.get("silver_ore_upgrade_level", 0), f"+{player_data.get('silver_ore_upgrade_level', 0) * 2} silver ore per farm"),
            format_upgrade("Gold Ore Upgrade", player_data.get("gold_ore_upgrade_level", 0), f"+{player_data.get('gold_ore_upgrade_level', 0) * 2} gold ore per farm"),
        ]

        rebirth_multiplier = player_data.get("rebirth_multiplier", 1.0)  # Default to 1.0 if no multiplier

        price_upgrades = [
            format_upgrade("Wheat Price Upgrade", player_data.get("wheat_price_upgrade_level", 0), 
                        f"Sell value: {int((1 + (player_data.get('wheat_price_upgrade_level', 0) * 2)) * rebirth_multiplier)} coins per wheat"),
            format_upgrade("Wood Price Upgrade", player_data.get("wood_price_upgrade_level", 0), 
                        f"Sell value: {int((5 + (player_data.get('wood_price_upgrade_level', 0) * 3)) * rebirth_multiplier)} coins per wood"),
            format_upgrade("Stone Price Upgrade", player_data.get("stone_price_upgrade_level", 0), 
                        f"Sell value: {int((25 + (player_data.get('stone_price_upgrade_level', 0) * 10)) * rebirth_multiplier)} coins per stone"),
            format_upgrade("Hardwood Price Upgrade", player_data.get("hardwood_price_upgrade_level", 0), 
                        f"Sell value: {int((100 + (player_data.get('hardwood_price_upgrade_level', 0) * 20)) * rebirth_multiplier)} coins per hardwood"),
            format_upgrade("Iron Ore Price Upgrade", player_data.get("iron_ore_price_upgrade_level", 0), 
                        f"Sell value: {int((300 + (player_data.get('iron_ore_price_upgrade_level', 0) * 35)) * rebirth_multiplier)} coins per iron ore"),
            format_upgrade("Silver Ore Price Upgrade", player_data.get("silver_ore_price_upgrade_level", 0), 
                        f"Sell value: {int((750 + (player_data.get('silver_ore_price_upgrade_level', 0) * 45)) * rebirth_multiplier)} coins per silver ore"),
            format_upgrade("Gold Ore Price Upgrade", player_data.get("gold_ore_price_upgrade_level", 0), 
                        f"Sell value: {int((2000 + (player_data.get('gold_ore_price_upgrade_level', 0) * 120)) * rebirth_multiplier)} coins per gold ore"),
            format_upgrade("Milk Price Upgrade", player_data.get("milk_price_upgrade_level", 0), 
                        f"Sell value: {int((150 * (1.2 ** player_data.get('milk_price_upgrade_level', 0)) - 150) * rebirth_multiplier)} coins per milk"),
]

        # Combine all the categories with extra space between each group
        upgrades = (
    "\n".join([upgrade for upgrade in cow_upgrades if upgrade]) + "\n\n" +
    "\n".join([upgrade for upgrade in farming_cooldown_upgrades if upgrade]) + "\n\n" +
    "\n".join([upgrade for upgrade in normal_upgrades if upgrade]) + "\n\n" +
    "\n".join([upgrade for upgrade in price_upgrades if upgrade])
)


        # Now 'upgrades' contains all the upgrades with space between each group
        upgrades_text = upgrades if upgrades else "No upgrades purchased yet."

        profile_name = target_user.display_name if target_user else f"User ID: {user_id}"

        message = f"""
📜 **__{profile_name}'s Profile__** 📜

🔄 **Rebirths:** `{player_data.get("rebirths", 0)}` \n✖️(**Multiplier:** `{player_data.get("rebirth_multiplier", 1.0):.2f}x`)

💰 **__Money and Net Worth__** 💰

💰 **Money:** `{player_data.get("money", 0)}` coins
💸 **Debt:** `{player_data.get("debt", 0)}` coins
💎 **Total Money Earned:** `{player_data.get("total_earnings", 0)}` coins


🛠 **Total Upgrades:** `{total_upgrades}`

✨ **__Upgrades__** ✨

{upgrades_text}

📦 **__Inventory__** 📦
"""

        # Dynamically adding resources only if they exist
        resources = {
            "🌾 Wheat": player_data.get("wheat", 0),
            "🪵 Wood": player_data.get("wood", 0),
            "🪨 Stone": player_data.get("stone", 0),
            "🌳 Hardwood": player_data.get("hardwood", 0),
            "⛏ Iron Ore": player_data.get("iron_ore", 0),
            "🥈 Silver Ore": player_data.get("silver_ore", 0),
            "🏆 Gold Ore": player_data.get("gold_ore", 0),
            "🥛 Milk": player_data.get("milk", 0),
        }

        resource_text = "\n".join(f"{name}: `{amount}`" for name, amount in resources.items() if amount > 0)

        if resource_text:
            message += resource_text + "\n"
# Gambling stats section (only show if any gambling-related values are greater than 0)
        if player_data.get("total_earned_or_lost", 0) > 0 or player_data.get("total_gambled", 0) > 0 or player_data.get("coinflip_uses", 0) > 0:
            message += f"""
🎲**__Gambling__** 🎲

💰 **Total Earned/Lost:** `{player_data.get("total_earned_or_lost", 0)}`
💸 **Total Plinko Games Played:** `{player_data.get("total_gambled", 0)}`
🎰 **Coins flipped:** `{player_data.get("coinflip_uses", 0)}`
"""
        # Always show streak info
        message += f"""
🏆 **__Streak Info__** 🏆

📅 **Current Streak:** `{player_data.get("daily_streak", 0)}` days  
🏅 **Longest Streak:** `{player_data.get("longest_streak", 0)}` days  
🔄 **Total Daily Claims:** `{player_data.get("total_claims", 0)}` times  

🌾 **Times Farmed:** `{player_data.get('farm_usage_count', 0)}`
"""


        # Rare items section
        if player_data.get("rare_artifacts", 0) > 0 or player_data.get("cucumber", 0) > 0 or player_data.get("candy", 0) > 0 or player_data.get("weed", 0) > 0:
            message += "**\n💎 Current Rare Items**\n\n"
            
            if player_data.get("rare_artifacts", 0) > 0:
                message += f"🏺 **Rare Artifacts:** `{player_data['rare_artifacts']}`\n"

            if player_data.get("cucumber", 0) > 0:
                message += f"🥒 **Larry the Cucumbers:** `{player_data['cucumber']}`\n"

            if player_data.get("candy", 0) > 0:
                message += f"🍬 **Candy:** `{player_data['candy']}`\n"
            
            if player_data.get("weed", 0) > 0:
                message += f"🍃 **Weed:** `{player_data['weed']}`\n\n"

        # Total rare items collected
        if player_data.get("total_rare_artifacts", 0) > 0 or player_data.get("total_cucumber", 0) > 0 or player_data.get("total_candy", 0) > 0 or player_data.get("total_weed", 0) > 0:
            message += "**\n🏆 Total Collected Rare Items**\n\n"
            
            if player_data.get("total_cucumber", 0) > 0:
                message += f"🥒 **Total Larries Found:** `{player_data['total_cucumber']}`\n"
            
            if player_data.get("total_candy", 0) > 0:
                message += f"🍬 **Total Candy Found:** `{player_data['total_candy']}`\n"
            
            if player_data.get("total_weed", 0) > 0:
                message += f"🍃 **Total Weed Found:** `{player_data['total_weed']}`\n"

            if player_data.get("total_rare_artifacts", 0) > 0:
                message += f"🏺 **Total Artifacts Found:** `{player_data['total_rare_artifacts']}`\n"

        await interaction.response.send_message(message)

    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)



@client.slash_command(name="sell", description="Sell your resources for money!")
async def sell(
    interaction: nextcord.Interaction,
    items: str = nextcord.SlashOption(
        name="items",
        description="What to sell. Type 'all' to sell everything, or specify multiple resources separated by commas.",
        required=False  # Now not required
    ),
    amounts: str = nextcord.SlashOption(
        name="amounts",
        description="Amounts to sell per item (comma-separated, or 'all' for max).",
        required=False
    )
):
    user_id = interaction.user.id

    # Load the player data from the JSON file using your existing load_json function
    data = load_json(DATA_FILE)

    # Check if the user is registered
    if not is_registered(user_id, data):
        await interaction.response.send_message("⚠️ You need to register first! Please use `/register` to create an account.", ephemeral=True)
        return
    
    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return

    player_data = data["players"].get(str(user_id))

    if "total_earnings" not in player_data:
        player_data["total_earnings"] = 0

    # Resource Prices with Upgrades (keys are title-case)
    prices = {
    "Wheat": 1 + (player_data["wheat_price_upgrade_level"] * 2),  # Reduced scaling
    "Wood": 5 + (player_data["wood_price_upgrade_level"] * 3),
    "Stone": 25 + (player_data["stone_price_upgrade_level"] * 10),
    "Hardwood": 100 + (player_data["hardwood_price_upgrade_level"] * 20), 
    "Iron Ore": 300 + (player_data["iron_ore_price_upgrade_level"] * 35),
    "Silver Ore": 750 + (player_data["silver_ore_price_upgrade_level"] * 45),
    "Gold Ore": 2000 + (player_data["gold_ore_price_upgrade_level"] * 120),
}

    # Player's inventory (keys are title-case)
    inventory = {
        "Wheat": player_data.get("wheat", 0),
        "Wood": player_data.get("wood", 0),
        "Stone": player_data.get("stone", 0),
        "Hardwood": player_data.get("hardwood", 0),
        "Iron Ore": player_data.get("iron_ore", 0),
        "Silver Ore": player_data.get("silver_ore", 0),
        "Gold Ore": player_data.get("gold_ore", 0)
    }

    # Convert all keys to lowercase for easier comparison
    prices_lower = {key.lower(): value for key, value in prices.items()}
    inventory_lower = {key.lower(): value for key, value in inventory.items()}

    # If no items are provided, sell everything
    if not items or items.lower() == "all":
        items_to_sell = prices_lower.keys()  # Sell all resources
    else:
        items_to_sell = [item.strip().lower() for item in items.split(",")]

    # If no valid items to sell
    if not items_to_sell:
        await interaction.response.send_message("⚠️ No valid items selected to sell!", ephemeral=True)
        return

    # If amounts are provided, split them; otherwise, use 'all'
    if amounts:
        amount_list = amounts.split(",")
        amount_dict = {item.strip().lower(): amt.strip() for item, amt in zip(items_to_sell, amount_list)}
    else:
        amount_dict = {item: "all" for item in items_to_sell}

    # Process each selected item
    total_earnings = 0
    sold_items = []

    for item in items_to_sell:
        if item not in inventory_lower:
            continue  # Skip invalid items

        # Get original resource name from lowercase key
        original_item_name = [key for key, value in inventory_lower.items() if key == item][0]

        if inventory_lower[item] == 0:
            continue  # Skip items the player has none of

        # Determine amount to sell
        amount = amount_dict.get(item, "all")
        amount = inventory_lower[item] if amount == "all" else min(int(amount), inventory_lower[item])

        # Calculate earnings with rebirth multiplier
        earnings = int(amount * prices_lower[item] * player_data["rebirth_multiplier"])
        player_data["total_earnings"] += earnings  # Track the total earnings
        total_earnings += earnings
        sold_items.append(f"{amount} {original_item_name}")
        player_data[original_item_name.lower().replace(" ", "_")] -= amount  # Update inventory

    # If nothing was sold
    if not sold_items:
        await interaction.response.send_message("⚠️ You have no resources to sell!", ephemeral=True)
        return

    # Now handle debt first, then add remaining money to user's balance
    debt = player_data.get("debt", 0)  # Get current debt
    if debt > 0:
        if total_earnings >= debt:
            # Pay off debt first, then add remaining money
            remaining_money = total_earnings - debt
            player_data["money"] += remaining_money  # Add remaining money after clearing debt
            player_data["debt"] = 0  # Clear the debt
            debt_cleared_message = f"Your debt of {debt} coins has been **cleared**!"
        else:
            # All earnings go to pay off the debt
            player_data["debt"] -= total_earnings
            player_data["money"] = 0  # No money left, all went to debt
            debt_cleared_message = f"Your remaining debt is **{player_data['debt']} coins**."
    else:
        # No debt, just add the money
        player_data["money"] += total_earnings
        debt_cleared_message = ""  # No debt message

    # Save the updated data back to the JSON file
    save_json(DATA_FILE, data)

    sold_list = ", ".join(sold_items)
    reward_message = (
        f"💰 You sold {sold_list} for {total_earnings} coins!\n"
        f"{debt_cleared_message}\n"  # Include debt clearing message
    )

    await interaction.response.send_message(reward_message, ephemeral=True)



@client.slash_command(name="sellmilk", description="Sell your milk for coins!")
async def sell_milk(interaction: nextcord.Interaction, amount: int = nextcord.SlashOption(name="amount", description="Amount of milk to sell", required=True)):
    user_id = interaction.user.id

    # Load the player data from the JSON file
    data = load_json(DATA_FILE)

    # Check if the user is registered
    if not is_registered(user_id, data):
        await interaction.response.send_message("⚠️ You need to register first! Please use `/register` to create an account.", ephemeral=True)
        return
    
    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return

    player_data = data["players"].get(str(user_id))

    if not player_data.get("cow_owned", False):
        await interaction.response.send_message("❌ You don't have a cow! It costs 50,000 coins.", ephemeral=True)
        return

    if player_data["milk"] == 0:
        await interaction.response.send_message("❌ You have no milk to sell!", ephemeral=True)
        return

    # Ensure the amount is valid
    amount = min(amount, player_data["milk"])
    if amount <= 0:
        await interaction.response.send_message("❌ You don't have enough milk to sell!", ephemeral=True)
        return

    # Calculate milk price with upgrades and rebirth multiplier
    milk_price = 150 + (player_data["milk_price_upgrade_level"] * 100)  # Milk price upgrade multiplier
    milk_price *= player_data["rebirth_multiplier"]  # Rebirth multiplier

    # Sell the milk
    earnings = int(amount * milk_price)  # Use int() to ensure earnings is an integer
    player_data["milk"] -= amount

    # Now handle debt first, then add remaining money to user's balance
    debt = player_data.get("debt", 0)  # Get current debt
    if debt > 0:
        if earnings >= debt:
            # Pay off debt first, then add remaining money
            remaining_money = earnings - debt
            player_data["money"] += remaining_money  # Add remaining money after clearing debt
            player_data["debt"] = 0  # Clear the debt
            debt_cleared_message = f"Your debt of {debt} coins has been **cleared**!"
        else:
            # All earnings go to pay off the debt
            player_data["debt"] -= earnings
            player_data["money"] = 0  # No money left, all went to debt
            debt_cleared_message = f"Your remaining debt is **{player_data['debt']} coins**."
    else:
        # No debt, just add the money
        player_data["money"] += earnings
        debt_cleared_message = ""  # No debt message

    # Save the updated data to the JSON file
    save_json(DATA_FILE, data)

    await interaction.response.send_message(f"💰 You sold {amount} milk for {earnings} coins!\n{debt_cleared_message}", ephemeral=True)



@client.slash_command(name="treasuresell", description="???")
async def treasuresell(
    interaction: nextcord.Interaction,
    item: str = nextcord.SlashOption(
        name="item",
        description="Choose what to sell",
        choices=["All","Cucumber", "Candy", "Weed", "Rare Artifact"],
        required=True
    ),
    amount: int = nextcord.SlashOption(
        name="amount",
        description="Number of items to sell (or type 'all' to sell everything)",
        required=False
    )
):
    user_id = interaction.user.id

    # Load the player data from the JSON file
    data = load_json(DATA_FILE)

    # Check if the user is registered
    if not is_registered(user_id, data):
        await interaction.response.send_message("⚠️ You need to register first! Please use `/register` to create an account.", ephemeral=True)
        return
    
    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return

    player_data = data["players"].get(str(user_id))

    if "total_earnings" not in player_data:
        player_data["total_earnings"] = 0

    # Prices per item
    prices = {
        "Rare Artifact": 50000,
        "Candy": 10000,
        "Weed": 25000,
        "Cucumber": 5000
    }

    # Mapping item names to correct keys in player_data
    item_keys = {
        "Rare Artifact": "rare_artifacts",
        "Candy": "candy",
        "Weed": "weed",
        "Cucumber": "cucumber"
    }

    # Player's inventory
    inventory = {key: player_data.get(item_keys[key], 0) for key in item_keys}

    total_earnings = 0
    if item == "All":
        for key, price in prices.items():
            count = inventory[key]
            if count > 0:
                # Apply rebirth multiplier only once and calculate earnings
                earnings = int(count * price * player_data["rebirth_multiplier"])
                player_data["total_earnings"] += earnings
                player_data[item_keys[key]] = 0  # Reset inventory
                total_earnings += earnings

        if total_earnings == 0:
            await interaction.response.send_message("⚠️ You have no treasures to sell!", ephemeral=True)
            return
    else:
        if item in inventory:
            if inventory[item] == 0:
                await interaction.response.send_message(f"⚠️ You have no {item}s to sell!", ephemeral=True)
                return

            # If amount is not provided or exceeds inventory, sell all available
            amount = min(amount or inventory[item], inventory[item])

            # Calculate earnings with rebirth multiplier (only applied once here)
            earnings = int(amount * prices[item] * player_data["rebirth_multiplier"])
            player_data["total_earnings"] += earnings
            player_data[item_keys[item]] -= amount  # Correctly update inventory key
            total_earnings += earnings

    # Now handle debt first, then add remaining money to user's balance
    debt = player_data.get("debt", 0)  # Get current debt
    if debt > 0:
        if total_earnings >= debt:
            # Pay off debt first, then add remaining money
            remaining_money = total_earnings - debt
            player_data["money"] += remaining_money  # Add remaining money after clearing debt
            player_data["debt"] = 0  # Clear the debt
            debt_cleared_message = f"Your debt of {debt} coins has been **cleared**!"
        else:
            # All earnings go to pay off the debt
            player_data["debt"] -= total_earnings
            player_data["money"] = 0  # No money left, all went to debt
            debt_cleared_message = f"Your remaining debt is **{player_data['debt']} coins**."
    else:
        # No debt, just add the money
        player_data["money"] += total_earnings
        debt_cleared_message = ""  # No debt message

    # Save the updated data to the JSON file
    save_json(DATA_FILE, data)

    await interaction.response.send_message(f"💰 You sold your treasures for {total_earnings} coins!\n{debt_cleared_message}", ephemeral=True)



@client.slash_command(name="upgrades", description="Check your upgrade levels and their effects.")
async def upgrades(interaction: nextcord.Interaction):
    user_id = interaction.user.id

    # Load the player data without modifying it
    data = load_json(DATA_FILE)
    
    # Check if the user is registered
    if not is_registered(user_id, data):
        await interaction.response.send_message("⚠️ You need to register first! Please use `/register` to create an account.", ephemeral=True)
        return
    
    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return

    player_data = data["players"].get(str(user_id), {})

    maxed = lambda level, max_level: f"**MAX**" if level >= max_level else f"{level}"

    # If player data is missing specific fields, assume they are 0 instead of adding them
    farming_cooldown_level = player_data.get("farming_cooldown_level", 0)
    cow_owned = player_data.get("cow_owned", False)

    # Yield Upgrades (Default to 0 if not found)
    yield_upgrades = {
        "wheat": player_data.get("wheat_upgrade_level", 0),
        "wood": player_data.get("wood_upgrade_level", 0),
        "stone": player_data.get("stone_upgrade_level", 0),
        "hardwood": player_data.get("hardwood_upgrade_level", 0),
        "iron_ore": player_data.get("iron_ore_upgrade_level", 0),
        "silver_ore": player_data.get("silver_ore_upgrade_level", 0),
        "gold_ore": player_data.get("gold_ore_upgrade_level", 0),
    }

    # Price Upgrades (Default to 0 if not found)
    price_upgrades = {
        "wheat": player_data.get("wheat_price_upgrade_level", 0),
        "wood": player_data.get("wood_price_upgrade_level", 0),
        "stone": player_data.get("stone_price_upgrade_level", 0),
        "hardwood": player_data.get("hardwood_price_upgrade_level", 0),
        "iron_ore": player_data.get("iron_ore_price_upgrade_level", 0),
        "silver_ore": player_data.get("silver_ore_price_upgrade_level", 0),
        "gold_ore": player_data.get("gold_ore_price_upgrade_level", 0),
        "milk": player_data.get("milk_price_upgrade_level", 0),
    }

    # Upgrade Effects
    cooldown_upgrade_effect = f"Reduces farming cooldown by {0.2 * farming_cooldown_level}s."
    cow_purchase_effect = "Allows you to purchase a cow to start producing milk."
    milk_price_upgrade_effect = f"Increases money from milk sales by {int(150 * (1.2 ** price_upgrades['milk']) - 150)} per milk."

    # Total Upgrades Calculation
    total_upgrades = farming_cooldown_level + cow_owned + sum(yield_upgrades.values()) + sum(price_upgrades.values())

    # Build the message
    message = f"⚙️ **Your Upgrades**\n\n"
    message += f"💡 **Total Upgrades:** {total_upgrades}\n\n"

    if farming_cooldown_level > 0:
        message += f"⏳ **Farming Cooldown Level:** {maxed(farming_cooldown_level, 20)} - {cooldown_upgrade_effect}\n\n"

    if cow_owned:
        message += f"🐄 **Cow Purchased:** ✅ - {cow_purchase_effect}\n\n"

    for resource, level in yield_upgrades.items():
        if level > 0:
            message += f"🔼 **{resource.replace('_', ' ').title()} Yield Level:** {maxed(level, 100)} - Increases {resource} yield by {2 * level} per farm.\n"

    for resource, level in price_upgrades.items():
        if level > 0:
            increase = {
                "wheat": 2, "wood": 3, "stone": 10, "hardwood": 20,
                "iron_ore": 35, "silver_ore": 45, "gold_ore": 120
            }.get(resource, 0)
            
            if resource == "milk":
                message += f"\n💰 **Milk Price Level:** {maxed(level, 100)} - {milk_price_upgrade_effect}\n"
            else:
                message += f"💰 **{resource.replace('_', ' ').title()} Price Level:** {maxed(level, 100)} - Increases money from {resource} sales by {increase * level} per unit.\n"

    await interaction.response.send_message(message, ephemeral=True)



@client.slash_command(name="rebirth", description="Rebirth to gain a multiplier, resetting upgrades and inventory.")
async def rebirth(interaction: nextcord.Interaction):
    user_id = interaction.user.id
    data = load_json("data.json")

    # Check if the user is registered
    if not is_registered(user_id, data):
        await interaction.response.send_message("⚠️ You need to register first! Please use `/register` to create an account.", ephemeral=True)
        return
    
    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return

    player_data = data["players"][str(user_id)]

    # Exponential rebirth price formula
    base_price = 100000
    growth_factor = 1.4  # Adjust this for a more moderate scaling
    rebirth_price = int(base_price * (growth_factor ** player_data["rebirths"]))

    # Round to the nearest 10
    rebirth_price = round(rebirth_price / 1000) * 1000

    # Create a view for the rebirth button
    class RebirthView(nextcord.ui.View):
        def __init__(self):
            super().__init__()

            # Disable the rebirth button if the user doesn't have enough money
            if player_data["money"] < rebirth_price:
                self.children[0].disabled = True

        @nextcord.ui.button(label=f"Rebirth (Cost: {rebirth_price} coins)", style=nextcord.ButtonStyle.green)
        async def rebirth_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            if player_data["money"] < rebirth_price:
                await interaction.response.send_message(f"❌ You need {rebirth_price} coins to rebirth.", ephemeral=True)
                return

            # Deduct the rebirth price
            player_data["money"] -= rebirth_price

            # Clear inventory and upgrades
            player_data.update({
                "money": 0, "wheat": 0, "wood": 0, "stone": 0, "hardwood": 0, "iron_ore": 0,
                "silver_ore": 0, "gold_ore": 0, "farming_cooldown_level": 0, "wheat_upgrade_level": 0,
                "wood_upgrade_level": 0, "stone_upgrade_level": 0, "hardwood_upgrade_level": 0,
                "iron_ore_upgrade_level": 0, "silver_ore_upgrade_level": 0, "gold_ore_upgrade_level": 0,
                "wheat_price_upgrade_level": 0, "wood_price_upgrade_level": 0, "stone_price_upgrade_level": 0,
                "hardwood_price_upgrade_level": 0, "iron_ore_price_upgrade_level": 0, "silver_ore_price_upgrade_level": 0,
                "gold_ore_price_upgrade_level": 0, "rare_artifacts": 0, "candy": 0, "weed": 0, "cucumber": 0,
                "cow_owned": False, "milk": 0, "stored_milk": 0, "milk_price_upgrade_level": 0,
                "production_on": False, "debt": 0
            })

            # Apply rebirth effects
            player_data["rebirths"] += 1
            player_data["rebirth_multiplier"] *= 1.1  # Apply 1.1x multiplier

            # Save the data after rebirth
            save_json("data.json", data)

            # Milestone checks
            milestone_message = ""
            milestones = {
                5: "🎉 You've reached 5 rebirths! You can now collect **stone**!",
                7: "🎉 You've reached 7 rebirths! You can now collect use the **/plinko** command!!",
                10: "🎉 You've reached 10 rebirths! You can now collect **hardwood**!",
                12: "🎉 You've reached 12 rebirths! You can now collect use the **/coinflip** command!!",
                15: "🎉 You've reached 15 rebirths! You can now collect **iron ore**!",
                20: "🎉 You've reached 20 rebirths! You can now collect **silver ore**!",
                25: "🎉 You've reached 25 rebirths! You can now collect **gold ore**!"
            }
            milestone_message = milestones.get(player_data["rebirths"], "")

            # Disable the button after rebirth
            self.children[0].disabled = True
            self.stop()

            # Confirm rebirth and the new multiplier
            await interaction.response.send_message(
                f"🔄 **You rebirthed!** New multiplier: {player_data['rebirth_multiplier']:.2f}x\n{milestone_message}",
                ephemeral=True
            )

    # Send the rebirth menu with the button
    await interaction.response.send_message(
        f"💡 **Rebirth Information:**\n\nYou currently have {player_data['rebirths']} rebirth(s). \nYour current multiplier is: {player_data['rebirth_multiplier']:.2f}x.\n\n💰 **Current Balance:** {player_data['money']} coins\n\nTo rebirth, press the button below.",
        view=RebirthView(),
        ephemeral=True
    )



@client.slash_command(name="leaderboard", description="View the top 10 players in different categories.")
async def leaderboard(interaction: nextcord.Interaction):
    data = load_json(DATA_FILE)
    user_id = interaction.user.id


    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return

    # Function to generate the leaderboard message dynamically
    def generate_leaderboard_message(category):
        # Sort players based on the selected category
        sorted_players = sorted(data["players"].items(), key=lambda x: x[1].get(category, 0), reverse=True)

        # Limit to top 10 players
        top_10 = sorted_players[:10]

        # Prepare the leaderboard message
        leaderboard_message = f"🏆 **Top 10 Players by {category.capitalize()}** 🏆\n\n"
        
        for rank in range(10):
            if rank < len(top_10):
                user_id, player_data = top_10[rank]
                username = player_data.get("username", f"Unknown User #{user_id}")
                value = player_data.get(category, 0)
            else:
                username = f"-- #{rank + 1}"
                value = 0
            
            # Add emojis for ranks
            if rank == 0:
                emoji = "🥇"
            elif rank == 1:
                emoji = "🥈"
            elif rank == 2:
                emoji = "🥉"
            else:
                emoji = "🔹"

            leaderboard_message += f"{emoji} **{rank + 1}. {username}** - {value} {category.replace('_', ' ').capitalize()}\n"

        return leaderboard_message

    # Create a view class for handling button interactions
    class LeaderboardView(nextcord.ui.View):
        def __init__(self):
            super().__init__()
            self.category = "rebirths"  # Default category is "rebirths"
        
        async def update_leaderboard(self, interaction: nextcord.Interaction):
            leaderboard_message = generate_leaderboard_message(self.category)
            await interaction.response.edit_message(content=leaderboard_message, view=self)

        # Button for "By Rebirths"
        @nextcord.ui.button(label="🏅 By Rebirths", style=nextcord.ButtonStyle.blurple, row=0)
        async def by_rebirths(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            self.category = "rebirths"
            await self.update_leaderboard(interaction)

        # Button for "By Money"
        @nextcord.ui.button(label="💰 By Money", style=nextcord.ButtonStyle.blurple, row=1)
        async def by_money(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            self.category = "money"
            await self.update_leaderboard(interaction)

        # Button for "By Daily Streak"
        @nextcord.ui.button(label="📅 By Daily Streak", style=nextcord.ButtonStyle.blurple, row=2)
        async def by_daily_streak(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            self.category = "daily_streak"
            await self.update_leaderboard(interaction)


    # Initial leaderboard message based on "rebirths"
    leaderboard_view = LeaderboardView()
    leaderboard_message = generate_leaderboard_message("rebirths")
    
    # Send the initial leaderboard message with buttons
    await interaction.response.send_message(leaderboard_message, view=leaderboard_view)



@client.slash_command(name="shop", description="Buy upgrades to improve farming efficiency!")
async def shop(interaction: nextcord.Interaction):
    user_id = interaction.user.id
    data = load_json("data.json")  # Load player data

    # Check if the user is registered
    if not is_registered(user_id, data):
        await interaction.response.send_message("⚠️ You need to register first! Please use `/register` to create an account.", ephemeral=True)
        return
    
    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return

    player_data = data["players"][str(user_id)]  # Get player data

    class ShopView(nextcord.ui.View):
        def __init__(self, message):
            super().__init__()
            self.message = message  # Store the message object for editing later

        async def purchase_upgrade(self, interaction, upgrade_key, max_level, price_func):
            if player_data[upgrade_key] >= max_level:
                await interaction.response.send_message("❌ Max level reached!", ephemeral=True)
                return

            price = price_func(player_data[upgrade_key])
            if player_data["money"] < price:
                await interaction.response.send_message("❌ Not enough money!", ephemeral=True)
                return

            # Deduct money and upgrade the stat
            player_data["money"] -= price
            player_data[upgrade_key] += 1
            save_json("data.json", data)

            # Update the message with new prices and balance
            await self.update_shop_message(interaction)

        async def update_shop_message(self, interaction):
            updated_prices = generate_shop_message(player_data)
            await self.message.edit(content=updated_prices, view=self)
            await interaction.response.defer()  # Prevents "Interaction failed" errors

        # Top Row: Cooldown Upgrade
        @nextcord.ui.button(label="🛠️ Cooldown Upgrade", style=nextcord.ButtonStyle.green, row=0)
        async def buy_cooldown(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "farming_cooldown_level", 20, cooldown_upgrade_price)

        # Row 1: Resource Yield Upgrades (blurple buttons)
        @nextcord.ui.button(label="🌾 Wheat Yield Upgrade", style=nextcord.ButtonStyle.blurple, row=1)
        async def buy_wheat_yield(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "wheat_upgrade_level", 100, wheat_upgrade_price)

        @nextcord.ui.button(label="🌲 Wood Yield Upgrade", style=nextcord.ButtonStyle.blurple, row=1)
        async def buy_wood_yield(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "wood_upgrade_level", 100, wood_upgrade_price)

        # Stone Yield Upgrade: Only show after 5 rebirths
        @nextcord.ui.button(label="⛏️ Stone Yield Upgrade", style=nextcord.ButtonStyle.blurple, row=1)
        async def buy_stone_yield(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "stone_upgrade_level", 100, stone_upgrade_price)

        # Hardwood Yield Upgrade: Only show after 10 rebirths
        @nextcord.ui.button(label="🌳 Hardwood Yield Upgrade", style=nextcord.ButtonStyle.blurple, row=1)
        async def buy_hardwood_yield(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "hardwood_upgrade_level", 100, hardwood_upgrade_price)

        # Iron Ore Yield Upgrade: Only show after 15 rebirths
        @nextcord.ui.button(label="⛏️ Iron Ore Yield Upgrade", style=nextcord.ButtonStyle.blurple, row=2)
        async def buy_iron_ore_yield(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "iron_ore_upgrade_level", 100, iron_ore_upgrade_price)

        # Silver Ore Yield Upgrade: Only show after 20 rebirths
        @nextcord.ui.button(label="💎 Silver Ore Yield Upgrade", style=nextcord.ButtonStyle.blurple, row=2)
        async def buy_silver_ore_yield(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "silver_ore_upgrade_level", 100, silver_ore_upgrade_price)

        # Gold Ore Yield Upgrade: Only show after 25 rebirths
        @nextcord.ui.button(label="🏆 Gold Ore Yield Upgrade", style=nextcord.ButtonStyle.blurple, row=2)
        async def buy_gold_ore_yield(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "gold_ore_upgrade_level", 100, gold_ore_upgrade_price)

        # Row 2: Price Upgrades (green buttons)
        @nextcord.ui.button(label="💰 Wheat Price Upgrade", style=nextcord.ButtonStyle.gray, row=3)
        async def buy_wheat_price(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "wheat_price_upgrade_level", 100, wheat_price_upgrade)

        @nextcord.ui.button(label="💰 Wood Price Upgrade", style=nextcord.ButtonStyle.gray, row=3)
        async def buy_wood_price(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "wood_price_upgrade_level", 100, wood_price_upgrade)

        @nextcord.ui.button(label="💰 Stone Price Upgrade", style=nextcord.ButtonStyle.gray, row=3)
        async def buy_stone_price(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "stone_price_upgrade_level", 100, stone_price_upgrade)

        @nextcord.ui.button(label="💰 Hardwood Price Upgrade", style=nextcord.ButtonStyle.gray, row=3)
        async def buy_hardwood_price(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "hardwood_price_upgrade_level", 100, hardwood_price_upgrade)

        @nextcord.ui.button(label="💰 Iron Ore Price Upgrade", style=nextcord.ButtonStyle.gray, row=4)
        async def buy_iron_ore_price(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "iron_ore_price_upgrade_level", 100, iron_ore_price_upgrade)

        @nextcord.ui.button(label="💰 Silver Ore Price Upgrade", style=nextcord.ButtonStyle.gray, row=4)
        async def buy_silver_ore_price(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "silver_ore_price_upgrade_level", 100, silver_ore_price_upgrade)

        @nextcord.ui.button(label="💰 Gold Ore Price Upgrade", style=nextcord.ButtonStyle.gray, row=4)
        async def buy_gold_ore_price(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_upgrade(interaction, "gold_ore_price_upgrade_level", 100, gold_ore_price_upgrade)


    # Adjusting buttons visibility based on rebirths
    shop_message = await interaction.response.send_message(
        generate_shop_message(player_data), view=ShopView(None), ephemeral=True
    )

    shop_view = ShopView(shop_message)
    # Disable buttons if player has reached max level for each upgrade
    if player_data["farming_cooldown_level"] >= 20:
        shop_view.children[0].disabled = True
    if player_data["wheat_upgrade_level"] >= 100:
        shop_view.children[1].disabled = True
    if player_data["wood_upgrade_level"] >= 100:
        shop_view.children[2].disabled = True
    if player_data["stone_upgrade_level"] >= 100:
        shop_view.children[3].disabled = True
    if player_data["hardwood_upgrade_level"] >= 100:
        shop_view.children[4].disabled = True
    if player_data["iron_ore_upgrade_level"] >= 100:
        shop_view.children[5].disabled = True
    if player_data["silver_ore_upgrade_level"] >= 100:
        shop_view.children[6].disabled = True
    if player_data["gold_ore_upgrade_level"] >= 100:
        shop_view.children[7].disabled = True

    # Disable price upgrade buttons if the player has reached max price level
    if player_data["wheat_price_upgrade_level"] >= 100:
        shop_view.children[8].disabled = True
    if player_data["wood_price_upgrade_level"] >= 100:
        shop_view.children[9].disabled = True
    if player_data["stone_price_upgrade_level"] >= 100:
        shop_view.children[10].disabled = True
    if player_data["hardwood_price_upgrade_level"] >= 100:
        shop_view.children[11].disabled = True
    if player_data["iron_ore_price_upgrade_level"] >= 100:
        shop_view.children[12].disabled = True
    if player_data["silver_ore_price_upgrade_level"] >= 100:
        shop_view.children[13].disabled = True
    if player_data["gold_ore_price_upgrade_level"] >= 100:
        shop_view.children[14].disabled = True

    # Disable buttons based on rebirths
    if player_data["rebirths"] < 5:
        shop_view.children[3].disabled = True  # Stone Yield Upgrade
        shop_view.children[10].disabled = True  # Stone Price Upgrade
    if player_data["rebirths"] < 10:
        shop_view.children[4].disabled = True  # Hardwood Yield Upgrade
        shop_view.children[11].disabled = True  # Hardwood Price Upgrade
    if player_data["rebirths"] < 15:
        shop_view.children[5].disabled = True  # Iron Ore Yield Upgrade
        shop_view.children[12].disabled = True  # Iron Ore Price Upgrade
    if player_data["rebirths"] < 20:
        shop_view.children[6].disabled = True  # Silver Ore Yield Upgrade
        shop_view.children[13].disabled = True  # Silver Ore Price Upgrade
    if player_data["rebirths"] < 25:
        shop_view.children[7].disabled = True  # Gold Ore Yield Upgrade
        shop_view.children[14].disabled = True  # Gold Ore Price Upgrade

    await shop_message.edit(view=shop_view)


def generate_shop_message(player_data):
    balance_display = f"💰 **Current Balance:** {player_data['money']} coins\n\n"

    prices = [
        f"💰 **Current Balance:** {player_data['money']} coins\n\n"
        f"🛠️ **Cooldown Upgrade**: {cooldown_upgrade_price(player_data['farming_cooldown_level'])} coins (Level {player_data['farming_cooldown_level']})",
        f"🔄 **Current Cooldown:** {round(5 - player_data['farming_cooldown_level'] * 0.2, 1)} seconds",
        "\n━━━━━━━━━━━━━━━━━━\n",  # Separator
        f"🌾 **Wheat Yield Upgrade**: {wheat_upgrade_price(player_data['wheat_upgrade_level'])} coins (Level {player_data['wheat_upgrade_level']})",
        f"🌲 **Wood Yield Upgrade**: {wood_upgrade_price(player_data['wood_upgrade_level'])} coins (Level {player_data['wood_upgrade_level']})",
    ]

    if player_data["rebirths"] >= 5:
        prices.append(f"⛏️ **Stone Yield Upgrade**: {stone_upgrade_price(player_data['stone_upgrade_level'])} coins (Level {player_data['stone_upgrade_level']})")
        
    if player_data["rebirths"] >= 10:
        prices.append(f"🌳 **Hardwood Yield Upgrade**: {hardwood_upgrade_price(player_data['hardwood_upgrade_level'])} coins (Level {player_data['hardwood_upgrade_level']})")
        
    if player_data["rebirths"] >= 15:
        prices.append(f"⛏️ **Iron Ore Yield Upgrade**: {iron_ore_upgrade_price(player_data['iron_ore_upgrade_level'])} coins (Level {player_data['iron_ore_upgrade_level']})")
        
    if player_data["rebirths"] >= 20:
        prices.append(f"💎 **Silver Ore Yield Upgrade**: {silver_ore_upgrade_price(player_data['silver_ore_upgrade_level'])} coins (Level {player_data['silver_ore_upgrade_level']})")
        
    if player_data["rebirths"] >= 25:
        prices.append(f"🏆 **Gold Ore Yield Upgrade**: {gold_ore_upgrade_price(player_data['gold_ore_upgrade_level'])} coins (Level {player_data['gold_ore_upgrade_level']})")
        
    prices.append("\n━━━━━━━━━━━━━━━━━━\n")  # Separator

    # Price upgrades
    prices.append(f"💰 **Wheat Price Upgrade**: {wheat_price_upgrade(player_data['wheat_price_upgrade_level'])} coins (Level {player_data['wheat_price_upgrade_level']})")
    prices.append(f"📈 **New Base Price:** {1 + player_data['wheat_price_upgrade_level'] * 2}")

    prices.append(f"💰 **Wood Price Upgrade**: {wood_price_upgrade(player_data['wood_price_upgrade_level'])} coins (Level {player_data['wood_price_upgrade_level']})")
    prices.append(f"📈 **New Base Price:** {5 + player_data['wood_price_upgrade_level'] * 3}")

    if player_data["rebirths"] >= 5:
        prices.append(f"💰 **Stone Price Upgrade**: {stone_price_upgrade(player_data['stone_price_upgrade_level'])} coins (Level {player_data['stone_price_upgrade_level']})")
        prices.append(f"📈 **New Base Price:** {25 + player_data['stone_price_upgrade_level'] * 10}")

    if player_data["rebirths"] >= 10:
        prices.append(f"💰 **Hardwood Price Upgrade**: {hardwood_price_upgrade(player_data['hardwood_price_upgrade_level'])} coins (Level {player_data['hardwood_price_upgrade_level']})")
        prices.append(f"📈 **New Base Price:** {100 + player_data['hardwood_price_upgrade_level'] * 20}")

    if player_data["rebirths"] >= 15:
        prices.append(f"💰 **Iron Ore Price Upgrade**: {iron_ore_price_upgrade(player_data['iron_ore_price_upgrade_level'])} coins (Level {player_data['iron_ore_price_upgrade_level']})")
        prices.append(f"📈 **New Base Price:** {300 + player_data['iron_ore_price_upgrade_level'] * 35}")

    if player_data["rebirths"] >= 20:
        prices.append(f"💰 **Silver Ore Price Upgrade**: {silver_ore_price_upgrade(player_data['silver_ore_price_upgrade_level'])} coins (Level {player_data['silver_ore_price_upgrade_level']})")
        prices.append(f"📈 **New Base Price:** {750 + player_data['silver_ore_price_upgrade_level'] * 45}")

    if player_data["rebirths"] >= 25:
        prices.append(f"💰 **Gold Ore Price Upgrade**: {gold_ore_price_upgrade(player_data['gold_ore_price_upgrade_level'])} coins (Level {player_data['gold_ore_price_upgrade_level']})")
        prices.append(f"📈 **New Base Price:** {2000 + player_data['gold_ore_price_upgrade_level'] * 120}")


    return "\n".join(prices)




# Price Scaling Functions (Updated with Specific Prices)
def cooldown_upgrade_price(level):
    return int(250 * (1.5 ** level) + (level * 100))

def wheat_upgrade_price(level):
    return int(50 * (1.3 ** level) + (level * 10))  # Base price for wheat yield upgrade

def wood_upgrade_price(level):
    return int(80 * (1.3 ** level) + (level * 20))  # Wood yield upgrade price

def stone_upgrade_price(level):
    return int(120 * (1.4 ** level) + (level * 30))  # Stone yield upgrade price

def hardwood_upgrade_price(level):
    return int(160 * (1.4 ** level) + (level * 40))  # Hardwood yield upgrade price

def iron_ore_upgrade_price(level):
    return int(200 * (1.5 ** level) + (level * 50))  # Iron Ore yield upgrade price

def silver_ore_upgrade_price(level):
    return int(250 * (1.6 ** level) + (level * 60))  # Silver Ore yield upgrade price

def gold_ore_upgrade_price(level):
    return int(300 * (1.7 ** level) + (level * 70))  # Gold Ore yield upgrade price

def wheat_price_upgrade(level):
    return int(50 * (1.4 ** level) + (level * 10))  # Wheat price upgrade

def wood_price_upgrade(level):
    return int(80 * (1.4 ** level) + (level * 15))  # Wood price upgrade

def stone_price_upgrade(level):
    return int(120 * (1.5 ** level) + (level * 25))  # Stone price upgrade

def hardwood_price_upgrade(level):
    return int(160 * (1.5 ** level) + (level * 35))  # Hardwood price upgrade

def iron_ore_price_upgrade(level):
    return int(200 * (1.6 ** level) + (level * 45))  # Iron Ore price upgrade

def silver_ore_price_upgrade(level):
    return int(250 * (1.7 ** level) + (level * 55))  # Silver Ore price upgrade

def gold_ore_price_upgrade(level):
    return int(300 * (1.8 ** level) + (level * 65))  # Gold Ore price upgrade



@client.slash_command(name="cowshop", description="Buy cows and upgrade milk prices!")
async def cowshop(interaction: nextcord.Interaction):
    user_id = interaction.user.id
    data = load_json(DATA_FILE)  # Load player data

    # Check if the user is registered
    if not is_registered(user_id, data):
        await interaction.response.send_message("⚠️ You need to register first! Please use `/register` to create an account.", ephemeral=True)
        return
    
    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return

    player_data = data["players"][str(user_id)]  # Get player data

    # Initialize missing keys if they don't exist yet
    player_data.setdefault("cow_owned", False)  # Default to False if the player doesn't have a cow
    player_data.setdefault("milk", 0)  # Initialize milk amount to 0
    player_data.setdefault("milk_price_upgrade_level", 0)  # Initialize upgrade level to 0
    player_data.setdefault("money", 0)  # Ensure player has money initialized
    player_data.setdefault("stored_milk", 0)  # Ensure stored milk is initialized

    class CowShopView(nextcord.ui.View):
        def __init__(self, message):
            super().__init__()
            self.message = message  # Store the message object for editing later

            # Disable the "Buy Cow" button if the player already owns a cow
            if player_data["cow_owned"]:
                self.children[0].disabled = True  # Disable "Buy Cow" button
            
            # Disable the "Upgrade Milk Price" button if the player reached level 50
            if player_data["milk_price_upgrade_level"] >= 50:
                self.children[1].disabled = True  # Disable milk price upgrade button

        async def purchase_cow(self, interaction):
            if player_data["cow_owned"]:
                await interaction.response.send_message("❌ You already own a cow!", ephemeral=True)
                return

            if player_data["money"] < 50000:
                await interaction.response.send_message("❌ Not enough money to buy a cow!", ephemeral=True)
                return

            # Deduct money and grant the cow
            player_data["money"] -= 50000
            player_data["cow_owned"] = True
            player_data["milk"] = 0  # Initialize the milk amount to 0 when the cow is bought
            save_json(DATA_FILE, data)
            await self.update_cowshop_message(interaction)

        async def upgrade_milk_price(self, interaction):
            price = milk_price_upgrade_cost(player_data["milk_price_upgrade_level"])

            if player_data["money"] < price:
                await interaction.response.send_message("❌ Not enough money to upgrade milk price!", ephemeral=True)
                return

            if player_data["milk_price_upgrade_level"] >= 50:
                await interaction.response.send_message("❌ Maximum upgrade level reached for milk price!", ephemeral=True)
                return

            # Deduct money and upgrade milk price
            player_data["money"] -= price
            player_data["milk_price_upgrade_level"] += 1
            save_json(DATA_FILE, data)
            await self.update_cowshop_message(interaction)

        async def update_cowshop_message(self, interaction):
            updated_message = generate_cowshop_message(player_data)
            await self.message.edit(content=updated_message, view=self)
            await interaction.response.defer()  # Prevents "Interaction failed" errors

        # Button to purchase cow
        @nextcord.ui.button(label="🐄 Buy Cow (50,000 coins)", style=nextcord.ButtonStyle.green, row=0)
        async def buy_cow(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.purchase_cow(interaction)

        # Button to upgrade milk price
        @nextcord.ui.button(label="💰 Upgrade Milk Price", style=nextcord.ButtonStyle.blurple, row=1)
        async def upgrade_milk_price_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            await self.upgrade_milk_price(interaction)

    # Send the shop message with the initial view
    cowshop_message = await interaction.response.send_message(
        generate_cowshop_message(player_data), view=CowShopView(None), ephemeral=True
    )

    # Update the view for the shop with message
    cowshop_view = CowShopView(cowshop_message)
    await cowshop_message.edit(view=cowshop_view)

# Function to generate the cowshop message dynamically
def generate_cowshop_message(player_data):
    prices = [
        f"💸 **Your Balance:** {player_data['money']} coins\n\n",
        "🛒 **Welcome to the Cow Shop!**\n*Buy a cow and upgrade milk prices!*",
        "\n",  # Blank row
        f"🐄 **Buy Cow (50,000 coins):** {'✅ Purchased' if player_data['cow_owned'] else '❌ Not Owned'}",
        f"💰 Milk Price Upgrade: {milk_price_upgrade_cost(player_data['milk_price_upgrade_level'])} coins (Level {player_data['milk_price_upgrade_level']})"
    ]
    
    # If player owns a cow, display the milk price without decimals
    if player_data['cow_owned']:
        milk_price = int(150 * (1.2 ** player_data['milk_price_upgrade_level']))
        prices.append(f"**Milk Price:** {milk_price} coins per milk")
    else:
        prices.append("**Milk Price:** Not yet available until you buy a cow!")

    return "\n".join(prices)



# Define the price and upgrade function for milk price upgrade
def milk_price_upgrade(level):
    base_price = 150  # Base price of milk
    return int(base_price * (1.2 ** level))  # Prices increase with each level

def milk_price_upgrade_cost(level):
    return int(300 * (1.6 ** level) + (level * 75))  # MILK!!!




@client.slash_command(name="daily", description="Claim your daily reward!")
async def daily(interaction: nextcord.Interaction):
    user_id = interaction.user.id
    data = load_json("data.json")

    # Check if the user is registered
    if not is_registered(user_id, data):
        await interaction.response.send_message("⚠️ You need to register first! Please use `/register` to create an account.", ephemeral=True)
        return
    
    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return

    player_data = data["players"][str(user_id)]

    # Initialize missing keys if they don't exist
    player_data.setdefault("last_daily_claim", None)
    player_data.setdefault("daily_streak", 0)
    player_data.setdefault("longest_streak", 0)
    player_data.setdefault("total_claims", 0)
    player_data.setdefault("money", 0)
    player_data.setdefault("wheat", 0)
    player_data.setdefault("wood", 0)
    player_data.setdefault("stone", 0)
    player_data.setdefault("hardwood", 0)
    player_data.setdefault("iron_ore", 0)
    player_data.setdefault("silver_ore", 0)
    player_data.setdefault("gold_ore", 0)

    # Get current date in UTC
    today = datetime.now(timezone.utc).date()
    last_claim_str = player_data["last_daily_claim"]

    # Check if last claim exists and is valid
    last_claim = datetime.strptime(last_claim_str, "%Y-%m-%d").date() if last_claim_str else None
    if last_claim and last_claim == today:
        await interaction.response.send_message("You've already claimed your daily reward today! Come back tomorrow.", ephemeral=True)
        return

    # Check if the streak is maintained or reset
    if last_claim and last_claim + timedelta(days=1) == today:
        player_data["daily_streak"] += 1  # Increase streak
    else:
        player_data["daily_streak"] = 1  # Reset streak if a day was missed

    streak = player_data["daily_streak"]

    # Update longest streak if current streak exceeds it
    player_data["longest_streak"] = max(player_data["longest_streak"], streak)

    # Increment the total dailies claimed
    player_data["total_claims"] += 1

    # Unlock resources based on rebirths
    rebirths = player_data.get("rebirths", 0)
    rebirth_multiplier = player_data.get("rebirth_multiplier", 1.0)

    # Calculate base rewards, then apply streak and rebirth multiplier
    wheat_reward = round(random.randint(2, 5) * (1 + streak / 2) * rebirth_multiplier)
    wood_reward = round(random.randint(2, 5) * (1 + streak / 2.5) * rebirth_multiplier)
    stone_reward = round(random.randint(1, 3) * (1 + streak / 3) * rebirth_multiplier)
    hardwood_reward = iron_ore_reward = silver_ore_reward = gold_ore_reward = 0

    # Unlock resources based on rebirth requirements
    if rebirths >= 5:
        hardwood_reward = round(random.randint(0, 2) * (1 + streak / 3.5) * rebirth_multiplier)
    if rebirths >= 10:
        iron_ore_reward = round(random.randint(0, 2) * (1 + streak / 3.5) * rebirth_multiplier)
    if rebirths >= 15:
        silver_ore_reward = round(random.randint(0, 2) * (1 + streak / 4) * rebirth_multiplier)
    if rebirths >= 20:
        gold_ore_reward = round(random.randint(0, 2) * (1 + streak / 4) * rebirth_multiplier)

    # Calculate the money reward with the same scaling
    money_reward = round(random.uniform(50, 100) * (1 + streak / 1.5) * rebirth_multiplier)

    # Check if the user has any debt
    debt = player_data.get("debt", 0)

    # Initialize the debt message to an empty string
    debt_cleared_message = ""

    # If the user has debt, apply the daily reward to clear it first
    if debt > 0:
        if money_reward >= debt:
            remaining_money = money_reward - debt  # Money after clearing debt
            player_data["money"] += remaining_money  # Add the remaining money after clearing debt
            player_data["debt"] = 0  # Clear the debt
            debt_cleared_message = f"Your debt of {debt} coins has been **cleared**!"
        else:
            player_data["debt"] -= money_reward  # Reduce the debt by the money rewarded
            player_data["money"] = 0  # Money stays 0 since debt is still present
            debt_cleared_message = f"Your remaining debt is **{player_data['debt']} coins**."
    else:
        player_data["money"] += money_reward  # No debt, just add the money reward

    # Update player stats
    player_data["wheat"] += wheat_reward
    player_data["wood"] += wood_reward
    player_data["stone"] += stone_reward
    player_data["hardwood"] += hardwood_reward
    player_data["iron_ore"] += iron_ore_reward
    player_data["silver_ore"] += silver_ore_reward
    player_data["gold_ore"] += gold_ore_reward
    player_data["last_daily_claim"] = today.strftime("%Y-%m-%d")

    save_json("data.json", data)

    # Create response message
    reward_message = (
        f"🎉 **Daily Reward Claimed!** (Streak: {streak} days) 🎉\n"
        f"💰 **Money:** +${money_reward}\n"
        f"🌾 **Wheat:** +{wheat_reward}\n"
        f"🌲 **Wood:** +{wood_reward}\n"
        f"⛏️ **Stone:** +{stone_reward}\n"
        f"🌳 **Hardwood:** +{hardwood_reward}\n"
        f"⚒️ **Iron Ore:** +{iron_ore_reward}\n"
        f"💎 **Silver Ore:** +{silver_ore_reward}\n"
        f"🏅 **Gold Ore:** +{gold_ore_reward}\n"
        f"\n{debt_cleared_message}\n"  # Add message about clearing debt or remaining debt
        f"Claim again tomorrow to increase your streak! 🔥\n"
    )

    await interaction.response.send_message(reward_message, ephemeral=True)




@client.slash_command(name="streak", description="Check your daily streak information.")
async def streak(interaction: nextcord.Interaction):
    user_id = interaction.user.id
    data = load_json("data.json")

    # Check if the user is registered
    if not is_registered(user_id, data):
        await interaction.response.send_message("⚠️ You need to register first! Please use `/register` to create an account.", ephemeral=True)
        return
    
    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return

    player_data = data["players"][str(user_id)]

    # Initialize missing keys if they don't exist
    player_data.setdefault("daily_streak", 0)
    player_data.setdefault("longest_streak", 0)
    player_data.setdefault("total_claims", 0)

    # Retrieve current streak, longest streak, and total claims
    current_streak = player_data["daily_streak"]
    longest_streak = player_data["longest_streak"]
    total_claims = player_data["total_claims"]

    # Create response message
    streak_message = (
        f"📅 **Daily Streak Information** 📅\n"
        f"🌟 **Current Streak:** {current_streak} days\n"
        f"🏆 **Longest Streak:** {longest_streak} days\n"
        f"🔄 **Total Daily Claims:** {total_claims} times\n"
    )

    await interaction.response.send_message(streak_message, ephemeral=True)


@client.slash_command(name="plinko", description="Gamble your money and try to win big!")
async def plinko(interaction: nextcord.Interaction, amount: int):
    user_id = interaction.user.id

    # Load player data
    data = load_json(DATA_FILE)

    if not is_registered(user_id, data):
        await interaction.response.send_message("⚠️ You need to register first! Please use `/register` to create an account.", ephemeral=True)
        return

    player_data = data["players"].get(str(user_id), {})

    # Check if the user has at least 7 rebirths
    if player_data["rebirths"] < 7:
        await interaction.response.send_message("⚠️ You need at least 7 rebirths to play the plinko! Keep rebirthing to unlock this.", ephemeral=True)
        return

    # Retrieve user balance and debt
    money = player_data.get("money", 0)
    total_debt = player_data.get("debt", 0)


     # **NEW**: Limit betting if the user is in debt
    max_bet_if_in_debt = 25000
    if (total_debt > 0 or money <= 0) and amount > max_bet_if_in_debt:
        await interaction.response.send_message(
            f"🚫 You are in debt! While in debt, you can only bet up to **{max_bet_if_in_debt} coins**.",
            ephemeral=True
        )
        return

    player_data.setdefault("total_gambled", 0)
    player_data.setdefault("total_earned_or_lost", 0.0)


    # Gambling multipliers
    outcome = random.choices(
        ["25x", "10x", "5x", "3x", "2x", "1.5x", "1x", "0.5x", "0.2x", "0x", "-5x"],
        weights=[0.1, 0.4, 1.5, 2, 5, 10, 19, 19, 33, 7, 3],
        k=1
    )[0]


    multipliers = {
        "25x": 25, "10x": 10, "5x": 5, "3x": 3, "2x": 2,
        "1.5x": 1.5, "1x": 1, "0.5x": 0.5, "0.2x": 0.2,
        "0x": 0, "-5x": -5
    }

    multiplier = multipliers[outcome]
    earnings = amount * multiplier
    net_gain_or_loss = earnings - amount  # The actual change in money


    # Deduct bet from money or increase debt
    if money >= amount:
        money -= amount  # Deduct full amount from money
    else:
        debt_increase = amount - money  # How much we need to add to debt
        money = 0  # Reset money to zero first!
        total_debt += debt_increase  # Increase debt

    # Handling debt repayment if any
    if total_debt > 0:
        if earnings >= total_debt:
            money = earnings - total_debt  # Pay off debt, keep the rest
            total_debt = 0
        else:
            total_debt -= earnings  # Reduce debt
            money = 0  # No money since debt still exists
    else:
        money += earnings  # No debt, just add winnings

    # Update player data
    player_data["money"] = money
    player_data["debt"] = total_debt
    player_data["total_gambled"] += 1
    player_data["total_earned_or_lost"] += net_gain_or_loss

    # 🔥 NEW: Dynamic message formatting for clarity 🔥
    if net_gain_or_loss > 0:
        result_message = f"You won **{net_gain_or_loss} coins**!"
    elif net_gain_or_loss < 0:
        result_message = f"You lost **{-net_gain_or_loss} coins**!"
    else:
        result_message = "You broke even."

    # If earnings are enough to clear the debt
    if total_debt > 0 and net_gain_or_loss >= total_debt:
        remaining_money = net_gain_or_loss - total_debt  # Pay off all debt
        total_debt = 0  # Debt is cleared
        money = remaining_money  # Remaining money after debt clearance
        final_message = f"💥 You gambled {amount} coins and got **{outcome}**. {result_message} Your debt has been **cleared**, and you now have **{money} coins**."

    # If the user is still in debt, show remaining debt
    elif total_debt > 0:
        final_message = f"💥 You gambled {amount} coins and got **{outcome}**. {result_message} Your remaining debt is **{total_debt} coins**."

    # If no debt, show the total money after winnings
    else:
        if net_gain_or_loss == 0:
            final_message = f"💥 You gambled {amount} coins and got **{outcome}**. {result_message} Your total money is now **{money} coins**, and your debt remains the same."
        else:
            final_message = f"💥 You gambled {amount} coins and got **{outcome}**. {result_message} Your total money is now **{money} coins**."

    # Send message to user
    await interaction.response.send_message(final_message, ephemeral=True)

    # Save the data
    save_json(DATA_FILE, data)

@client.slash_command(name="coinflip", description="Flip a coin and try your luck!")
async def coinflip(
    interaction: nextcord.Interaction,
    bet: str = nextcord.SlashOption(
        name="bet",
        description="Choose what to bet on",
        choices=["Heads", "Tails", "Side"],
        required=True
    ),
    amount: int = nextcord.SlashOption(
        name="amount",
        description="Amount of money you want to bet",
        required=True
    )
):
    user_id = interaction.user.id

    # Load player data
    data = load_json(DATA_FILE)

    # Check if the user is registered
    if not is_registered(user_id, data):
        await interaction.response.send_message("⚠️ You need to register first! Please use `/register` to create an account.", ephemeral=True)
        return
    
    if is_banned(user_id, data):
        await interaction.response.send_message("⛔ You are banned from using this bot.", ephemeral=True)
        return

    player_data = data["players"].get(str(user_id), {})

    # Ensure the player has necessary attributes
    player_data.setdefault("total_earned_or_lost", 0)
    player_data.setdefault("coinflip_uses", 0)

    # Check if the user has at least 12 rebirths
    if player_data["rebirths"] < 12:
        await interaction.response.send_message("⚠️ You need at least 12 rebirths to play the coinflip game. Keep rebirthing to unlock this.", ephemeral=True)
        return

    # Retrieve user balance and debt
    money = player_data.get("money", 0)
    total_debt = player_data.get("debt", 0)

    # **NEW**: Limit betting if the user is in debt
    max_bet_if_in_debt = 25000
    if (total_debt > 0 or money <= 0) and amount > max_bet_if_in_debt:
        await interaction.response.send_message(
            f"🚫 You are in debt! While in debt, you can only bet up to **{max_bet_if_in_debt} coins**.",
            ephemeral=True
        )
        return

    # Define the odds and multipliers for the bets
    if bet == "Heads":
        odds = {"Heads": 19.99, "Tails": 80, "Side": 0.01}
        win_multiplier = 2.5
        lose_multiplier = 4
    elif bet == "Tails":
        odds = {"Heads": 80, "Tails": 19.99, "Side": 0.01}
        win_multiplier = 2.5
        lose_multiplier = 4
    elif bet == "Side":
        odds = {"Heads": 50, "Tails": 49.99, "Side": 0.01}
        win_multiplier = 1000  # 1000x reward
        lose_multiplier = 24   # 24x loss

    # Flip the coin
    outcome = random.choices(
        list(odds.keys()), 
        weights=[odds["Heads"], odds["Tails"], odds["Side"]], 
        k=1
    )[0]

    # Handle betting
    if money < amount:
        debt_increase = amount - money
        total_debt += debt_increase  # Add missing amount to debt
        money = 0
        result_message = f"You didn't have enough money, so **{debt_increase} coins** have been added to your debt."
    else:
        money -= amount
        result_message = f"You've placed a bet of **{amount} coins**."

    # Determine if the player wins or loses
    if outcome == bet:
        winnings = amount * win_multiplier
        money += winnings
        player_data["total_earned_or_lost"] += winnings  # Track earnings
        result_message += f" 🎉 **JACKPOT!** You won **{winnings} coins**!"
    else:
        loss = amount * lose_multiplier
        total_loss = loss + amount  # Full loss includes the original bet
        if money >= loss:
            money -= loss
        else:
            debt_increase = loss - money
            total_debt += debt_increase  # Add the missing amount to debt
            money = 0
        player_data["total_earned_or_lost"] -= total_loss  # Track losses
        result_message += f" 💀 **OUCH!** You lost **{total_loss} coins**!"

    # Handle debt repayment
    if total_debt > 0:
        if money >= total_debt:
            money -= total_debt  # Pay off debt
            total_debt = 0
        else:
            total_debt -= money  # Reduce debt by the amount of money available
            money = 0

    # Update player data
    player_data["money"] = money
    player_data["debt"] = total_debt
    player_data["coinflip_uses"] += 1  # Increment usage count

    # Final message formatting
    final_message = (
        f"💥 You chose **{bet}**. The outcome was **{outcome}**. {result_message} "
        f"Your total money is now **{money} coins** and your debt is **{total_debt} coins**. "
    )

    await interaction.response.send_message(final_message, ephemeral=True)

    # Save the data
    save_json(DATA_FILE, data)


client.run(config.get("token"))
