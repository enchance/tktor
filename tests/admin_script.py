from idna.idnadata import scripts
from pytest import mark
from typer.testing import CliRunner
from faker import Faker

from core import ic
from core.config import get_session_context_script
from account.models import Role, RoleSvc
from dev.scripts.admin import app


fake = Faker()
runner = CliRunner()


# class TestAdminScript:
#     @mark.focus
#     async def test_create_update_role(self):
#         try:
#             result = runner.invoke(app, ['role', fake.word(), 'this that there'])
#             # assert result.exit_code == 0
#             ic(result.exit_code)
#             ic(result.stdout)
#         except Exception as e:
#             ic(e)
#
#
#     async def test_account_role(self):
#         pass
#
#
#     async def test_account_permissions(self):
#         pass
