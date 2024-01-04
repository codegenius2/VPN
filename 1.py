import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QStyleFactory
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Theme Example')
        self.setGeometry(100, 100, 300, 200)

        # Create a combo box for theme selection
        self.combo = QComboBox(self)
        self.combo.addItem('Fusion')
        self.combo.addItem('Windows')
        self.combo.addItem('WindowsVista')
        self.combo.addItem('Macintosh')
        self.combo.addItem('Breeze')
        self.combo.currentIndexChanged.connect(self.changeTheme)
        self.combo.setGeometry(50, 50, 200, 30)

    def changeTheme(self):
        theme = self.combo.currentText()

        # Set the application style
        QApplication.setStyle(QStyleFactory.create(theme))

        # Update palette for consistent colors
        palette = QPalette()
        if theme == 'Fusion':
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(15, 15, 15))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        else:
            palette = QApplication.palette()
        QApplication.setPalette(palette)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())