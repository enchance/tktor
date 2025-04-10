from pytest import mark
from collections import Counter
from faker import Faker
from sqlmodel import select

from core import ic, utils
from core.models import Taxonomy
from authentication import Role, Account
from exchange import Exchange


fake = Faker()


class TestCore:

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
    async def test_taxonomy(self, session, account_, make_taxonomy):
        parent = await make_taxonomy(name='Foo the one!', account=account_)
        child = await make_taxonomy(name='Bar the two//', account=account_, parent=parent)
        baz = await make_taxonomy(name='Baz the three\\', slug='bt3', account=account_)
        boom = await make_taxonomy(name='Boom the four', slug='', account=account_)

        assert parent.slug == 'foo-the-one'
        assert child.slug == 'bar-the-two'
        assert baz.slug == 'bt3'
        assert boom.slug == 'boom-the-four'

        await session.refresh(parent, ['children'])
        assert not parent.parent
        assert parent.children == [child]
        await parent.add_child(boom, session=session)
        assert parent.children == [child, boom]

        assert child.parent == parent
        assert child.parent_id == parent.id

        # Clean
        # Not needed since account_ cleans after itself


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


    # @mark.focus
    async def test_modstr(self, account_, taxonomy_, session):
        assert str(account_) == f'<Account {account_.id}: {account_.email}>'
        assert utils.modstr(account_) == f'<Account: {account_.id}>'

        assert str(taxonomy_) == f'<Taxonomy {taxonomy_.id}: {taxonomy_.name}>'
        assert (utils.modstr(taxonomy_, 'name', 'slug')
                == (f'<Taxonomy {taxonomy_.id}: {taxonomy_.name}, {taxonomy_.slug}>'))

        # Clean
        # Not needed since account_ cleans after itself

