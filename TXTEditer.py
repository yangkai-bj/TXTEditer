import sys
import os
import getopt
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication,QLineEdit
from PyQt5.QtWidgets import QFileDialog, QFontDialog, QColorDialog
from PyQt5.QtWidgets import QMessageBox,QDialog, QPushButton
from PyQt5.QtWidgets import QGridLayout, QComboBox, QLabel
from PyQt5.QtGui import QIcon, QFont, QTextDocument
from PyQt5.QtCore import QDir, Qt


class ReplaceDialog(QDialog):
    __source__ = None
    __target__ = None
    __ok__ = False

    def __init__(self, parent=None, source=None):
        super(ReplaceDialog, self).__init__(parent)
        if source is not None:
            self.__source__ = source
        self.setWindowTitle('替换')
        self.resize(210, 90)
        grid = QGridLayout()
        grid.setSpacing(10)
        self.label1 = QLabel('原字符:')
        grid.addWidget(self.label1, 1, 0)
        self.sourceLineEdit = QLineEdit()
        self.sourceLineEdit.textChanged.connect(self.change)
        grid.addWidget(self.sourceLineEdit, 1, 1, 1, 2)
        self.label2 = QLabel('替换为:')
        grid.addWidget(self.label2, 2, 0)
        self.targetLineEdit = QLineEdit()
        self.targetLineEdit.textChanged.connect(self.change)
        grid.addWidget(self.targetLineEdit, 2, 1, 1, 2)
        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('确定')
        grid.addWidget(self.btn_ok, 3, 1)
        self.btn_ok.clicked.connect(self.accept)

        self.btn_cancel = QPushButton(self)
        self.btn_cancel.setText('取消')
        grid.addWidget(self.btn_cancel, 3, 2)
        self.btn_cancel.clicked.connect(self.reject)

        self.setLayout(grid)
        self.setWindowModality(Qt.WindowModal)
        self.exec_()

    def change(self):
        self.__source__ = self.sourceLineEdit.text()
        self.__target__ = self.targetLineEdit.text()
        self.__ok__ = True

    def getReplace(self):
        return self.__source__, self.__target__, self.__ok__


class CharsetDialog(QDialog):
    __charset__ = None
    __ok__ = False

    def __init__(self, parent=None, charset=None):
        super(CharsetDialog, self).__init__(parent)
        if charset is not None:
            self.__charset__ = charset
        self.setWindowTitle('编码')
        self.resize(210, 90)
        grid = QGridLayout()
        grid.setSpacing(10)

        self.btn1 = QLabel('字符集:')
        grid.addWidget(self.btn1, 1, 0)

        self.cb = QComboBox()
        self.cb.addItem(sys.getfilesystemencoding().upper(), sys.getfilesystemencoding().upper())
        self.cb.addItem('GBK', 'GBK')
        self.cb.addItem('UTF-8', 'UTF-8')
        if self.__charset__ is not None:
            self.cb.setCurrentText(self.__charset__.upper())
        self.cb.currentIndexChanged.connect(self.selectionchange)
        grid.addWidget(self.cb, 1, 1, 1, 2)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('确定')
        grid.addWidget(self.btn_ok, 2, 1)
        self.btn_ok.clicked.connect(self.accept)

        self.btn_cancel = QPushButton(self)
        self.btn_cancel.setText('取消')
        grid.addWidget(self.btn_cancel, 2, 2)
        self.btn_cancel.clicked.connect(self.reject)

        self.setLayout(grid)
        self.setWindowModality(Qt.WindowModal)
        self.exec_()

    def selectionchange(self):
        self.__charset__ = self.cb.currentText()
        self.__ok__ = True

    def getCharset(self):
        return self.__charset__, self.__ok__

class SQLEditer(QMainWindow):
    __sql_key__ = {'keywords': ['SELECT', 'UPDATE', 'INSERT', 'DELETE', 'DROP', 'CREATE', 'TABLE', 'INDEX',
                                'DATABASE', 'DECLARE', 'ALTER', 'FROM', 'ORDER', 'GROUP', 'BY', 'NOT', 'NULL',
                                'CHARSET', 'LEFT', 'RIGHT', 'OUTER', 'JOIN', 'WHERE', 'AND ', 'OR', 'CASE',
                                'DEFAULT', 'LIMIT', 'ADD', 'COLUMN', 'SET', 'ON', 'UNION', 'ENGINE', 'WHEN',
                                'THEN', 'END', 'ELSE', 'IN', 'DESC', 'ASC', 'ALL', 'AS', 'CHARSET', 'ENGINE',
                                'COLLATE'],
                   'format': '<font color=#CC7832>{0}</font>'}
    __sql_fun__ = {'keywords': ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'ROUND', 'DATE_FORMAT', 'STRFTIME',
                                'REPLACE', 'ABS'],
                   'format': '<font color=#9876AA>{0}</font>'}

    __sql_unit__ = {'keywords': ['INT', 'DECIMAL', 'CHAR', 'VARCHAR', 'DATE', 'NVARCHAR'],
                    'format': '<font color=#9876AA>{0}</font>'}

    __sql_oper__ = {'keywords': ['+', '-', '*', '&gt;', '&lt;', '&lt;&gt;'],
                    'format': '<font color=brown>{0}</font>'}

    __param__ = {'keywords': ['TITLE', 'MODE', 'TYPE', 'CHART', 'STYLE', 'THEME', 'WIDTH','HEIGHT', 'DATAZOOM',
                              'DATAZOOM-TYPE', 'MARK-POINT', 'MARK-LINE', 'PARAM'],
                 'format': '<font color=#008D67>{0}</font>'}

    __c_key__ = {'keywords': ['AUTO', ' BREAK', 'CASE', 'CHAR', 'CONST', 'CONTINUE', 'DEFAULT', 'DO', 'DOUBLE',
                              'ELSE', 'ENUM', 'EXTERN', 'FLOAT', 'FOR', 'GOTO', 'IF', 'INT', 'INCLUDE', 'LONG', 'REGISTER',
                              'RETURN', 'SHORT', 'SIGNED', 'SIZEOF', 'STATIC', 'STRUCT', 'SWITCH', 'TYPEDEF', 'UNION',
                              'UNSIGNED', 'VOID', 'VOLATILE', 'WHILE', 'PRINTF', 'SCANF', 'STRCMP', 'TOUPPER', 'TOLOWER'],
                 'format': '<font color=#CC7832>{0}</font>'}

    __default_file__ = None
    __setting__ = {"runpath": os.path.abspath(os.path.split(sys.argv[0])[0]),
                   'path': os.getcwd(),
                   'encoding': sys.getfilesystemencoding(),
                   'font': QFont('Verdana', 12, QFont.Normal),
                   'Background': '#383838',
                   'Color': 'cyan'}
    #'Color': '#a6a6a6'
    textEdit = None
    LABEL_ENCODING = None

    def __init__(self, file=None, encoding=None):
        super().__init__()
        if encoding is not None:
            self.__setting__['encoding'] = encoding
        if file is not None:
            self.__default_file__ = file
            self.setWindowTitle('SQL Editer  [ {0} ]'.format(os.path.split(self.__default_file__)[1]))
        else:
            self.setWindowTitle('SQL Editer')

        self.initUI()

    def initUI(self):

        self.textEdit = QTextEdit()
        self.textEdit.setFont(self.__setting__['font'])
        self.textEdit.setStyleSheet(
            'background:{0};color:{1}'.format(self.__setting__['Background'], self.__setting__['Color']))
        self.textEdit.textChanged.connect(self.txtChanged)
        self.setCentralWidget(self.textEdit)

        images_path = '{0}{1}{2}{3}'.format(self.__setting__['runpath'], os.path.sep, 'images', os.path.sep)
        newFileAcction = QAction(QIcon('{0}{1}'.format(images_path, 'new.png')), '新建', self)
        newFileAcction.setShortcut('Ctrl+N')
        newFileAcction.setStatusTip('新建')
        newFileAcction.triggered.connect(self.newFile)

        openFileAcction = QAction(QIcon('{0}{1}'.format(images_path, 'open.png')), '打开', self)
        openFileAcction.setShortcut('Ctrl+O')
        openFileAcction.setStatusTip('打开')
        openFileAcction.triggered.connect(self.openFiles)

        saveFileAcction = QAction(QIcon('{0}{1}'.format(images_path, 'save.png')), '保存', self)
        saveFileAcction.setShortcut('Ctrl+S')
        saveFileAcction.setStatusTip('保存')
        saveFileAcction.triggered.connect(self.saveFile)

        saveAsAcction = QAction(QIcon('{0}{1}'.format(images_path, 'saveas.png')), '另存为', self)
        #saveAsAcction.setShortcut('Ctrl+O')
        saveAsAcction.setStatusTip('另存为')
        saveAsAcction.triggered.connect(self.saveAs)

        aboutAcction = QAction(QIcon('{0}{1}'.format(images_path, 'about.png')), '关于', self)
        aboutAcction.setShortcut('Ctrl+A')
        aboutAcction.setStatusTip('关于')
        aboutAcction.triggered.connect(self.about)

        setFontAcction = QAction(QIcon('{0}{1}'.format(images_path, 'font.png')), '字体', self)
        setFontAcction.setShortcut('Ctrl+F')
        setFontAcction.setStatusTip('设置字体')
        setFontAcction.triggered.connect(self.setFont)

        setBackgroundColorAcction = QAction(QIcon('{0}{1}'.format(images_path, 'background.png')), '背景', self)
        setBackgroundColorAcction.setShortcut('Ctrl+B')
        setBackgroundColorAcction.setStatusTip('设置背景颜色')
        setBackgroundColorAcction.triggered.connect(self.setBackgroundColor)

        setColorAcction = QAction(QIcon('{0}{1}'.format(images_path, 'color.png')), '颜色', self)
        setColorAcction.setShortcut('Ctrl+C')
        setColorAcction.setStatusTip('设置字体颜色')
        setColorAcction.triggered.connect(self.setColor)

        setCharsetAcction = QAction(QIcon('{0}{1}'.format(images_path, 'charset.png')), '编码', self)
        setCharsetAcction.setShortcut('Ctrl+T')
        setCharsetAcction.setStatusTip('设置编码')
        setCharsetAcction.triggered.connect(self.setCharset)

        replaceAcction = QAction(QIcon('{0}{1}'.format(images_path, 'replace.png')), '查找替换', self)
        replaceAcction.setShortcut('Ctrl+T')
        replaceAcction.setStatusTip('查找替换')
        replaceAcction.triggered.connect(self.replace)


        exitAction = QAction(QIcon('{0}{1}'.format(images_path, 'exit.png')), '退出', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('退出')
        exitAction.triggered.connect(self.close)

        self.LABEL_ENCODING = QLabel(self.__setting__["encoding"].upper().ljust(15, " "))
        #self.statusBar()
        self.statusBar().addPermanentWidget(self.LABEL_ENCODING, stretch=0)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&文件')
        fileMenu.addAction(newFileAcction)
        fileMenu.addAction(openFileAcction)
        fileMenu.addAction(saveFileAcction)
        fileMenu.addAction(saveAsAcction)
        fileMenu.addAction(exitAction)

        setMenu = menubar.addMenu('&设置')
        setMenu.addAction(setBackgroundColorAcction)
        setMenu.addAction(setColorAcction)
        setMenu.addAction(setFontAcction)
        setMenu.addAction(setCharsetAcction)

        helpMenu = menubar.addMenu('&帮助')
        helpMenu.addAction(aboutAcction)

        filebar = self.addToolBar('文件')
        filebar.addAction(newFileAcction)
        filebar.addAction(openFileAcction)
        filebar.addAction(saveFileAcction)
        filebar.addAction(saveAsAcction)

        setbar = self.addToolBar('设置')
        setbar.addAction(replaceAcction)
        setbar.addAction(setBackgroundColorAcction)
        setbar.addAction(setColorAcction)
        setbar.addAction(setFontAcction)
        setbar.addAction(setCharsetAcction)

        self.setWindowIcon(QIcon('{0}{1}'.format(images_path, 'main.png')))
        self.setGeometry(300, 300, 1024, 650)
        self.show()

        if self.__default_file__ is not None:
            self.readFile(self.__default_file__, self.__setting__['encoding'])
        else:
            self.about()

    def replace(self):
        source, target, ok = ReplaceDialog(parent=self, source=None).getReplace()
        if ok:
            s = self.textEdit.toPlainText()
            s = s.replace(source, target)
            ok, txt = self.toHTML(s, type=os.path.splitext(self.__default_file__)[1])
            self.textEdit.setHtml(txt)

    def txtChanged(self):
        document = self.textEdit.document()
        cursor = self.textEdit.textCursor()
        #cursor.movePosition(QTextCursor.End)
        self.textEdit.setTextCursor(cursor)

    def about(self):
        QMessageBox.information(self, '关于',  '''<font size=18>TXT Editer</font><br><hr><br>
                                <font color=brown>欢迎使用.<br><br></font>
                                <pre><p>{0}杨凯<br>{1}yangkai.bj@ccb.com</p></pre>'''.format('&#9;'*4, '&#9;'*4), QMessageBox.Ok)

    def setCharset(self):
        charset, ok = CharsetDialog(parent=self, charset=self.__setting__['encoding']).getCharset()
        if ok:
            if self.__default_file__ is not None:
                self.readFile(self.__default_file__, charset)
            else:
                self.__setting__['encoding'] = charset
                self.LABEL_ENCODING.setText(self.__setting__["encoding"].upper().ljust(15, " "))

    def setColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.__setting__['Color'] = color.name()
            self.textEdit.setStyleSheet(
                'background:{0};color:{1}'.format(self.__setting__['Background'], self.__setting__['Color']))

    def setBackgroundColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.__setting__['Background'] = color.name()
            self.textEdit.setStyleSheet(
                'background:{0};color:{1}'.format(self.__setting__['Background'], self.__setting__['Color']))

    def setFont(self):
        font, ok = QFontDialog.getFont(self.__setting__['font'])
        if ok:
            self.__setting__['font'] = font
            self.textEdit.setFont(self.__setting__['font'])

    def newFile(self):
        self.__default_file__ = None
        self.textEdit.setPlainText('')
        self.setWindowTitle('TXT Editer')

    def readFile(self, file, encoding):
        try:
            ok = False
            data = ""
            try:
                if os.path.exists(file):
                    f = open(file, 'r', encoding=encoding)
                    while True:
                        d = f.readline()
                        if not d:
                            break
                        data += d
                    f.close()
                    ok = True
            except Exception as error:
                QMessageBox.warning(self, '文件读取失败', str(error), QMessageBox.Yes)
            if ok:
                self.__default_file__ = file
                self.__setting__['path'] = os.path.split(file)[0]
                self.__setting__['encoding'] = encoding
                self.LABEL_ENCODING.setText(self.__setting__["encoding"].upper().ljust(15, " "))
                self.setWindowTitle('TXT Editer  [ {0} ]'.format(os.path.split(file)[1]))
                try:
                    self.textEdit.clear()
                except Exception:
                    pass
                ok, txt = self.toHTML(data, type=os.path.splitext(file)[1])
                if ok:
                    self.textEdit.setHtml(txt)
                else:
                    self.textEdit.setPlainText(txt)
        except Exception as err:
            QMessageBox.warning(self, '读取文件失败', err, QMessageBox.Yes)

    def toHTML(self, data, type=None):
        ok = False
        try:
            print(data)
            # 首先置换&,<,>为HTML代字符,&最优先
            if type.upper() == '.SQL':
                data = data.replace('&', '&amp;').replace('>', '&gt;').replace('<', '&lt;').replace("\t", "&nbsp;"*8).replace(" "*8, "&nbsp;"*8)
                words = data
                signs = [' ', '[', ']', ':', '(', ')', '{', '}', "'", '"', '\n', '+', '=', '-', '*', '/', '^', '.']
                for sign in signs:
                    words = words.replace(sign, ',')
                words = list(set(words.split(",")))
                #去重
                print(words)
                for word in words:
                    if word.upper() in self.__sql_key__['keywords']:
                        data = data.replace(word, self.__sql_key__['format'].format(word))
                    if word.upper() in self.__sql_fun__['keywords']:
                        data = data.replace(word, self.__sql_fun__['format'].format(word))
                    if word.upper() in self.__sql_unit__['keywords']:
                        data = data.replace(word, self.__sql_unit__['format'].format(word))

                data = data.replace('\n', '<br>').replace('"', '&quot;')
                # 最后置换回车符和双引号
                ok = True
            elif type.upper() == '.PAR':
                data = data.replace('&', '&amp;').replace('>', '&gt;').replace('<', '&lt;').replace("\t", "&nbsp;"*8).replace(" "*8, "&nbsp;"*8)
                try:
                    words = str(eval(data))
                except Exception:
                    words = data
                signs = [' ', '[', ']', ':', '(', ')', '{', '}', "'", '"', '\n', '=', '+', '-', '*', '/', '^', '.']
                for sign in signs:
                    words = words.replace(sign, ',')
                words = list(set(words.split(",")))
                # 去重
                for word in words:
                    if word.upper() in self.__param__['keywords']:
                        data = data.replace(word, self.__param__['format'].format(word))
                    else:
                        for key in self.__param__['keywords']:
                            if word.upper().startswith(key):
                                data = data.replace(word, self.__param__['format'].format(word))
                                break

                data = data.replace('\n', '<br>').replace('"', '&quot;')
                #最后置换回车符和双引号
                ok = True
            elif type.upper() == '.C':
                data = data.replace('&', '&amp;').replace('>', '&gt;').replace('<', '&lt;').replace("\t", "&nbsp;"*8).replace(" "*8, "&nbsp;"*8)
                try:
                    words = str(eval(data))
                except Exception:
                    words = data
                signs = [' ', '[', ']', ':', '(', ')', '{', '}', "'", '"', '\n', '=', '+', '-', '*', '/', '^', '.', ';', '#']
                for sign in signs:
                    words = words.replace(sign, ',')
                words = list(set(words.split(",")))
                # 去重
                for word in words:
                    if word.upper() in self.__c_key__['keywords']:
                        data = data.replace(word, self.__c_key__['format'].format(word))
                    else:
                        for key in self.__c_key__['keywords']:
                            if word.upper().startswith(key):
                                data = data.replace(word, self.__c_key__['format'].format(word))
                                break

                data = data.replace('\n', '<br>').replace('"', '&quot;')
                #最后置换回车符和双引号
                ok = True
            print(data)
        except Exception as err:
            QMessageBox.warning(self, '数据转换失败', err, QMessageBox.Yes)
        finally:
            return ok, data

    def openFiles(self):
        dig = QFileDialog(self, '打开...', self.__setting__['path'], 'All file (*.*);;SQL file (*.sql);;Par file (*.par);;Txt file (*.txt);;Python file (*.py);;C code (*.c)')
        dig.setFileMode(QFileDialog.AnyFile)
        dig.setFilter(QDir.Files)
        if dig.exec_():
            filenames = dig.selectedFiles()
            self.readFile(filenames[0], self.__setting__['encoding'])

    def saveFile(self):
        try:
            if self.__default_file__ is None:
                filename, ok = QFileDialog.getSaveFileName(self, '保存...', self.__setting__['path'], 'All file (*.*);;SQL file (*.sql);;Par file (*.par);;Txt file (*.txt);;Python file (*.py);;C code (*.c)')
                if ok:
                    self.__default_file__ = filename
                    self.__setting__['path'] = os.path.split(self.__default_file__)[0]
                    self.setWindowTitle('SQL Editer  [ {0} ]'.format(os.path.split(self.__default_file__)[1]))
            with open(self.__default_file__, 'w', encoding=self.__setting__['encoding']) as f:
                f.write(self.textEdit.toPlainText())
            ok, txt = self.toHTML(self.textEdit.toPlainText(), type=os.path.splitext(self.__default_file__)[1])
            if ok:
                self.textEdit.setHtml(txt)
            else:
                self.textEdit.setPlainText(txt)
        except Exception as error:
            QMessageBox.warning(self, '文件保存失败', str(error), QMessageBox.Yes)

    def saveAs(self):
        try:
            if self.__default_file__ is not None:
                filename, ok = QFileDialog.getSaveFileName(self, '另存为...', self.__setting__['path'], 'All file (*.*);;SQL file (*.sql);;Par file (*.par);;Txt file (*.txt);;Python file (*.py);;C code (*.c)')
                if ok:
                    charset, ok = CharsetDialog(parent=self, charset=self.__setting__['encoding']).getCharset()
                    if ok:
                        with open(filename, 'w', encoding=charset) as f:
                            f.write(str(self.textEdit.toPlainText()))
                        self.__setting__['encoding'] = charset
                        self.LABEL_ENCODING.setText(self.__setting__["encoding"].upper().ljust(15, " "))
                    else:
                        with open(filename, 'w', encoding=self.__setting__['encoding']) as f:
                            f.write(str(self.textEdit.toPlainText()))
                    self.textEdit.setHtml(self.toHTML(self.textEdit.toPlainText(), type=os.path.splitext(self.__default_file__)[1]))
                    self.__default_file__ = filename
                    self.__setting__['path'] = os.path.split(self.__default_file__)[0]
                    self.setWindowTitle('SQL Editer  [ {0} ]'.format(os.path.split(self.__default_file__)[1]))
        except Exception as error:
            QMessageBox.warning(self, '文件另存失败', str(error), QMessageBox.Yes | QMessageBox.No)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    file = None
    encoding = None
    path = None
    try:
        options, args = getopt.getopt(sys.argv, 'HhF:f:E:e:', ['HELP', 'help', 'FILE=', 'file=', 'ENCODING=', 'encoding='])

        for option, value in options:
            if str(option).upper() in ('-H', '--HELP'):
                print('Usage:')
                print('\t-f <FILE> -e <Encoding>')
                print('\t--file=<File> --Encoding=<Encoding>')
                print('\t<File> <Encoding>')
                sys.exit()
            if str(option).upper() in ('-F', '--FILE'):
                file = value
            if str(option).upper() in ('-E', '--ENCODING'):
                port = value
        for index, arg in enumerate(args):
            if file is None and index == 1:
                file = arg
            if encoding is None and index == 2:
                encoding = arg
    except Exception:
        pass

    ex = SQLEditer(file=file, encoding=encoding)
    sys.exit(app.exec_())