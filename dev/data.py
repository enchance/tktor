import os, secrets, arrow, json
from faker import Faker
from pydantic import BaseModel
from dotenv import load_dotenv

from core import CommentStatus, ic


# from auth import Opt

load_dotenv()
fake = Faker()

SEED_ROLES = {
    'user': {
        'upload_image',
        'upload_file',
        'update_profile',
    },
    'monitor': {
        'read_other_account',
        'read_private_account',
    },
    'moderator': {
        'ban_user',
    },
    'admin': {
        'create_user',
        'update_user',
        'delete_user',
        'create_moderator',
        'ban_moderator',
    },
    'superadmin': {
        'create_admin',
        'delete_admin',
        'update_admin',
        'ban_admin',
    },
    'devtesting': {
        'win_money',
        '-win_money',
        'eat_food',
        'eat_food',
        'drink_beer',
        'drink_beer',
    },
}
# SEED_ROLES['moderator'].update(SEED_ROLES['user'])
# SEED_ROLES['admin'].update(SEED_ROLES['moderator'])
# SEED_ROLES['superadmin'].update(SEED_ROLES['admin'])

SEED_ACCOUNTS = {
    'superadmin': [
        (os.getenv('DEV_EMAIL_SUPERADMIN'), 'Superadmin', 'Account', os.getenv('DEV_UID_SUPERADMIN'), ['google']),
    ],
    'admin': [
        (os.getenv('DEV_EMAIL_ADMIN'), 'Admin', 'Account', os.getenv('DEV_UID_ADMIN'), ['google']),
    ],
    'moderator': [
        (os.getenv('DEV_EMAIL_MODERATOR'), 'Moderator', 'Account', os.getenv('DEV_UID_MODERATOR'), ['google']),
    ],
    'user': [
        (os.getenv('DEV_EMAIL_USER'), 'User', 'Account', os.getenv('DEV_UID_USER'), ['email']),
        ('user1@mail.com', 'User1', 'Account', secrets.token_hex(16), ['email']),  # custom perm
        ('user2-banned@mail.com', 'User2', 'Account', secrets.token_hex(16), ['email']),  # banned
        ('user3@mail.com', 'User3', 'Account', secrets.token_hex(16), ['email']),
    ],
}

SEED_USER_OPTIONS = [
    {'name': 'date_format', 'value': '%b %d, %Y', 'description': 'Date format'},
    {'name': 'time_format', 'value': '%I:%M%p', 'description': 'Time format'},
    {'name': 'timezone', 'value': 'UTC', 'description': 'Account timezone'},
    {'name': 'items_per_page', 'value': '10', 'description': 'Items to show per page'},
    {'name': 'comment_publish_delay', 'value': '120', 'description': 'Delay in seconds before publishing a comment'},
    {'name': 'comments_per_page', 'value': '10', 'description': 'Number of comments to show per page'},
    {'name': 'comment_order', 'value': 'desc', 'description': 'Ordering of comments'},
    # {'name': 'comments_blacklist', 'value': '', 'description': ''},
    {'name': 'max_upload_mb', 'value': '5', 'description': ''},
    {'name': 'pointer_all_orders', 'value': '0', 'description': 'Date to start fetching all orders'},
    {'name': 'pointer_all_trades', 'value': '0', 'description': 'Date to start fetching all trades'},
]

SEED_SYSTEM_OPTIONS = [
    {'name': 'site_name', 'value': 'Tktor', 'type': 1},
    {'name': 'site_description', 'value': 'Add description here', 'type': 1},
    {'name': 'site_icon', 'value': '', 'type': 1},
    {'name': 'site_url', 'value': 'localhost:8000', 'type': 1},
    {'name': 'admin_email', 'value': 'admin1@mail.com', 'type': 1},
    {'name': 'home_path', 'value': '/home', 'type': 1},
    {'name': 'users_can_register', 'value': True, 'type': 1},
    {'name': 'comment_status', 'value': 'pending', 'type': 1},
    {'name': 'comment_anonymous', 'value': False, 'type': 1},
    {'name': 'comment_threads', 'value': False, 'type': 1},
    {'name': 'comment_depth', 'value': 2, 'type': 1},
    {'name': 'show_avatars', 'value': True, 'type': 1},
    {'name': 'avatar_default_url', 'value': '', 'type': 1},
]

# SEED_TAXONOMY = {
#     'system': [],
#     'user': ['Work', 'Home']
# }

SEED_EXCHANGES = [
    {'name': 'binance', 'prefix': 'bnc', 'display': 'Binance', 'website': 'https://www.binance.com'},
    {'name': 'binanceus', 'prefix': 'bnus', 'display': 'BinanceUS', 'website': 'https://www.binance.us'},
    {'name': 'coinsph', 'prefix': 'cph', 'display': 'CoinsPH', 'website': 'https://coins.ph'},
    {'name': 'coinbase', 'prefix': 'cbs', 'display': 'Coinbase', 'website': 'https://www.coinbase.com'},
]

SEED_SYMBOLS = {'BANANAUSDT', 'EPICUSDT', 'OMUSDT', 'SUSDT', 'ACHUSDT', 'OGUSDT', 'BNXUSDT', 'REDUSDT', 'ZROUSDT',
                'MANAUSDT', 'EGLDUSDT', 'XLMUSDT', 'AVAXUSDT'}
# SEED_SYMBOLS = {'EPICUSDT'}
