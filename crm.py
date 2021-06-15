import re
import sqlite3
import string
from pathlib import Path

import jwt
from faker import Faker
from sqlite3cm import OpenSqlite3db


class User:
    DB = Path(__file__).parent.resolve() / "database.db"

    def __init__(self, first_name: str, last_name: str, phone_number: str = "", address: str = "",
                 **trash_args):
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = f"{self.first_name} {self.last_name}"
        self.phone_number = phone_number
        self.address = address
        self.token = jwt.encode(self.__dict__, "secret")

    def __repr__(self):
        return f"User({self.full_name})"

    def __str__(self):
        return f"""
        La personne s'appele {self.full_name},
        son numéro de telephone est {self.phone_number}
        est son addresse est {self.address}.
        """

    @property
    def db_info(self):
        User._init_db()

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

        if info is not None:
            info = dict(info)

        return info

    @staticmethod
    def _init_db():
        with OpenSqlite3db(User.DB) as (conn, cursor):
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS people
                (
                    first_name text,
                    last_name text,
                    full_name text,
                    phone_number text,
                    address text,
                    token text
                )
                """)

    def _check_all(self):
        self._check_phone_number()
        self._check_names()

    def _check_phone_number(self):
        ok_number = re.sub(r"[+()\s]*", "", self.phone_number)
        if len(ok_number) < 10 or not ok_number.isdigit():
            raise ValueError(f"Le nombre '{self.phone_number}' est incorrecte.")

    def _check_names(self):
        if not (self.first_name and self.last_name):
            raise ValueError("Le prénom et le nom de famille ne doivent pas êtres vides")

        special_characters = string.digits + string.punctuation

        if any(
                character in special_characters
                for character in self.first_name + self.last_name
        ):
            raise ValueError(f"Nom invalide '{self.full_name}'")

    def delete(self):
        all_info = self.db_info

        if not all_info:
            raise ValueError(f"'{self.full_name}' n'est pas dans la base de donnée")

        User._init_db()

        with OpenSqlite3db(User.DB) as (conn, cursor):
            cursor.execute("""
                DELETE FROM people
                WHERE token = :instance_token
                """,
                           {
                               "instance_token": all_info.get("token", "")
                           })

    def exists(self) -> bool:
        return bool(self.db_info)

    def save(self, validate: bool = False):
        if validate:
            self._check_all()

        User._init_db()

        with OpenSqlite3db(User.DB) as (conn, cursor):
            cursor.execute("""
            SELECT token FROM people
            WHERE token == :instance_token
            """,
                           {
                               "instance_token": self.token
                           })

            if cursor.fetchone() is not None:
                raise OverflowError(f"L'utilisateur '{self.full_name}' est déjà dans la liste")

            cursor.execute("""
            INSERT INTO people 
            VALUES (:first_name, :last_name, :full_name, :phone_number, :address, :token)
            """,
                           self.__dict__)


def get_all_users():
    User._init_db()

    with OpenSqlite3db(User.DB) as (conn, cursor):
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM people
        """)
        all_users = [User(**i) for i in [dict(i) for i in cursor.fetchall()]]

    return all_users


if __name__ == "__main__":
    fake_data = Faker(locale="fr_FR")
    # for _ in range(10):
    #     user_preset = {
    #         "first_name": fake_data.unique.first_name(),
    #         "last_name": fake_data.unique.last_name(),
    #         "phone_number": fake_data.unique.phone_number(),
    #         "address": fake_data.unique.address(),
    #     }
    #     pprint((user := User(**user_preset)))
    #     user.save()
    #     print('-' * 100)
    # pprint(get_all_users())
    laure = User("Laure", "Bourgeois")
    print(laure.exists())
