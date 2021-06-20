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
def user() -> User:
    u = User(first_name="Patrick",
             last_name="Martin",
             address="1 rue de chemin, 75000 Paris",
             phone_number="0123456798")
    u.save()
    return u


@pytest.fixture()
def random_user():
    return User(first_name="John",
                last_name="Cena",
                address="1 rue de chemin, 75000 Paris",
                phone_number="0123456798")


def test_first_row_id(user, random_user):
    assert user._rowid() == 1
    random_user.save()
    assert random_user._rowid() == 2


def test_assignations(user):
    assert user.first_name == "Patrick"
    assert user.last_name == "Martin"
    assert user.address == "1 rue de chemin, 75000 Paris"
    assert user.phone_number == "0123456798"


def test_full_name(user):
    assert user.full_name == "Patrick Martin"


def test_exists(user):
    assert user._exists()


def test_does_not_exists(random_user):
    assert not random_user._exists()


def test_db_info(user):
    assert isinstance(user.db_info(), dict)

    assert user.db_info()["first_name"] == "Patrick"
    assert user.db_info()["last_name"] == "Martin"
    assert user.db_info()["address"] == "1 rue de chemin, 75000 Paris"
    assert user.db_info()["phone_number"] == "0123456798"


def test_check_phone():
    good_user = User(first_name="Jean",
                     last_name="Smith",
                     address="1 rue du chemin, 75015, Paris",
                     phone_number="0123465789")
    bad_user = User(first_name="Jean",
                    last_name="Smith",
                    address="1 rue du chemin, 75015, Paris",
                    phone_number="abcd")

    with pytest.raises(ValueError) as error:
        bad_user._check_phone_number()

    assert error.value.args[0] == "Le nombre 'abcd' est incorrecte."

    assert good_user._check_phone_number()


def test_check_names_empty():
    bad_user = User(first_name="",
                    last_name="",
                    address="1 rue du chemin, 75015, Paris",
                    phone_number="abcd")

    with pytest.raises(ValueError) as error:
        bad_user._check_names()

    assert error.value.args[0] == "Le prénom et le nom de famille ne doivent pas êtres vides"


def test_check_invalid_characters():
    bad_user = User(first_name="Patrick P34T5P45L££¨¨%µ%",
                    last_name="claude 8942'(_ç'è",
                    address="1 rue du chemin, 75015, Paris",
                    phone_number="abcd")

    with pytest.raises(ValueError) as error:
        bad_user._check_names()

    assert error.value.args[0] == "Nom invalide 'Patrick P34T5P45L££¨¨%µ% claude 8942'(_ç'è'"


def test_delete():
    first_user = User(first_name="Jean",
                      last_name="Smith",
                      address="1 rue du chemin, 75015, Paris",
                      phone_number="0123456789")

    second_user = User(first_name="Patrick",
                       last_name="William",
                       address="1 rue du chemin, 75015, Paris",
                       phone_number="0123456789")

    third_user = User(first_name="Patrick",
                      last_name="William",
                      address="1 rue du chemin, 75015, Paris",
                      phone_number="0123456789")

    first_user.save()
    second_user.save()
    first_user.delete()
    second_user.delete()
    assert not first_user._exists()
    assert not second_user._exists()

    with pytest.raises(ValueError) as error:
        third_user.delete()

    assert error.value.args[0] == "'Patrick William' n'est pas dans la base de donnée"


def test_save():
    first_user = User(first_name="Jean",
                      last_name="Smith",
                      address="1 rue du chemin, 75015, Paris",
                      phone_number="0123456789")

    second_user = User(first_name="Jean",
                       last_name="Smith",
                       address="1 rue du chemin, 75015, Paris",
                       phone_number="0123456789")

    first_user.save()

    with pytest.raises(OverflowError) as error:
        second_user.save()

    assert error.value.args[0] == "L'utilisateur 'Jean Smith' est déjà dans la liste"
