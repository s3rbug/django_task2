from peewee import *
from config import MYSQL, POSTGRESQL, SQLITE

TABLE_NAME = "internet_store_licenses"

my_sql_database = MySQLDatabase(
    host=MYSQL["host"],
    user=MYSQL["user"],
    password=MYSQL["password"],
    database=MYSQL["database"],
)

postgresql_database = PostgresqlDatabase(
    host=POSTGRESQL["host"],
    user=POSTGRESQL["user"],
    password=POSTGRESQL["password"],
    database=POSTGRESQL["database"],
    autorollback=True
)

sqlite_database = SqliteDatabase(SQLITE["filename"])


class ImprovedModel(Model):
    @classmethod
    def get_field_names(cls):
        return [field_item.name for field_item in cls._meta.sorted_fields]


class InternetStore(ImprovedModel):
    id = AutoField()
    price = IntegerField()
    count = IntegerField()
    rating = FloatField()
    program_name = TextField()
    program_description = TextField()
    license_expire_year = IntegerField(null=True)
    is_unlimited_license = BooleanField()


class InternetStoreMySQL(InternetStore):
    class Meta:
        database = my_sql_database
        table_name = TABLE_NAME


class InternetStorePostgreSQL(InternetStore):
    class Meta:
        database = postgresql_database
        table_name = TABLE_NAME


def create_sqlite_model(fields: [str]):
    class InternetStoreSQLite(ImprovedModel):
        class Meta:
            database = sqlite_database
            table_name = TABLE_NAME

    for field_name in fields:
        field = getattr(InternetStore, field_name)
        getattr(InternetStoreSQLite, '_meta').add_field(field_name, field)

    return InternetStoreSQLite
