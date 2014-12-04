from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys

class MyForm(QDialog):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        dialog_layout=QGridLayout()

        layout=QGridLayout()
        frame=QWidget()
        self.scroll_area=QScrollArea()
        frame.setLayout(layout)
    
        self.scroll_area.setWidget(frame)
        self.scroll_area.setWidgetResizable(True)
        for i in range(0,100):
            layout.addWidget(QLabel("YO"))  
            layout.addWidget(QLabel("SON"))

        dialog_layout.addWidget(self.scroll_area)
        self.setLayout(dialog_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
