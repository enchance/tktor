from pytest import mark
from collections import Counter
from faker import Faker

from core import ic, utils


fake = Faker()


class TestCore:
    pass
    # # @mark.focus
    # @mark.parametrize('datastr', [
    #     'foo, bar, baz',
    #     'foo,bar,baz',
    #     {'foo', 'bar', 'baz'},
    # ])
    # def test_schemas(self, datastr):
    #     foo = SystemOptionsSchema(default_role=datastr)
    #     assert foo.default_role == {'foo', 'bar', 'baz'}
    #     assert isinstance(foo.default_role, set)


    # @mark.focus
    @mark.skip
    async def test_taxonomy(self, session, account_, make_taxonomy):
        foo = await make_taxonomy(name='foo', owner=account_)
        bar = await make_taxonomy(name='bar', owner=account_, parent=foo)
        await session.refresh(foo, ['children'])  # noqa
        await session.refresh(bar, ['parent'])  # noqa

        # stmt = select(Taxonomy).options(selectinload(Taxonomy.children)).where(Taxonomy.id == foo.id)  # noqa
        # exec_ = await session.exec(stmt)
        # foo = exec_.first()

        assert bar.parent == foo
        assert foo.children == [bar]

        await session.delete(account_)
        await session.commit()


class TestUtils:
    # # @mark.focus
    # @mark.parametrize('ll, result', [
    #     (['a', 'b'], ['a', 'b']), (['a'], ['a']), ([], []),
    #     (['a', 'b', '-b'], ['a']), (['-a', '-b'], []),
    #     (['a', 'b', 'a', 'b'], ['a', 'b']),
    #     (['a', 'b', 'a', 'b', '-a'], ['b']),
    #     ([' a    ', 'b', ' -b  '], ['a']),
    #     ([' ', '  '], ['']),
    # ])
    # def test_refactor_permissions(self, ll, result):
    #     assert Counter(utils.reduce_permissions(ll)) == Counter(result)


    # @mark.focus
    @mark.parametrize('val, out', [('Hey You', ('Hey', 'You')), ('Sir Hey You', ('Sir Hey', 'You')),
                                   ('Sir Hey You Phd', ('Sir Hey', 'You Phd')), ('Hey delos You', ('Hey', 'delos You')),
                                   ('Eliza Maria dona Aurora Phd Md', ('Eliza Maria', 'dona Aurora Phd Md'))])
    def test_split_fullname(self, val, out):
        assert utils.split_fullname(val) == out  # type: ignore

    # # @mark.focus
    # async def test_modstr(self, account_, taxonomy_, session):
    #     assert utils.modstr(account_) == f'<Account: {account_.id}>'
    #     assert utils.modstr(account_, 'email', 'display') == f'<Account {account_.id}: {account_.email}, {account_.display}>'
    #     assert utils.modstr(taxonomy_, 'name') == f'<Taxonomy {taxonomy_.id}: {taxonomy_.name}>'
    #
    #     await session.delete(account_)
    #     await session.delete(taxonomy_)
    #     await session.commit()
