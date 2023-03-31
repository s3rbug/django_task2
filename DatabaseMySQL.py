from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt

from Logger import Logger

from peewee import *
from models import my_sql_database, InternetStoreMySQL


class DatabaseMySQL:
    def __init__(self, table_widget: QTableWidget, logger: Logger):
        #   Ініціалізація змінних
        self.fields = self.column_names = []
        self.table_rows = self.table_columns = 0
        self.editable = True
        self.tableWidget = table_widget
        self.logger = logger
        self.db = my_sql_database
        self.cursor: Database | None = None
        #   З'єднання з базою даних
        self.connect()
        self.update_table_widget()
        #   Обробка зміни комірки в таблиці
        self.tableWidget.itemChanged.connect(self.update_field)

    def __del__(self):
        """Закриття з'єднання"""
        self.cursor.close()
        self.db.close()

    def connect(self):
        """З'єднання з базою MySQL"""
        try:
            self.db.connect()
            self.cursor = self.db.cursor()
            InternetStoreMySQL.create_table()
            self.logger.log(f"Successful connection to MySQL database")
        except Exception as error:
            self.logger.error_message_box(f"MySQL connection error! {error}", should_abort=True)

    def init_table_widget_axis(self):
        """Ініціалізація назв комірок у таблиці"""
        try:
            self.column_names = InternetStoreMySQL.get_field_names()
            self.table_columns = len(self.column_names)
            self.tableWidget.setColumnCount(self.table_columns + 1)
            header_labels = self.column_names.copy()
            header_labels.append("")
            self.tableWidget.setHorizontalHeaderLabels(header_labels)
            self.fields = [field for field in InternetStoreMySQL.select().dicts()]
            self.table_rows = len(self.fields)
            self.tableWidget.setRowCount(self.table_rows + 1)
            vertical_labels = ["" for _ in self.fields]
            vertical_labels.append("New item:")
            self.tableWidget.setVerticalHeaderLabels(vertical_labels)
        except Exception as error:
            self.logger.error_message_box(f"MySQL error connecting table! {error}")

    def init_table_widget_fields(self):
        """Заповнення таблиці значеннями"""
        for i, field in enumerate(self.fields):
            for j, value in enumerate(field):
                table_widget_item = QTableWidgetItem(str(field.get(value)))
                table_widget_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.tableWidget.setItem(i, j, table_widget_item)
            delete_button = QPushButton("Delete item")
            delete_button.clicked.connect(self.delete_field(field.get("id")))
            self.tableWidget.setCellWidget(i, len(field), delete_button)

    def init_table_widget_create_item(self):
        """Створення додаткових кнопок в таблиці"""
        add_button = QPushButton("Create item")
        add_button.clicked.connect(self.create_field)
        self.tableWidget.setCellWidget(self.table_rows, self.table_columns, add_button)
        for i in range(self.table_columns):
            table_widget_item = QTableWidgetItem("")
            table_widget_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(self.table_rows, i, table_widget_item)

    def update_table_widget(self):
        """Оновити PyQt віджет для зображення бази даних"""
        try:
            self.editable = False
            self.init_table_widget_axis()
            self.init_table_widget_fields()
            self.init_table_widget_create_item()
            self.editable = True
        except Exception as error:
            self.logger.error_message_box(f"MySQL error trying to update table! {error}")

    def delete_field(self, field_id):
        """Видалення значення по id"""

        def wrap_foo():
            try:
                InternetStoreMySQL.delete_instance(InternetStoreMySQL.get(InternetStoreMySQL.id == field_id))
                self.update_table_widget()
            except Exception as error:
                self.logger.error_message_box(f"MySQL error trying to delete table item! {error}")

        return wrap_foo

    def create_field(self):
        """Створення нового елемента в БД"""
        new_field_widgets = [self.tableWidget.item(self.table_rows, i) for i in range(self.table_columns)]
        new_field_items = [
            field_widget.text()
            if field_widget
            else ""
            for field_widget in new_field_widgets
        ]

        new_field_items = [item if item.lower() != "false" else False for item in new_field_items]

        values = dict(zip(self.column_names, new_field_items))

        try:
            InternetStoreMySQL.create(**values)
            self.update_table_widget()
        except Exception as error:
            self.logger.error_message_box(f"MySQL error trying to add table item! {error}")

    def update_field(self, item: QTableWidgetItem):
        """Оновлення значення в БД"""
        if not self.editable:
            return
        row, column = item.row(), item.column()
        #   Перевірка, чи змінена комірка частина БД
        if row == self.table_rows or column == self.table_columns:
            return
        field = self.column_names[column]
        field_id = self.fields[row].get("id")
        try:
            value = item.text() if not item.text().lower() == "false" else False
            query = InternetStoreMySQL.update(**{field: value}).where(InternetStoreMySQL.id == field_id)
            query.execute()
            self.update_table_widget()
        except Exception as error:
            self.logger.error_message_box(f"MySQL error trying to update table item! {error}")
