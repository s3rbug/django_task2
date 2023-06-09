from PyQt5 import QtWidgets, uic

from DatabaseMySQL import DatabaseMySQL
from DatabasePostgreSQL import DatabasePostgreSQL
from DatabaseSQLite import DatabaseSQLite
from Logger import Logger


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        #   Завантаження файлу інтерфейсу
        uic.loadUi('MainWindowForm.ui', self)
        self.setWindowTitle("Лабораторна робота №2")
        self.logger = Logger(self.label_log)
        #   Створення баз даних
        self.dbMySql = DatabaseMySQL(
            table_widget=self.mysql_table,
            logger=self.logger
        )
        self.dbPostgreSQL = DatabasePostgreSQL(
            table_widget=self.postgresql_table,
            logger=self.logger
        )
        self.dbSQLite = DatabaseSQLite(
            table_widget=self.sqlite_table,
            logger=self.logger
        )
        #   З'єднання кнопок з UI та відповідних функцій
        self.export_to_postgres_button.clicked.connect(
            self.dbPostgreSQL.migrate_from_mysql(self.dbMySql)
        )
        self.export_fields_button.clicked.connect(
            self.dbPostgreSQL.export_to_sqlite(self.export_fields_lineedit, self.dbSQLite)
        )
        self.show()
