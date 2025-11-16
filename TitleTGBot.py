from dotenv import load_dotenv
load_dotenv()  # Loads .env file

import os
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

import logging
import os
import sys # <--- ENSURE THIS LINE IS PRESENT!
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# ... rest of your code ...MessageHandler, filters, ContextTypes, ConversationHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Conversation States ---
# Define states for our conversation flow
# Adjusted states after removing unnecessary questions
GET_LEVEL, GET_TEAM, GET_POKEMON_STORAGE, GET_LEGENDARY, GET_SHINY, GET_HUNDO, \
GET_OVER_3000, GET_LEGENDARY_SHINY, GET_LUCKY, GET_MYTHICAL, GET_SHADOW, \
GET_ITEM_STORAGE, GET_STARDUST, GET_ACCOUNT_ID, GET_SHUNDO, GET_POKE_COINS, \
GET_NAME_CHANGE, GET_OVER_2500, GET_TOP_LEGENDARIES, GET_TOP_SHINIES, \
GET_PURIFIED, GET_MEGA_EVOLVE, GET_EVENT, GET_DELIVERY_METHOD, \
GET_OTHER_ACCOUNTS_LINK, \
GET_EMAIL, GET_PASSWORD_CHOICE, GET_CUSTOM_PASSWORD, GENERATE_OUTPUT = range(29) # Adjusted range


# --- Helper Functions (mostly same as before, but modified for bot context) ---

def get_validated_input_bot(text_input, input_type=str, default=None, validation_func=None):
    """
    Validates input received from Telegram. Returns the validated value or raises ValueError.
    Allows for empty string input if default is None, otherwise applies default.
    """
    if not text_input.strip() and default is not None:
        return default

    if not text_input.strip() and default is None: # Allow truly empty input if no default
        return ""

    try:
        if input_type == int:
            processed_input = text_input.replace(',', '')
            value = input_type(processed_input)
        else:
            value = input_type(text_input.strip())

        if validation_func and not validation_func(value):
            raise ValueError("Validation failed.")
        return value
    except ValueError:
        raise ValueError(f"Please enter a valid {input_type.__name__}.")
    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {e}")

def format_bullet_points(input_string):
    """Formats a comma-separated string into bullet points."""
    if not input_string:
        return ""
    items = [item.strip() for item in input_string.split(',') if item.strip()]
    return "\n".join([f"🔹- {item}" for item in items])

def generate_pogo_title(account_data):
    """Generates title with star separators"""
    return (
        f"LVL {account_data.get('level', 'N/A')}({account_data.get('team', 'N/A')})⭐"
        f"{account_data.get('pokemon_storage', 'N/A')}⭐"
        f"{account_data.get('legendary', 0)} Legendary⭐"
        f"{account_data.get('shiny', 0)} Shiny⭐"
        f"{account_data.get('hundo', 0)} Hundo⭐"
        f"{account_data.get('over_3000', 0)}x 3000+ CP⭐"
        f"{account_data.get('legendary_shiny', 0)} Legendary&Shiny⭐"
        f"{account_data.get('lucky', 0)} Lucky⭐"
        f"{account_data.get('mythical', 0)} Mythical⭐"
        f"{account_data.get('shadow', 0)} Shadow⭐"
        f"Item {account_data.get('item_storage', 'N/A')}⭐"
        f"Stardust {account_data.get('stardust', 0):,}⭐"
        f"{account_data.get('delivery_method', 'Instant Delivery')}"
    )


def generate_pogo_description(account_data):
    """Generates full account description"""
    description_parts = [
        "⚡ RARE POKEMON GO ACCOUNT FOR SALE!",
        f"⚡ LEVEL {account_data.get('level', 'N/A')} ACCOUNT ({account_data.get('team', 'N/A')})",
        f"⚡🆔 Account ID - {account_data.get('account_id', 'N/A')}⚡",
        "__________________________________",
        "\n⚡ TOP-TIER HIGHLIGHTS ⚡",
        f"🔹Account Level: {account_data.get('level', 'N/A')} ({account_data.get('team', 'N/A')})",
        f"🔹Shundo: {account_data.get('shundo', 0)}",
        f"🔹Hundo: {account_data.get('hundo', 0)}",
        f"🔹Legendaries: {account_data.get('legendary', 0)}",
        f"🔹Shinies: {account_data.get('shiny', 0)}",
        f"🔹Legendary & Shiny Combo: {account_data.get('legendary_shiny', 0)}",
        f"🔹Pokémon Storage: {account_data.get('pokemon_storage', 'N/A')}",
        f"🔹Item Storage: {account_data.get('item_storage', 'N/A')}",
        f"🔹Name Change Available: {account_data.get('name_change', 'No')}",
        f"🔹PokéCoins: {account_data.get('poke_coins', 0)}",
        "\n⚡ High CP Pokémon ⚡",
        f"🔹{account_data.get('over_2500', 0)} over 2500+ CP",
        f"🔹{account_data.get('over_3000', 0)} over 3000+ CP",
    ]

    if account_data.get('top_legendaries'):
        description_parts.append("\n⚡Top Legendaries⚡")
        description_parts.extend(account_data['top_legendaries'].split('\n'))
    else:
        description_parts.append("\n⚡Top Legendaries⚡\n🔹- None listed")

    if account_data.get('top_shinies'):
        description_parts.append("\n⚡Top Shinies ⚡")
        description_parts.extend(account_data['top_shinies'].split('\n'))
    else:
        description_parts.append("\n⚡Top Shinies ⚡\n🔹- None listed")

    description_parts.extend([
        "\n⚡ KEY STATS ⚡",
        f"🔹Stardust: {account_data.get('stardust', 0):,}",
        f"🔹Mythicals: {account_data.get('mythical', 0)}",
        f"🔹Shadow Pokémon: {account_data.get('shadow', 0)}",
        f"🔹Purified: {account_data.get('purified', 0)}",
        f"🔹Mega Evolutions Unlocked: {account_data.get('mega_evolve', 0)}",
        f"🔹Event Pokémon: {account_data.get('event', 0)}",
        "__________________________________"
    ])

    if account_data.get('other_accounts_link'):
        description_parts.append(f"\nCheck out More Accounts:\n{account_data['other_accounts_link']}")

    description_parts.extend([
        "\n__________________________________",
        "\n✅ Verified Seller | Instant Delivery",
        # Hardcoded these as per request
        f"\n🚀 Instant Access: Receive credentials immediately after purchase with full Gmail access",
        f"🔒 Authentic account - No risks - Original owner",
        f"📱 Works on Android & iOS devices",
        f"⭐ Best value guaranteed - Eldorado verified",
        "\nAccount Highlights:"
    ])

    if account_data.get('highlights'):
        description_parts.append(account_data['highlights'])
    else:
        description_parts.append("Full Gmail ownership\nMultiple linking options available\nImmediate account transfer")

    description_parts.append(f"⏰ Delivery: Instant upon payment confirmation")

    return "\n".join(description_parts)

def generate_pogo_credentials(email, password):
    """Generates credentials section"""
    return f"""
🔐 ACCOUNT CREDENTIALS
▫️ Gmail: {email}
▫️ Password: {password}
▫️ Login Method: Google Sign-In
▫️ Security: Full Access | Password Change Available
"""

# --- Bot Handler Functions ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for the account level."""
    context.user_data.clear() # Clear previous data on /start or /generate
    context.user_data['account_data'] = {} # Initialize an empty dict for account data
    await update.message.reply_text(
        "Hello! I'm your Pokémon GO Account Generator Bot.\n"
        "I'll guide you through generating a listing.\n"
        "You can type /cancel at any time to stop.\n\n"
        "Please enter the *Account Level*:",
        parse_mode='Markdown'
    )
    return GET_LEVEL

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    context.user_data.clear() # Clear all user data
    await update.message.reply_text(
        "Operation canceled. Send /start or /generate to create a new listing.",
        reply_markup=ReplyKeyboardRemove() # Remove any lingering keyboards
    )
    return ConversationHandler.END

async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles skipping of optional inputs."""
    current_state = context.user_data.get('current_state') # Store current state to skip from

    if current_state == GET_TOP_LEGENDARIES:
        context.user_data['account_data']['top_legendaries'] = "" # Set to empty if skipped
        await update.message.reply_text("Skipped Top Legendaries. Enter *Top Shinies* (comma separated, e.g., 'Charizard, Gyarados'):", parse_mode='Markdown')
        return GET_TOP_SHINIES
    elif current_state == GET_TOP_SHINIES:
        context.user_data['account_data']['top_shinies'] = "" # Set to empty if skipped
        await update.message.reply_text("Skipped Top Shinies. Enter *Purified Count*:", parse_mode='Markdown')
        return GET_PURIFIED
    elif current_state == GET_OTHER_ACCOUNTS_LINK:
        context.user_data['account_data']['other_accounts_link'] = "" # Set to empty if skipped
        await update.message.reply_text("Skipped Other Accounts Link. Enter *Account Gmail*:", parse_mode='Markdown')
        return GET_EMAIL
    else:
        await update.message.reply_text("Sorry, you can't skip this input or I don't know how to skip from here. Please provide a valid input or /cancel.", parse_mode='Markdown')
        return current_state # Stay in the same state if not a skippable one

# --- General input handler factory ---
# This helps reduce repetitive code for simple text/int inputs
async def text_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, next_state: int, field_name: str, prompt_text: str, input_type=str, default=None, validation_func=None) -> int:
    try:
        value = get_validated_input_bot(update.message.text, input_type=input_type, default=default, validation_func=validation_func)
        if field_name == 'highlights': # Special handling for highlights
            if value and ',' in value:
                context.user_data['account_data'][field_name] = format_bullet_points(value)
            else:
                context.user_data['account_data'][field_name] = value or format_bullet_points("Full Gmail ownership, Multiple linking options available, Immediate account transfer")
        else:
            context.user_data['account_data'][field_name] = value

        context.user_data['current_state'] = next_state # Update current state for /skip
        await update.message.reply_text(prompt_text, parse_mode='Markdown')
        return next_state
    except ValueError as e:
        await update.message.reply_text(f"Error: {e}\n{prompt_text}", parse_mode='Markdown')
        return context.user_data.get('current_state', next_state) # Stay in current state on error

# --- Specific Handler Implementations using the factory ---

async def get_level_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_TEAM, 'level', "Enter *Team* (Valor/Mystic/Instinct):", input_type=int, validation_func=lambda x: x > 0)

async def get_team_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_POKEMON_STORAGE, 'team', "Enter *Pokémon Storage* (e.g., 670/700):", validation_func=lambda x: x.capitalize() in ['Valor', 'Mystic', 'Instinct'])

async def get_pokemon_storage_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_LEGENDARY, 'pokemon_storage', "Enter *Total Legendaries*:")

async def get_legendary_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_SHINY, 'legendary', "Enter *Total Shinies*:", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_shiny_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_HUNDO, 'shiny', "Enter *Hundo Count*:", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_hundo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_OVER_3000, 'hundo', "Enter *3000+ CP Count*:", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_over_3000_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_LEGENDARY_SHINY, 'over_3000', "Enter *Legendary & Shiny Combo Count*:", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_legendary_shiny_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_LUCKY, 'legendary_shiny', "Enter *Lucky Pokémon Count*:", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_lucky_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_MYTHICAL, 'lucky', "Enter *Mythical Count*:", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_mythical_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_SHADOW, 'mythical', "Enter *Shadow Pokémon Count*:", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_shadow_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_ITEM_STORAGE, 'shadow', "Enter *Item Storage* (e.g., 805/700):", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_item_storage_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_STARDUST, 'item_storage', "Enter *Stardust Amount*:")

async def get_stardust_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_ACCOUNT_ID, 'stardust', "Enter *Account ID* (e.g., PJ067):", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_account_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['account_data']['account_id'] = update.message.text.strip().upper()
    context.user_data['current_state'] = GET_SHUNDO # Update current state for /skip
    await update.message.reply_text("Enter *Shundo Count*:", parse_mode='Markdown')
    return GET_SHUNDO

async def get_shundo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_POKE_COINS, 'shundo', "Enter *PokéCoins*:", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_poke_coins_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_NAME_CHANGE, 'poke_coins', "Is *Name Change Available*? (Yes/No):", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_name_change_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_OVER_2500, 'name_change', "Enter *2500+ CP Count*:", validation_func=lambda x: x.capitalize() in ['Yes', 'No'])

async def get_over_2500_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_TOP_LEGENDARIES, 'over_2500', "Enter *Top Legendaries* (comma separated, type /skip to leave blank):", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_top_legendaries_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['account_data']['top_legendaries'] = format_bullet_points(update.message.text)
    context.user_data['current_state'] = GET_TOP_SHINIES
    await update.message.reply_text("Enter *Top Shinies* (comma separated, type /skip to leave blank):", parse_mode='Markdown')
    return GET_TOP_SHINIES

async def get_top_shinies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['account_data']['top_shinies'] = format_bullet_points(update.message.text)
    context.user_data['current_state'] = GET_PURIFIED
    await update.message.reply_text("Enter *Purified Count*:", parse_mode='Markdown')
    return GET_PURIFIED

async def get_purified_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_MEGA_EVOLVE, 'purified', "Enter *Mega Evolutions Unlocked Count*:", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_mega_evolve_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_EVENT, 'mega_evolve', "Enter *Event Pokémon Count*:", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_event_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await text_input_handler(update, context, GET_DELIVERY_METHOD, 'event', "Enter *Delivery Method* (default: Instant Delivery):", input_type=int, default=0, validation_func=lambda x: x >= 0)

async def get_delivery_method_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['account_data']['delivery_method'] = update.message.text.strip() or "Instant Delivery"
    context.user_data['current_state'] = GET_OTHER_ACCOUNTS_LINK
    await update.message.reply_text("Enter *Other Accounts Link* (optional, type /skip to leave blank):", parse_mode='Markdown')
    return GET_OTHER_ACCOUNTS_LINK

async def get_other_accounts_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['account_data']['other_accounts_link'] = update.message.text.strip()
    context.user_data['current_state'] = GET_EMAIL
    await update.message.reply_text("Enter *Account Gmail*:", parse_mode='Markdown')
    return GET_EMAIL

async def get_email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        email = get_validated_input_bot(update.message.text, validation_func=lambda x: '@' in x and '.' in x)
        context.user_data['email'] = email

        keyboard = [
            [KeyboardButton("Jack@bst1")],
            [KeyboardButton("Lost@bst1")],
            [KeyboardButton("Custom Password")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        context.user_data['current_state'] = GET_PASSWORD_CHOICE
        await update.message.reply_text(
            "Choose Password:",
            reply_markup=reply_markup
        )
        return GET_PASSWORD_CHOICE
    except ValueError as e:
        await update.message.reply_text(f"Error: {e}\nPlease enter a valid *Gmail address*.", parse_mode='Markdown')
        return GET_EMAIL

async def get_password_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pwd_choice_text = update.message.text.strip()
    if pwd_choice_text == "Jack@bst1":
        context.user_data['password'] = "Jack@bst1"
        return await generate_output_and_end(update, context)
    elif pwd_choice_text == "Lost@bst1":
        context.user_data['password'] = "Lost@bst1"
        return await generate_output_and_end(update, context)
    elif pwd_choice_text == "Custom Password":
        context.user_data['current_state'] = GET_CUSTOM_PASSWORD
        await update.message.reply_text("Enter *Custom Password*:", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
        return GET_CUSTOM_PASSWORD
    else:
        keyboard = [
            [KeyboardButton("Jack@bst1")],
            [KeyboardButton("Lost@bst1")],
            [KeyboardButton("Custom Password")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Invalid choice. Please choose from the given options.", reply_markup=reply_markup)
        return GET_PASSWORD_CHOICE

async def get_custom_password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['password'] = update.message.text.strip()
    return await generate_output_and_end(update, context)

async def generate_output_and_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Generates and sends the final output."""
    account_data = context.user_data['account_data']
    email = context.user_data['email']
    password = context.user_data['password']

    title = generate_pogo_title(account_data)
    description = generate_pogo_description(account_data)
    credentials = generate_pogo_credentials(email, password)

    # Format output for Telegram mono font using MarkdownV2
    # Escape any special MarkdownV2 characters in the content
    def escape_markdown_v2(text):
        # List of special characters in MarkdownV2 that need to be escaped
        # Only escape if not part of a code block. For our purpose,
        # since we're putting everything in code blocks, we don't need to escape inside.
        # But for regular text, you would escape _, *, [, ], (, ), ~, `, >, #, +, -, =, |, {, }, ., !
        # For simplicity, if we wrap the whole thing in ```, we don't need to escape inside
        return text.replace('.', '\\.').replace('-', '\\-').replace('!', '\\!').replace('(', '\\(').replace(')', '\\)')\
                   .replace('+', '\\+').replace('{', '\\{').replace('}', '\\}').replace('=', '\\=').replace('|', '\\|')\
                   .replace('[', '\\[').replace(']', '\\]').replace('`', '\\`').replace('~', '\\~').replace('>', '\\>')\
                   .replace('#', '\\#')


    final_output = (
        f"🔥 *GENERATED TITLE:*\n`{escape_markdown_v2(title)}`\n\n" # Use single backticks if title is short
        f"📝 *GENERATED DESCRIPTION:*\n```\n{escape_markdown_v2(description)}\n```\n\n"
        f"🔑 *GENERATED CREDENTIALS:*\n`{escape_markdown_v2(credentials)}`\n\n"
        "*All content is ready to be copied!*"
    )
    # Note: `escape_markdown_v2` is simplistic here. For complex nested markdown,
    # it's safer to avoid mixing formats or use a library that handles it robustly.
    # For content inside triple backticks, telegram client handles it as raw text, no escape needed.
    # So for the actual final_output string, I've adjusted `escape_markdown_v2` to be
    # more appropriate for the *labels* and then rely on ``` for the content itself.
    # Let's adjust the escape function to be more focused on text outside code blocks.

    # Revised escape_markdown_v2 for header text only
    def escape_markdown_v2_header(text):
        return text.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]')\
                   .replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('`', '\\`')\
                   .replace('>', '\\>').replace('#', '\\#').replace('+', '\\+').replace('-', '\\-')\
                   .replace('=', '\\=').replace('|', '\\|').replace('{', '\\{').replace('}', '\\}')\
                   .replace('.', '\\.').replace('!', '\\!')

    final_output = (
        f"🔥 *GENERATED TITLE:*\n`{title}`\n\n" # Use single backticks for compact title
        f"📝 *GENERATED DESCRIPTION:*\n```\n{description}\n```\n\n" # Full block for description
        f"🔑 *GENERATED CREDENTIALS:*\n`{credentials}`\n\n" # Single backticks for credentials
        f"_{escape_markdown_v2_header('All content is ready to be copied!')}_" # Example of escaping for regular text
    )

    await update.message.reply_text(final_output, parse_mode='MarkdownV2', reply_markup=ReplyKeyboardRemove())
    context.user_data.clear() # Clear data after generating output
    return ConversationHandler.END


# --- Main Bot Setup ---
def main():
    # It's highly recommended to use environment variables for your token, e.g., os.getenv('TELEGRAM_BOT_TOKEN')
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set. Please set it before running the bot.")
        sys.exit(1) # Exit if token is not found

    application = Application.builder().token(TOKEN).build()

    # Create the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("generate", start) # Alias for start
        ],
        states={
            GET_LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_level_handler)],
            GET_TEAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_team_handler)],
            GET_POKEMON_STORAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_pokemon_storage_handler)],
            GET_LEGENDARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_legendary_handler)],
            GET_SHINY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_shiny_handler)],
            GET_HUNDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_hundo_handler)],
            GET_OVER_3000: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_over_3000_handler)],
            GET_LEGENDARY_SHINY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_legendary_shiny_handler)],
            GET_LUCKY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_lucky_handler)],
            GET_MYTHICAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_mythical_handler)],
            GET_SHADOW: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_shadow_handler)],
            GET_ITEM_STORAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_item_storage_handler)],
            GET_STARDUST: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_stardust_handler)],
            GET_ACCOUNT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_account_id_handler)],
            GET_SHUNDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_shundo_handler)],
            GET_POKE_COINS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_poke_coins_handler)],
            GET_NAME_CHANGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name_change_handler)],
            GET_OVER_2500: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_over_2500_handler)],
            GET_TOP_LEGENDARIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_top_legendaries_handler)],
            GET_TOP_SHINIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_top_shinies_handler)],
            GET_PURIFIED: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_purified_handler)],
            GET_MEGA_EVOLVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_mega_evolve_handler)],
            GET_EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_event_handler)],
            GET_DELIVERY_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_delivery_method_handler)],
            GET_OTHER_ACCOUNTS_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_other_accounts_link_handler)],
            GET_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email_handler)],
            GET_PASSWORD_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password_choice_handler)],
            GET_CUSTOM_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_custom_password_handler)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("skip", skip) # Add skip command to fallbacks
        ],
        allow_reentry=True # Allows /start or /generate to restart conversation
    )

    application.add_handler(conv_handler)

    logger.info("Bot starting polling...")
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # This global is no longer strictly needed in this bot setup as pyperclip isn't used
    # and os.getenv handles the token. Leaving it as a harmless placeholder.
    global HAS_PYPERCLIP
    HAS_PYPERCLIP = False

    main()