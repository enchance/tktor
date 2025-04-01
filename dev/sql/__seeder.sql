BEGIN;

-- INSERTS
-- Role
INSERT INTO auth_role (name)
VALUES ('monitor'),
       ('user'),
       ('moderator'),
       ('admin'),
       ('superadmin'),
       ('devtesting') ON CONFLICT (name) DO NOTHING;

-- ===========================================================================
-- Option
-- Update alongside: dev.seeder.seed (caching)
INSERT INTO app_option (name, value, type)
VALUES ('site_name', 'Tktor', 1),
       ('site_description', 'Track your PNL just because', 1),
       ('site_icon', '', 1),
       ('site_url', 'localhost:8000', 1),
       ('admin_email', 'admin1@mail.com', 1),
       ('home_path', '/home', 1),
       ('users_can_register', 'True', 1),
       ('comment_status', 'pending', 1),
       ('comment_anonymous', 'False', 1),
       ('comment_threads', 'False', 1),
       ('comment_depth', '2', 1),
       ('show_avatars', 'True', 1),
       ('avatar_default_url', '', 1) ON CONFLICT (name, owner_id) DO NOTHING;
-- ===========================================================================
-- ===========================================================================

COMMIT;