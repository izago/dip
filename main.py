import sys
import config

from controllers import institutecontroller as ic
from controllers import disciplinecontroller as dc
from controllers import positioncontroller as pc
from controllers import typecontroller as tc

from check_db import *

import calc

import dbconnection as DB

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidget, QComboBox, QTextEdit, QMessageBox, QFileDialog, \
    QPushButton
from PyQt5.uic import loadUi


class MainWindow(QDialog, QTextEdit):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("enter1.ui", self)

        self.pushButton.clicked.connect(self.Auth)
        self.pushButton_2.clicked.connect(self.gotoRegistration)
        self.base_line_edit = [self.login, self.password]

        self.check_db = CheckThread()
        self.check_db.mysignal.connect(self.signal_handler)

    def check_input(funct):
        def wrapper(self):
            for line_edit in self.base_line_edit:
                if len(line_edit.text()) == 0:
                    msg = QMessageBox()
                    msg.setWindowTitle("Ошибка")
                    msg.setText("Заполните все поля")
                    msg.setIcon(QMessageBox.Warning)
                    msg.exec_()
                    return
            funct(self)

        return wrapper

    @check_input
    def Auth(self):
        config.log = self.login.text()
        config.passw = self.password.text()

        isaut = self.check_db.thr_login(config.log, config.passw)

        if isaut:
            base = Base()
            widget.addWidget(base)
            widget.setCurrentIndex(widget.currentIndex() + 2)

            conn = DB.dbconnection.getconn()
            cursor = conn.cursor()

            cursor.execute(f"UPDATE USERS SET ch = 1 WHERE login='{config.log}'")
            conn.commit()

        else:
            mainwindow = MainWindow()
            widget.addWidget(mainwindow)
            widget.setCurrentIndex(widget.currentIndex())

    def signal_handler(self, value):
        QtWidgets.QMessageBox.about(self, 'Оповещение', value)

    def gotoRegistration(self):
        registr = Registration()
        widget.addWidget(registr)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class Registration(QDialog, QTextEdit, QComboBox):
    def __init__(self):
        super(Registration, self).__init__()
        loadUi("registr.ui", self)
        self.next_button.clicked.connect(self.reg)
        self.return_button.clicked.connect(self.gotoStart)
        self.initinst()
        self.initpos()

        self.base_line_edit = [self.login, self.oldpassword, self.surname, self.name, self.inst_box, self.possition_box]

        self.check_db = CheckThread()
        self.check_db.mysignal.connect(self.signal_handler)

        self.inst_box.currentIndexChanged.connect(self.instselected)
        self.possition_box.currentIndexChanged.connect(self.posselected)

    def instselected(self):
        cbinstindex = self.inst_box.currentIndex()
        inst_selected = listofinstitutetype[cbinstindex]
        sel = inst_selected.getInstID()
        return sel

    def posselected(self):
        cbposindex = self.possition_box.currentIndex()
        pos_selected = listofpositiontype[cbposindex]
        sel2 = pos_selected.getPosID()
        return sel2

    def signal_handler(self, value):
        QtWidgets.QMessageBox.about(self, 'Оповещение', value)

    def check_input(funct):
        def wrapper(self):
            for line_edit in self.base_line_edit:
                try:
                    text = line_edit.text()
                    print('text', text)
                except:
                    try:
                        text = line_edit.currentText()
                        print('text2', text)
                    except Exception as e:
                        print('говноош', e)
                if len(text) == 0:
                    msg = QMessageBox()
                    msg.setWindowTitle("Ошибка")
                    msg.setText("Заполните обязательные поля")
                    msg.setIcon(QMessageBox.Warning)
                    msg.exec_()
                    return
            funct(self)
        return wrapper

    @check_input
    def reg(self):
        config.log_2 = self.login.text()
        config.passw_2 = self.oldpassword.text()
        config.sur = self.surname.text()
        config.na = self.name.text()
        config.pat = self.patronymic.text()
        config.id_ins = self.instselected()
        config.id_pos = self.posselected()
        print('reg', config.log_2, config.passw_2, config.sur, config.na, config.pat, config.id_ins, config.id_pos)
        isreg = self.check_db.thr_register(config.log_2, config.passw_2, config.sur, config.na, config.pat, config.id_ins, config.id_pos)

        if isreg:
            base = Base()
            widget.addWidget(base)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            registr = Registration()
            widget.addWidget(registr)
            widget.setCurrentIndex(widget.currentIndex())

    def initinst(self):
        global listofinstitutetype
        listofinstitutetype = ic.institutecontroller.gettypeinst()

        for x in listofinstitutetype:
            self.inst_box.addItem(x.getInstName())

    def initpos(self):
        global listofpositiontype
        listofpositiontype = pc.positioncontroller.gettypepos()

        for x in listofpositiontype:
            self.possition_box.addItem(x.getPosName())

    def gotoStart(self):
        mainwindow = MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex() - 1)


class Base(QDialog, QComboBox, QTableWidget, QPushButton):

    def __init__(self):
        super(Base, self).__init__()
        loadUi("base.ui", self)
        self.initdisc()
        self.initdoc()
        self.inittype()

        self.base_line_edit = [self.file, self.nametest, self.discipline_box, self.quantity,
                               self.time_box, self.maxscore, self.type_box]

        self.calculateButton.clicked.connect(self.read)
        self.chooseButton.clicked.connect(self.BF)

        self.check_db = CheckThread()
        self.check_db.mysignal.connect(self.signal_handler)
        
        self.tableWidget_2.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Название документа'))
        self.tableWidget_2.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Дата создания'))
        self.tableWidget_2.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem('Дисциплина'))

        self.discipline_box.currentIndexChanged.connect(self.discselected)
        self.type_box.currentIndexChanged.connect(self.typeselected)

    def discselected(self):
        cbdiscindex = self.discipline_box.currentIndex()
        dis_selected = listofdisciplinetype[cbdiscindex]
        sel_3 = dis_selected.getDiscID()
        return sel_3

    def typeselected(self):
        cbtypeindex = self.type_box.currentIndex()
        type_selected = listoftesttype[cbtypeindex]
        sel_4 = type_selected.getTypeID()
        return sel_4

    def BF(self):
        config.fname = QFileDialog.getOpenFileName(self, 'Open file', 'C\\Users\\', 'EXCEL files (*.xlsx)')
        self.file.setText(config.fname[0])

    def signal_handler(self, value):
        QtWidgets.QMessageBox.about(self, 'Оповещение', value)

    def check_input(funct):
        def wrapper(self):
            for line_edit in self.base_line_edit:
                try:
                    text = line_edit.toPlainText()
                except:
                    try:
                        text = line_edit.currentText()
                    except Exception as e:
                        print('говноош', e)
                if len(text) == 0:
                    msg = QMessageBox()
                    msg.setWindowTitle("Ошибка")
                    msg.setText("Заполните обязательные поля")
                    msg.setIcon(QMessageBox.Warning)
                    msg.exec_()
                    return
            funct(self)
        return wrapper

    @check_input
    def read(self):
        try:
            config.file = self.file.toPlainText()
            config.name_t = self.nametest.toPlainText()
            config.disc = self.discselected()
            config.qua = self.quantity.toPlainText()
            config.time = self.time_box.toPlainText()
            config.max_s = self.maxscore.toPlainText()
            config.t_t = self.typeselected()
            is_read = self.check_db.thr_read(config.file, config.name_t, config.disc, config.qua, config.time, config.max_s, config.t_t)

            if is_read:
                print('config.time, config.qua, config.t_t, config.fname[0])', int(config.time), int(config.qua),
                      int(config.t_t), config.fname[0])
                try:
                    calc.calc_func(config.time, config.qua, config.t_t, config.fname[0])
                except Exception as e:
                    print('обраб', e)

                loadfiletodb(config.fname[0])

        except Exception as e:
            print('read', e)

    def initdoc(self):

        conn = DB.dbconnection.getconn()
        cursor = conn.cursor()
        cursor.execute('SELECT d.test_name, d.date_of_creation, di.name_discipline from DOCUMENTS d left join DISCIPLINE di  on d.ID_DISCIPLINE = di.ID_DISCIPLINE')

        self.tableWidget_2.setRowCount(1)
        tablerow = 0
        for row in cursor.fetchall():
            self.tableWidget_2.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(row[0]))
            self.tableWidget_2.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(str(row[1])))
            self.tableWidget_2.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(row[2]))

    def inittype(self):
        global listoftesttype
        listoftesttype = tc.typecontroller.gettesttype()

        for x in listoftesttype:
            self.type_box.addItem(x.getTypeName())

    def initdisc(self):
        global listofdisciplinetype
        listofdisciplinetype = dc.disciplinecontroller.gettypedisc()

        for x in listofdisciplinetype:
            self.discipline_box.addItem(x.getDiscName())


def loadfiletodb(file):
    import os
    import uuid
    filedbpath = "D:/FILEFOLDER"
    file_type = 'xlsx'
    uniq_name = uuid.uuid4()
    os.system(f'copy "{file}" "{filedbpath}/{uniq_name}.{file_type}"')

    fullname = str(uniq_name) + "." + file_type

    conn = DB.dbconnection.getconn()
    cursor = conn.cursor()
    print(file, fullname, config.name_t, config.qua, config.time, config.disc, config.t_t)

    try:
        cursor.execute(f"""Insert into DOCUMENTS (old_name, new_name, test_name, date_of_creation, num_question, time, 
        ID_DISCIPLINE, ID_USER, ID_TYPE_TEST) 
        VALUES ('{file}', '{fullname}', '{config.name_t}', (select convert(date, getdate())), {config.qua}, {config.time}, 
        {config.disc}, (select ID_USER from USERS where login = '{config.log}') , {config.t_t} )""")
        conn.commit()
    except Exception as e:
        print('bd', e)

    cursor.close()
    conn.close()


app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
mainwindow = MainWindow()
base = Base()
registr = Registration()
widget.setFixedWidth(700)
widget.setFixedHeight(500)

widget.addWidget(mainwindow)
widget.addWidget(registr)
widget.addWidget(base)

widget.show()

try:
    sys.exit(app.exec_())
except:

    conn = DB.dbconnection.getconn()
    cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE USERS SET ch = 0 WHERE login='{config.log}'")
        print(config.log)
        conn.commit()
    except Exception as e:
        print('ex', e)

    print("some")
