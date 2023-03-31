import re
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QLineEdit
from Logger import Logger
from DatabaseMySQL import DatabaseMySQL
from PyQt5.QtCore import Qt
from models import postgresql_database, InternetStorePostgreSQL
from peewee import *


class DatabasePostgreSQL:
    def __init__(self, table_widget: QTableWidget, logger: Logger):
        #   Ініціалізація змінних
        self.tableWidget = table_widget
        self.editable = True
        self.column_names = self.fields = self.column_types = []
        self.table_columns = self.table_rows = 0
        self.logger = logger
        self.db = postgresql_database
        #   З'єднання з базою даних
        self.connect()
        self.cursor: Database | None = None
        #   Обробка зміни комірки в таблиці
        self.tableWidget.itemChanged.connect(self.update_field)

    def connect(self):
        """З'єднання з базою PostgreSQL"""
        try:
            self.db.connect()
            self.cursor = self.db.cursor()
            InternetStorePostgreSQL.create_table()
            self.logger.log(f"Successful connection to PostgreSQL database")
        except Exception as error:
            self.logger.error_message_box(f"Error trying to connect to PostgreSQL! {error}", should_abort=True)

    def init_table_widget_axis(self):
        """Ініціалізація назв комірок у таблиці"""
        try:
            self.column_names = InternetStorePostgreSQL.get_field_names()
            self.table_columns = len(self.column_names)
            self.tableWidget.setColumnCount(self.table_columns)
            self.tableWidget.setHorizontalHeaderLabels(self.column_names)
            self.fields = [field for field in InternetStorePostgreSQL.select().dicts()]
            self.table_rows = len(self.fields)
            self.tableWidget.setRowCount(self.table_rows)
            self.tableWidget.setVerticalHeaderLabels("" for _ in self.fields)
        except Exception as error:
            self.logger.error_message_box(f"PostgreSQL error connecting table! {error}")

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

    def migrate_from_mysql(self, mysql_db: DatabaseMySQL):
        """Міграція з MySQL"""

        def wrap_foo():
            try:
                #   Очистити таблицю перед міграцією
                self.db.drop_tables([InternetStorePostgreSQL])
                #   Створення порожньої таблиці
                self.db.create_tables([InternetStorePostgreSQL])
                for field in mysql_db.fields:
                    InternetStorePostgreSQL.create(**field)
                self.update_table_widget()
                self.logger.log("Successfully exported MySQL table data to PostgreSQL")
            except Exception as error:
                self.logger.error_message_box(f"Error trying to export to PostgreSQL! {error}", should_abort=True)

        return wrap_foo

    def update_field(self, item: QTableWidgetItem):
        """Оновлення значення в БД"""
        if not self.editable:
            return
        row, column = item.row(), item.column()
        field = self.column_names[column]
        field_id = self.fields[row].get("id")
        try:
            value = False if item.text().lower() == "false" else item.text()
            value = value if not value or not item.text().lower() == "none" else None
            query = InternetStorePostgreSQL.update(**{field: value}).where(InternetStorePostgreSQL.id == field_id)
            query.execute()
            self.logger.log(f"Updated PostgreSQL cell {field} with id {field_id}. New value is {value}")
        except Exception as error:
            self.logger.error_message_box(f"PostgreSQL error trying to update table item! {error}")
        self.update_table_widget()

    def export_to_sqlite(self, export_fields_lineedit: QLineEdit, db_sqlite):
        """Експорт в SQLite"""
        def wrap_foo():
            export_fields_text = export_fields_lineedit.text()
            export_fields = re.split(",\\s*|\\s+", export_fields_text)
            for export_field in export_fields:
                if export_field not in self.column_names:
                    self.logger.error_message_box(f"{export_field} is not a valid field name.\n"
                                                  f"Valid field names are: {self.column_names}")
                    return
            db_sqlite.migrate_from_postgresql(self, export_fields)

        return wrap_foo
