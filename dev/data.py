import os, secrets
from faker import Faker
from pydantic import BaseModel

from core import CommentStatus, ic

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
        ('user1@mail.com', 'User1', 'Account', secrets.token_hex(16), ['email']),   # custom perm
        ('user2-banned@mail.com', 'User2', 'Account', secrets.token_hex(16), ['email']),   # banned
        ('user3@mail.com', 'User3', 'Account', secrets.token_hex(16), ['email']),
    ],
}

SEED_USER_OPTIONS = [
    {'name':'date_format', 'value':'%b %d, %Y', 'description':''},
    {'name':'time_format', 'value':'%I:%M%p', 'description':''},
    {'name':'timezone', 'value':'UTC', 'description':''},
    {'name':'items_per_page', 'value':'10', 'description':''},
    {'name':'comment_publish_delay', 'value':'120', 'description':''},
    {'name':'comments_per_page', 'value':'10', 'description':''},
    {'name':'comment_order', 'value':'desc', 'description':''},
    {'name':'comments_blacklist', 'value':'', 'description':''},
    {'name':'max_upload_mb', 'value':'5', 'description':''},
]

# SEED_OPTIONS = {
#     'system': OptionsSchema(
#         site_name='Bulma',
#         site_description='Add description here',
#         site_icon='',
#         site_url='localhost:8000',
#         admin_email='admin1@mail.com',
#         date_format='%b %d, %Y',
#         time_format='%I:%M%p',
#         timezone='UTC',
#         home_path='/home',
#         users_can_register=True,
#         default_role={'account', 'upload'},
#         items_per_page=10,
#         comment_status=CommentStatus.pending,
#         comment_publish_delay=120,
#         comment_anonymous=False,
#         comment_threads=False,
#         comment_depth=2,
#         comments_per_page=10,
#         comment_order='desc',
#         comments_blacklist=set(),
#         show_avatars=True,
#         avatar_default_url='',
#         max_upload_mb=5,
#     ),
#     'user': {
#         'notifications': 'True',
#     }
# }

# SEED_TAXONOMY = {
#     'system': [],
#     'user': ['Work', 'Home']
# }
