from peewee import *
from config import MYSQL

my_sql_database = MySQLDatabase(
    host=MYSQL["host"],
    user=MYSQL["user"],
    password=MYSQL["password"],
    database=MYSQL["database"],
)


class InternetStore(Model):
    id = AutoField()
    price = IntegerField()
    count = IntegerField()
    rating = FloatField()
    program_name = TextField()
    program_description = TextField()
    license_expire_year = IntegerField()
    is_unlimited_license = BooleanField()

    @classmethod
    def get_field_names(cls):
        return [field.name for field in cls._meta.sorted_fields]


class InternetStoreMySQL(InternetStore):
    class Meta:
        database = my_sql_database
        table_name = "internet_store_licenses"
