from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt

from DatabasePostgreSQL import DatabasePostgreSQL
from Logger import Logger
from models import sqlite_database, create_sqlite_model
from peewee import *


class DatabaseSQLite:
    def __init__(self, table_widget: QTableWidget, logger: Logger):
        #   Ініціалізація змінних
        self.tableWidget = table_widget
        self.editable = True
        self.export_indexes = self.column_names = self.fields = []
        self.table_columns = self.table_rows = 0
        self.logger = logger
        self.db = sqlite_database
        self.cursor: Database | None = None
        self.InternetStoreSQLite = None
        #   З'єднання з базою даних
        self.connect()

    def connect(self):
        """З'єднання з базою SQLite"""
        try:
            self.db.connect()
            self.cursor = self.db.cursor()
            self.logger.log(f"Successful connection to SQLite database")
        except Exception as error:
            self.logger.error_message_box(f"Error connecting to SQLite database! {error}")

    def init_table_widget_axis(self):
        """Ініціалізація назв комірок у таблиці"""
        try:
            self.column_names = self.InternetStoreSQLite.get_field_names()
            self.tableWidget.setColumnCount(len(self.column_names))
            self.tableWidget.setHorizontalHeaderLabels(self.column_names)
            self.table_columns = len(self.column_names)
            self.tableWidget.setColumnCount(self.table_columns)
            self.fields = [field for field in self.InternetStoreSQLite.select().dicts()]
            self.table_rows = len(self.fields)
            self.tableWidget.setRowCount(self.table_rows)
            self.tableWidget.setVerticalHeaderLabels("" for _ in self.fields)

        except Exception as error:
            self.logger.error_message_box(f"SQLite error connecting table! {error}")

    def init_table_widget_fields(self):
        """Заповнення таблиці значеннями"""
        for i, field in enumerate(self.fields):
            for j, value in enumerate(field):
                table_widget_item = QTableWidgetItem(str(field.get(value)))
                table_widget_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.tableWidget.setItem(i, j, table_widget_item)

    def update_table_widget(self):
        """Оновити PyQt віджет для зображення бази даних"""
        try:
            self.editable = False
            self.init_table_widget_axis()
            self.init_table_widget_fields()
            self.editable = True
        except Exception as error:
            self.logger.error_message_box(f"PostgreSQL error trying to update table! {error}")

    def migrate_from_postgresql(self, db_postgresql: DatabasePostgreSQL, export_fields: [str]):
        """Міграція з PostgreSQL"""

        self.InternetStoreSQLite = create_sqlite_model(export_fields)
        try:
            #   Очищення таблиці перед міграцією
            self.db.drop_tables([self.InternetStoreSQLite])
            #   Створення порожньої таблиці з необхідними полями
            self.db.create_tables([self.InternetStoreSQLite])

            fields = []

            for field in db_postgresql.fields:
                custom_field = field.copy()
                for key, value in field.items():
                    if key not in export_fields:
                        custom_field.pop(key)
                fields.append(custom_field)

            for field in fields:
                self.InternetStoreSQLite.create(**field)

            self.update_table_widget()
            self.logger.log(f"Successfully migrated fields {export_fields} to SQLite")
        except Exception as error:
            self.logger.error_message_box(f"Error migrating to SQLite database! {error}")
