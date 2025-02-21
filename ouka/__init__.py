import dotenv
import os

__all__ = (
    "__BOT_NAME__",
    "__DEBUG_DB_PATH__",
    "__EXTENSIONS_PATH__",
    "__PROD_DB_PATH__",
    "__TOKEN__",
    "__VERSION__",
    "debug_mode",
    "wipe",
)

# Load the enviornment variables.
dotenv.load_dotenv()

"""
Change to `False` to disable debug mode and use the production database.
"""
debug_mode = True

"""
Change to `True` to wipe the debug database on bot exit.
Will only work if `debug_mode` is set to `True`.
"""
wipe = True

# Constant paths for use throughout the bot
__BOT_NAME__ = "ouka"
__VERSION__ = "0.1.0"
__DEBUG_DB_PATH__ = "data/dynamic/debug.db"
__PROD_DB_PATH__ = "data/dynamic/prod.db"
__EXTENSIONS_PATH__ = f"{__BOT_NAME__}/extensions"

# Discord bot token (Always change in .env)
__TOKEN__ = os.environ["TOKEN"]
