import re
import sqlite3
import string
from pathlib import Path
# from pprint import pprint
from typing import Union

# from faker import Faker
from sqlite3cm import OpenSqlite3db


class User:
    DB = Path(__file__).parent.parent.resolve() / "db.sqlite3"

    def __init__(self, first_name: str, last_name: str, phone_number: str = "", address: str = "",
                 **trash_args):
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = f"{self.first_name} {self.last_name}"
        self.phone_number = phone_number
        self.address = address
        self._init_db()

    def __repr__(self):
        return f"User({self.full_name})"

    def __str__(self):
        return f"""
        La personne s'appele {self.full_name},
        son numéro de telephone est {self.phone_number}
        est son addresse est {self.address}.
        """

    def db_info(self, throw_error: bool = True) -> Union[dict, None]:
        conn = sqlite3.connect(User.DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM people
        WHERE first_name == :instance_first_name
        AND
        last_name == :instance_last_name
        """, {
            "instance_first_name": self.first_name,
            "instance_last_name": self.last_name
        })

        info = cursor.fetchone()

        if info is None:
            if throw_error:
                raise ValueError(f"L'utilisateur '{self.full_name}' n'est pas dans la base de données")
            else:
                return None

        return dict(info)

    @staticmethod
    def _init_db() -> bool:
        with OpenSqlite3db(User.DB) as (conn, cursor):
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS people
                (
                    first_name text,
                    last_name text,
                    full_name text,
                    phone_number text,
                    address text
                )
                """)

        return True

    def _check_all(self) -> bool:
        self._check_phone_number()
        self._check_names()
        return True

    def _check_phone_number(self) -> bool:
        ok_number = re.sub(r"[+()\s]*", "", self.phone_number)
        if len(ok_number) < 10 or not ok_number.isdigit():
            raise ValueError(f"Le nombre '{self.phone_number}' est incorrecte.")
        return True

    def _check_names(self) -> bool:
        if not (self.first_name and self.last_name):
            raise ValueError("Le prénom et le nom de famille ne doivent pas êtres vides")

        special_characters = string.digits + string.punctuation

        if any(
                character in special_characters
                for character in self.first_name + self.last_name
        ):
            raise ValueError(f"Nom invalide '{self.full_name}'")

        return True

    def delete(self) -> int:
        if not self._exists():
            raise ValueError(f"'{self.full_name}' n'est pas dans la base de donnée")

        with OpenSqlite3db(User.DB) as (conn, cursor):
            cursor.execute("""
                DELETE FROM people
                WHERE ROWID == :instance_number
                """,
                           {
                               "instance_number": (instance_number := self._rowid())
                           })

        return instance_number

    def _exists(self) -> bool:
        return bool(self.db_info(False))

    def _rowid(self):
        if self._exists():
            with OpenSqlite3db(User.DB) as (conn, cursor):
                cursor.execute("""
                   SELECT ROWID
                   FROM people
                   WHERE 
                   first_name = :first_name
                   AND
                   last_name = :last_name
                   
               """,
                               self.__dict__)

                number = cursor.fetchone()[0]

            return number

    def save(self, check_data_valid: bool = False) -> int:
        if check_data_valid:
            self._check_all()

        if self._exists():
            raise OverflowError(f"L'utilisateur '{self.full_name}' est déjà dans la liste")

        with OpenSqlite3db(User.DB) as (conn, cursor):
            cursor.execute("""
            INSERT INTO people 
            VALUES (:first_name, :last_name, :full_name, :phone_number, :address)
            """,
                           self.__dict__)

        return self._rowid()


def get_all_users() -> list[User]:
    with OpenSqlite3db(User.DB) as (conn, cursor):
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM people
        """)
        all_users = [User(**i) for i in [dict(i) for i in cursor.fetchall()]]

    return all_users


if __name__ == "__main__":
    pass
    # fake_data = Faker(locale="fr_FR")
    # for _ in range(10):
    #     user_preset = {
    #         "first_name": fake_data.unique.first_name(),
    #         "last_name": fake_data.unique.last_name(),
    #         "phone_number": fake_data.unique.phone_number(),
    #         "address": fake_data.unique.address(),
    #     }
    #     print((user := User(**user_preset)))
    #     user.save()
    # user.delete()
    # print('-' * 100)
    # pprint(get_all_users())
    # laure = User("Laure", "Bourgeois")
    # print(laure._exists())
