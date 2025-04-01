import pytest, os
from typing import TYPE_CHECKING
from pytest import mark
from unittest import mock
from secrets import token_hex
from collections import Counter
from firebase_admin import credentials, initialize_app
from faker import Faker
from redis_om import NotFoundError, get_redis_connection
from fastapi.security import HTTPAuthorizationCredentials

from dev.data import SEED_ROLES
from auth import Account, validate_token, AccountSvc, AccountCache, Can, UserOptions, Opt
from core import InvalidToken, ic
from models.auth_models import ProfileMod


if TYPE_CHECKING:
    from core import ic, utils, ForbiddenException, OptionsSvc
    from models.common_models import OptionMod

    # from core.dependencies import validate_token
    # from core.services import AccountSvc

fake = Faker()

fake_email = fake.email()
fake_hash = token_hex(14)
mock_decoded_token = {'aud': 'foo-123',
                      'auth_time': 1735373729,
                      'email': fake_email,
                      'email_verified': True,
                      'exp': 1735377329,
                      'firebase': {'identities': {'email': [fake_email],
                                                  'google.com': [fake.sha1()]},
                                   'sign_in_provider': 'google.com'},
                      'iat': 1735373729,
                      'iss': 'https://securetoken.google.com/foo-123',
                      'name': fake.user_name(),
                      'picture': fake.image_url(),
                      'sub': fake_hash,
                      'uid': fake_hash,
                      'user_id': fake_hash}


class TestToken:
    # @mark.focus
    @mock.patch('auth.dependencies.auth.verify_id_token', return_value=mock_decoded_token)
    def test_valid_token_mock(self, _):
        mock_token = 'valid_token'
        creds = HTTPAuthorizationCredentials(scheme='Bearer', credentials=mock_token)
        result = validate_token(creds)
        assert result == mock_decoded_token


    # @mark.focus
    @mock.patch('auth.dependencies.auth.verify_id_token', side_effect=InvalidToken)
    def test_invalid_token_mock(self, _):
        mock_token = "invalid_token"
        creds = HTTPAuthorizationCredentials(scheme='Bearer', credentials=mock_token)
        with pytest.raises(InvalidToken, match='INVALID_TOKEN'):
            validate_token(creds)


    # @mark.skip
    # @mark.focus
    # def test_invalid_token_abc(self, invalid_token):
    #     ic(invalid_token)
    #     with pytest.raises(InvalidIdTokenError):
    #         auth.verify_id_token(invalid_token)

    # @mark.skip
    # @mark.focus
    async def test_invalid_token(self, invalid_token, client):
        """You need a valid token to run this test."""
        headers = dict(authorization=f'Bearer {invalid_token}')
        response = await client.get('/test/validate_token', headers=headers)
        assert response.status_code == 403

    # @mark.skip
    # # @mark.focus
    # async def test_valid_token(self, client):
    #     """You need a valid token to run this test."""
    #     headers = dict(authorization=f'Bearer {os.getenv("DEV_TOKEN_VALID")}')
    #     response = await client.get('/test/validate_token', headers=headers)
    #     token_data = response.json()
    #     ic(response.status_code)
    #     ic(token_data)
    #     # assert response.status_code == 200

    # @mark.skip
    # # @mark.focus
    # async def test_current_user_dependency(self, client):
    #     """You need a valid token to run this test."""
    #     headers = dict(authorization=f'Bearer {os.getenv("DEV_TOKEN_VALID")}')
    #     response = await client.get('/test/current_user', headers=headers)
    #     user = response.json()
    #
    #     # if user['uid'] == os.getenv('DEV_UID_SUPERADMIN'):
    #     #     assert user['email'] == os.getenv('DEV_EMAIL_SUPERADMIN')
    #     # elif user['uid'] == os.getenv('DEV_UID_ADMIN'):
    #     #     assert user['email'] == os.getenv('DEV_EMAIL_ADMIN')
    #     # elif user['uid'] == os.getenv('DEV_UID_MODERATOR'):
    #     #     assert user['email'] == os.getenv('DEV_EMAIL_MODERATOR')
    #     # elif user['uid'] == os.getenv('DEV_UID_USER'):
    #     #     assert user['email'] == os.getenv('DEV_EMAIL_USER')


class TestAccount:
    def setup_class(self):  # noqa
        creds = credentials.Certificate(os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH'))
        initialize_app(creds)
        ic('[Fireabase inititialized]')
        ic('TEST_STARTED')


    # def teardown_class(self):  # noqa
    #     ic('TEST_ENDED')

    # @mark.focus
    async def test_create_account(self, session):
        account_min = await Account.create(uid=token_hex(14), email=fake.email(), provider='fake-provider',
                                           session=session)
        account_full = await Account.create(uid=token_hex(14), email=fake.email(), avatar=fake.image_url(),
                                            firstname=fake.first_name(), lastname=fake.last_name(),
                                            username=fake.user_name(), display=fake.word(), gender='male',
                                            social=dict(foo=fake.url(), bar=fake.url()),
                                            provider='fake-provider', website=fake.url(), session=session)

        cache_data = Account.get_cache(account_full.uid)
        account_cache = cache_data.to_account()

        account_select = await session.get(Account, account_full.id)
        account_email = await AccountSvc.get_by_email(account_full.email, session=session)
        account_uid = await AccountSvc.get_by_uid(account_full.uid, session=session)

        assert account_cache.model_dump() == account_full.model_dump()
        assert account_select.model_dump() == account_full.model_dump()
        assert account_email.model_dump() == account_full.model_dump()
        assert account_uid.model_dump() == account_full.model_dump()

        cache_data_min = Account.get_cache(account_min.uid)
        account_cache_min = cache_data_min.to_account()

        account_select_min = await session.get(Account, account_min.id)
        account_email_min = await AccountSvc.get_by_email(account_min.email, session=session)
        account_uid_min = await AccountSvc.get_by_uid(account_min.uid, session=session)

        assert account_cache_min.model_dump() == account_min.model_dump()
        assert account_select_min.model_dump() == account_min.model_dump()
        assert account_email_min.model_dump() == account_min.model_dump()
        assert account_uid_min.model_dump() == account_min.model_dump()

        # Cleanup
        AccountCache.delete(account_min.uid)
        AccountCache.delete(account_full.uid)
        await session.delete(account_min)
        await session.delete(account_full)
        await session.commit()


    # @mark.focus
    async def test_account_contents(self, account_):
        assert account_.email
        assert account_.uid
        assert account_.id
        # ic(account_.model_dump())
        assert account_.roles
        assert not account_.custom_permissions
        # assert set(account_.permissions) == set(
        #     utils.reduce_permissions([*SEED_ROLES['user'], *SEED_ROLES['devtesting']]))

        profile: ProfileMod = account_.profile
        if profile.firstname or profile.lastname:
            assert f'{profile.firstname} {profile.lastname}'.strip() == profile.fullname


    # @mark.focus
    async def test_get_account(self, session, account_):
        account1 = await Account.get(uid=account_.uid, session=session)
        assert account1.is_cache

        cache = AccountCache.get(account_.uid)
        account_cache = cache.to_account()
        assert account_cache.is_cache

        AccountCache.delete(cache.pk)
        with pytest.raises(NotFoundError):
            AccountCache.get(account_.uid)

        account2 = await Account.get(uid=account_.uid, session=session)
        account3 = await Account.get(uid=account_.uid, session=session)
        account4 = await Account.get(uid=account_.uid, use_db=True, session=session)
        assert not account2.is_cache
        assert account3.is_cache
        assert not account4.is_cache


    # @mark.focus
    async def test_account_options(self, account_):
        options = account_.options
        assert isinstance(options, UserOptions)


    # @mark.focus
    async def test_update_options(self, account_, session):
        new_int = 2345
        account = await Account.get(uid=account_.uid, session=session)
        accountdb = await Account.get(uid=account_.uid, use_db=True, session=session)
        assert account.is_cache
        assert not accountdb.is_cache
        assert account.options.items_per_page != new_int
        assert accountdb.options.items_per_page != new_int

        await account.update_options({Opt.items_per_page.name: new_int}, session=session)

        account = await Account.get(uid=account_.uid, session=session)
        accountdb = await Account.get(uid=account_.uid, use_db=True, session=session)
        assert account.is_cache
        assert not accountdb.is_cache
        assert account.options.items_per_page == new_int
        assert accountdb.options.items_per_page == new_int


    # @mark.focus
    async def test_get_options(self, account_, session):
        options = await AccountSvc.get_options(account_.id, session=session)
        assert account_.options == UserOptions(**options)

        await account_.update_options({'timezone': 'FOO'}, session=session)
        options = await AccountSvc.get_options(account_.id, session=session)
        assert account_.options == UserOptions(**options)


    # @mark.focus
    async def test_update_db(self, account_, session):
        new_display = 'foobar'

        account = await Account.get(uid=account_.uid, session=session)
        accountdb = await Account.get(uid=account_.uid, use_db=True, session=session)
        assert account.is_cache
        assert not accountdb.is_cache
        assert account.display != new_display
        assert accountdb.display != new_display

        await AccountSvc.update(account_.uid, {'display': new_display}, session=session)

        account = await Account.get(uid=account_.uid, session=session)
        accountdb = await Account.get(uid=account_.uid, use_db=True, session=session)
        assert account.is_cache
        assert not accountdb.is_cache
        assert account.display != new_display  # cache stays the same
        assert accountdb.display == new_display


    # @mark.focus
    def test_collate_permissions(self, account_):
        redis = get_redis_connection()

        ll = []
        for role in account_.roles:
            ll.extend(redis.lrange(f'role:{role}', 0, -1))
        assert Counter(account_.permissions) == Counter(Account._reduce_permissions(ll))


    @mark.focus
    async def test_can_roles_permissions(self, generate_accounts, session):
        user, moderator, admin, superadmin = generate_accounts
        user_can_ban = await AccountSvc.get_by_email('user1@mail.com', session=session)
        assert not set(user.roles) & {'moderator', 'admin', 'superadmin', 'monitor'}
        assert set(moderator.roles) & {'user', 'moderator', 'monitor'} == {'user', 'moderator', 'monitor'}
        assert not set(moderator.roles) & {'admin', 'superadmin'} == {'admin', 'superadmin'}
        assert set(admin.roles) & {'user', 'admin', 'monitor'} == {'user', 'admin', 'monitor'}
        assert not set(admin.roles) & {'superadmin'} == {'superadmin'}
        assert set(superadmin.roles) & {'user', 'superadmin', 'monitor'} == {'user', 'superadmin', 'monitor'}

        # User
        assert user.can(Can.upload_image)
        assert not user.can(Can.read_other_account)
        assert not user.can(Can.ban_user)
        assert not user.can(Can.create_user)
        assert not user.can(Can.create_admin)
        assert not user.is_moderator and not user.is_admin and not user.is_superadmin

        # User can ban
        assert user_can_ban.can(Can.upload_image)
        assert not user_can_ban.can(Can.read_other_account)
        assert user_can_ban.can(Can.ban_user)
        assert not user_can_ban.can(Can.create_user)
        assert not user_can_ban.can(Can.create_admin)
        assert not user_can_ban.is_moderator and not user.is_admin and not user.is_superadmin

        # Moderator
        assert moderator.can(Can.upload_image)
        assert moderator.can(Can.read_other_account)
        assert moderator.can(Can.ban_user)
        assert not moderator.can(Can.create_user)
        assert not moderator.can(Can.create_admin)
        assert moderator.is_moderator and not moderator.is_admin and not moderator.is_superadmin

        # Admin
        assert admin.can(Can.upload_image)
        assert admin.can(Can.read_other_account)
        assert admin.can(Can.ban_user)
        assert admin.can(Can.create_user)
        assert not admin.can(Can.create_admin)
        assert not admin.is_moderator and admin.is_admin and not admin.is_superadmin

        # Superadmin
        assert superadmin.can(Can.upload_image)
        assert superadmin.can(Can.read_other_account)
        assert superadmin.can(Can.ban_user)
        assert superadmin.can(Can.create_user)
        assert superadmin.can(Can.create_admin)
        assert not superadmin.is_moderator and not superadmin.is_admin and superadmin.is_superadmin


    # @mark.focus
    async def test_update_cache(self, account_, session):
        account = await Account.get(uid=account_.uid, session=session)
        assert account.is_cache

        new_firstname = 'foobar'
        assert account_.firstname != new_firstname
        assert account_.update_cache({'firstname': new_firstname})

        cache = Account.get_cache(account_.uid)
        assert cache.firstname == new_firstname


    # @mark.focus
    async def test_unique_email(self, account_, session):
        assert not await AccountSvc.is_unique_email(account_.email, session=session)
        assert await AccountSvc.is_unique_email(fake.email(), session=session)


    # @mark.focus
    async def test_unique_username(self, account_, session):
        assert not await AccountSvc.is_unique_username(account_.username, session=session)
        assert await AccountSvc.is_unique_username(fake.user_name(), session=session)


class _TestAccountManagement:
    # @mark.focus
    async def test_ban_failed(self, generate_accounts, session):
        user, moderator, admin, superadmin = generate_accounts
        ban_user, ban_moderator, ban_admin, ban_superadmin = generate_accounts
        assert not user.is_banned
        assert not moderator.is_banned
        assert not admin.is_banned
        assert not superadmin.is_banned
        assert not ban_user.is_banned
        assert not ban_moderator.is_banned
        assert not ban_admin.is_banned
        assert not ban_superadmin.is_banned

        # User
        with pytest.raises(ForbiddenException):
            await Account.ban(authorization=user, to_ban=user, session=session)
        with pytest.raises(ForbiddenException):
            await Account.ban(authorization=user, to_ban=ban_user, session=session)
        with pytest.raises(ForbiddenException):
            await Account.ban(authorization=user, to_ban=ban_moderator, session=session)
        with pytest.raises(ForbiddenException):
            await Account.ban(authorization=user, to_ban=ban_admin, session=session)
        with pytest.raises(ForbiddenException):
            await Account.ban(authorization=user, to_ban=ban_superadmin, session=session)

        # Moderator
        with pytest.raises(ForbiddenException):
            await Account.ban(authorization=moderator, to_ban=moderator, session=session)
        with pytest.raises(ForbiddenException):
            await Account.ban(authorization=moderator, to_ban=ban_moderator, session=session)
        with pytest.raises(ForbiddenException):
            await Account.ban(authorization=moderator, to_ban=ban_admin, session=session)
        with pytest.raises(ForbiddenException):
            await Account.ban(authorization=moderator, to_ban=ban_superadmin, session=session)

        # Admin
        with pytest.raises(ForbiddenException):
            await Account.ban(authorization=admin, to_ban=admin, session=session)
        with pytest.raises(ForbiddenException):
            await Account.ban(authorization=admin, to_ban=ban_admin, session=session)
        with pytest.raises(ForbiddenException):
            await Account.ban(authorization=admin, to_ban=ban_superadmin, session=session)


    # @mark.focus
    async def test_ban_user(self, account_factory, session):
        user1 = await account_factory(session=session)
        user2 = await account_factory(session=session)
        user3 = await account_factory(session=session)
        moderator = await account_factory(is_moderator=True, session=session)
        admin = await account_factory(is_admin=True, session=session)
        superadmin = await account_factory(is_superadmin=True, session=session)

        # Moderator
        assert not user1.is_banned
        await Account.ban(authorization=moderator, to_ban=user1, session=session)
        assert user1.is_banned
        assert user1.banned_by == moderator
        account = await Account.get(user1.uid, session=session)
        assert account.is_cache
        assert account.is_banned
        # account = await Account.get(user1.uid, use_db=True, session=session)
        # assert not account.is_cache
        # assert account.is_banned

        # Admin
        assert not user2.is_banned
        await Account.ban(authorization=admin, to_ban=user2, session=session)
        assert user2.is_banned
        assert user2.banned_by == admin
        account = await Account.get(user2.uid, session=session)
        assert account.is_cache
        assert account.is_banned
        # account = await Account.get(user2.uid, use_db=True, session=session)
        # assert not account.is_cache
        # assert account.is_banned

        # Superadmin
        assert not user3.is_banned
        await Account.ban(authorization=superadmin, to_ban=user3, session=session)
        assert user3.is_banned
        assert user3.banned_by == superadmin
        account = await Account.get(user3.uid, session=session)
        assert account.is_cache
        assert account.is_banned
        # account = await Account.get(user3.uid, use_db=True, session=session)
        # assert not account.is_cache
        # assert account.is_banned

        # Cleanup
        await session.delete(user1)
        await session.delete(user2)
        await session.delete(user3)
        await session.delete(moderator)
        await session.delete(admin)
        await session.delete(superadmin)
        await session.commit()


    # @mark.focus
    async def test_ban_moderator(self, account_factory, session):
        moderator1 = await account_factory(is_moderator=True, session=session)
        moderator2 = await account_factory(is_moderator=True, session=session)
        admin = await account_factory(is_admin=True, session=session)
        superadmin = await account_factory(is_superadmin=True, session=session)

        # Admin
        assert not moderator1.is_banned
        await Account.ban(authorization=admin, to_ban=moderator1, session=session)
        assert moderator1.is_banned
        assert moderator1.banned_by == admin
        account = await Account.get(moderator1.uid, session=session)
        assert account.is_cache
        assert account.is_banned
        # account = await Account.get(moderator1.uid, use_db=True, session=session)
        # assert not account.is_cache
        # assert account.is_banned

        # Superadmin
        assert not moderator2.is_banned
        await Account.ban(authorization=superadmin, to_ban=moderator2, session=session)
        assert moderator2.is_banned
        assert moderator2.banned_by == superadmin
        account = await Account.get(moderator2.uid, session=session)
        assert account.is_cache
        assert account.is_banned
        # account = await Account.get(moderator2.uid, use_db=True, session=session)
        # assert not account.is_cache
        # assert account.is_banned

        # Cleanup
        await session.delete(moderator1)
        await session.delete(moderator2)
        await session.delete(admin)
        await session.delete(superadmin)
        await session.commit()


    # @mark.focus
    async def test_ban_admin(self, account_factory, session):
        admin = await account_factory(is_admin=True, session=session)
        superadmin = await account_factory(is_superadmin=True, session=session)

        # Superadmin
        assert not admin.is_banned
        await Account.ban(authorization=superadmin, to_ban=admin, session=session)
        assert admin.is_banned
        assert admin.banned_by == superadmin
        account = await Account.get(admin.uid, session=session)
        assert account.is_cache
        assert account.is_banned
        # account = await Account.get(admin.uid, use_db=True, session=session)
        # assert not account.is_cache
        # assert account.is_banned

        # Cleanup
        await session.delete(admin)
        await session.delete(superadmin)
        await session.commit()


    # @mark.focus
    async def test_unban(self, account_factory, session):
        user1 = await account_factory(session=session)
        user2 = await account_factory(session=session)
        user3 = await account_factory(session=session)
        moderator = await account_factory(is_moderator=True, session=session)
        admin = await account_factory(is_admin=True, session=session)
        superadmin = await account_factory(is_superadmin=True, session=session)

        assert not user1.is_banned
        assert not user2.is_banned
        assert not user3.is_banned
        account = await Account.ban(authorization=admin, to_ban=user1, session=session)
        assert account.banned_at is not None
        assert account.banned_by_id is not None
        account = await Account.ban(authorization=admin, to_ban=user2, session=session)
        assert account.banned_at is not None
        assert account.banned_by_id is not None
        account = await Account.ban(authorization=admin, to_ban=user3, session=session)
        assert account.banned_at is not None
        assert account.banned_by_id is not None
        assert user1.is_banned
        assert user2.is_banned
        assert user3.is_banned

        account = await Account.unban(authorization=moderator, to_unban=user1, session=session)
        assert account.banned_at is None
        assert account.banned_by_id is None
        account = await Account.unban(authorization=admin, to_unban=user2, session=session)
        assert account.banned_at is None
        assert account.banned_by_id is None
        account = await Account.unban(authorization=superadmin, to_unban=user3, session=session)
        assert account.banned_at is None
        assert account.banned_by_id is None
        assert not user1.is_banned
        assert not user2.is_banned
        assert not user3.is_banned

        # Cleanup
        await session.delete(user1)
        await session.delete(user2)
        await session.delete(user3)
        await session.delete(moderator)
        await session.delete(admin)
        await session.delete(superadmin)
        await session.commit()


class _TestRole:
    # @mark.focus
    async def test_get(self, role_, session):
        # red = get_redis_connection()
        # assert set(await models.Role.get(role_.name, session=session)) == role_.permissions
        #
        # cache_key = f'role:{role_.name}'
        # assert red.exists(cache_key)
        # red.delete(cache_key)
        # assert not red.exists(cache_key)
        #
        # assert set(await models.Role.get(role_.name, session=session)) == role_.permissions  # No cache
        # assert red.exists(cache_key)
        # assert set(await models.Role.get(role_.name, session=session)) == role_.permissions  # With cache
        pass
