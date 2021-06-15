from pathlib import Path

from crm import User

import pytest
from sqlite3cm import OpenSqlite3db


@pytest.fixture(autouse=True)
def setup_db():
    User.DB = Path(__file__).parent.resolve() / "test_database.db"

    with OpenSqlite3db(User.DB) as (conn, cursor):
        cursor.execute("""
            DROP TABLE IF EXISTS people
             """)


@pytest.fixture
def user():
    u = User(first_name="Patrick",
             last_name="Martin",
             address="1 rue de chemin, 75000 Paris",
             phone_number="0123456798")
    u.save()
    return u


@pytest.fixture()
def random_user():
    return User(first_name="Patrick",
                last_name="Martin",
                address="1 rue de chemin, 75000 Paris",
                phone_number="0123456798")


def test_assignations(user):
    assert user.first_name == "Patrick"
    assert user.last_name == "Martin"
    assert user.address == "1 rue de chemin, 75000 Paris"
    assert user.phone_number == "0123456798"


def test_full_name(user):
    assert user.full_name == "Patrick Martin"


def test_exists(user):
    assert user.exists()


def test_does_not_exists(random_user):
    assert not random_user.exists()


def test_db_info(user):
    assert type(user.db_info) == dict
    print(type(user.db_info))

    assert user.db_info["first_name"] == "Patrick"
    assert user.db_info["last_name"] == "Martin"
    assert user.db_info["address"] == "1 rue de chemin, 75000 Paris"
    assert user.db_info["phone_number"] == "0123456798"


def test_not_db_info(random_user):
    assert random_user.db_info is None


def test__check_all():
    assert False


def test__check_names():
    assert False


def test__check_phone_number():
    assert False


def test_delete():
    assert False


def test_save():
    assert False
