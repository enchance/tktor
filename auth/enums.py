from __future__ import annotations
from enum import StrEnum, auto


# Update triggers.sql
class Opt(StrEnum):
    # System
    site_name = auto()
    site_description = auto()
    site_icon = auto()
    site_url = auto()
    admin_email = auto()
    home_path = auto()
    users_can_register = auto()
    comment_status = auto()
    comment_anonymous = auto()
    comment_threads = auto()
    comment_depth = auto()
    show_avatars = auto()
    avatar_default_url = auto()

    # User
    date_format = auto()
    time_format = auto()
    timezone = auto()
    items_per_page = auto()
    comment_publish_delay = auto()
    comments_per_page = auto()
    comment_order = auto()
    comments_blacklist = auto()
    max_upload_mb = auto()


class SysOps(StrEnum):
    site_name = auto()
    site_description = auto()
    site_icon = auto()
    site_url = auto()
    admin_email = auto()
    home_path = auto()
    users_can_register = auto()
    comment_status = auto()
    comment_anonymous = auto()
    comment_threads = auto()
    comment_depth = auto()
    show_avatars = auto()
    avatar_default_url = auto()


class Can(StrEnum):
    # User
    upload_image = auto()
    upload_file = auto()
    update_profile = auto()

    # Moderator
    ban_user = auto()

    # Monitor
    read_other_account = auto()
    read_private_account = auto()

    # Admin
    create_user = auto()
    update_user = auto()
    delete_user = auto()
    create_moderator = auto()
    ban_moderator = auto()

    # Superadmin
    create_admin = auto()
    delete_admin = auto()
    update_admin = auto()
    ban_admin = auto()


    def __eq__(self, other: Can | str) -> bool:
        if isinstance(other, Can):
            return self.name == other.name
        return self.name == other
