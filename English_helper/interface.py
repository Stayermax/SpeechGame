import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QImage, QPalette, QBrush, QPixmap, QPainter, QIcon
from PyQt5 import QtWidgets
import time
from recognizer import recognizer
from winsound import *
import random
from names import *

class PicButton(QtWidgets.QAbstractButton):
    def __init__(self, pixmap, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap
        #self.objectNameChanged('lol')

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()

class Interface(QtWidgets.QWidget):
    def __init__(self):
        super(QtWidgets.QWidget, self).__init__()
        self.window = QtWidgets.QHBoxLayout()
        self.init_ui()
        self.time_for_action = time.time()

    def init_ui(self):
        self.MainMenuWindow()
        self.setLayout(self.window)
        self.show()

    def MainMenuWindowStyle(self):
        oImage = QImage("background/main_menu.jpg")
        sImage = oImage.scaled(QSize(500, 200), Qt.KeepAspectRatioByExpanding)  # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))  # 10 = Windowrole
        self.setPalette(palette)
        self.setWindowTitle("Sound recognition 1.0.0")
        self.setGeometry(800, 200, 350, 200)

    def AnimalsLoad(self):
        import os
        files_list = (os.listdir('pics/'))
        self.Animals = {}
        for i in range(len(files_list)):
            if(files_list[i] not in 'bad pics'):
                self.Animals[files_list[i]] = files_list[i].split('.')[0]

    def MakeTriplets(self):
        animals = dict(self.Animals)
        self.Triplets = []
        i = 0
        while (len(animals)):
            if(not i%3):
                self.Triplets.append([])
            a = random.choice(list(animals.items()))
            self.Triplets[int(i/3)].append(a)
            del animals[a[0]]
            i+=1

    def MakeOrder(self):
        import copy
        import random
        animals = dict(self.Animals)
        self.Order = []
        i = 0
        while (len(animals)):
            a = random.choice(list(animals.items()))
            self.Order.append(a)
            del animals[a[0]]
            i += 1
        print(self.Order)

    def GetTriplet(self):
        triplet = self.Triplets[0]
        del self.Triplets[0]
        return triplet

    def GetOne(self):
        if(len(self.Order[0])):
            one = self.Order[0]
            del self.Order[0]
            print(self.Order)
            print(one)
            return one
        else:
            return False



    def MainMenuWindow(self):
        self.clearLayout(self.window)
        self.MainMenuWindowStyle()
        self.AnimalsLoad()
        self.MakeOrder()
        col = QtWidgets.QVBoxLayout()

        ImageRec_btn = QtWidgets.QPushButton('  Photo recognition')
        ImageRec_btn.setIcon(QIcon('service\camera.ico'))
        ImageRec_btn.setIconSize(QSize(100, 100))
        ImageRec_btn.setStyleSheet("color: black; font: 18px")
        ImageRec_btn.clicked.connect(self.ImageRecognitionWindow)

        VoiceRec_btn = QtWidgets.QPushButton('  Voice recognition')
        VoiceRec_btn.setIcon(QIcon('service\micro.ico'))
        VoiceRec_btn.setIconSize(QSize(100, 100))
        VoiceRec_btn.setStyleSheet("color: black; font: 18px")
        VoiceRec_btn.clicked.connect(self.SoundRecognitionWindow)

        col.addWidget(ImageRec_btn)
        col.addWidget(VoiceRec_btn)

        self.window.addLayout(col)

    def SoundRecognitionWindowStyle(self):
        oImage = QImage("background/main_menu.jpg")
        sImage = oImage.scaled(QSize(1200, 600), Qt.KeepAspectRatioByExpanding)  # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))  # 10 = Windowrole
        self.setPalette(palette)
#        self.setWindowTitle("Sound re")
        self.setGeometry(800, 200, 600, 600)

    def SoundRecognitionWindow(self):           # One
        R_animal = self.GetOne()
        self.SoundRecognitionWindowStyle()
        self.clearLayout(self.window)
        col = QtWidgets.QVBoxLayout()
        image = QtWidgets.QLabel(R_animal[1], self)
        image.setAlignment(Qt.AlignCenter)
        image.setPixmap(QPixmap('pics\\' + R_animal[0]).scaled(600, 450))
        self.CurrImg = (R_animal[1].lower())
        print('image text', self.CurrImg)

        speak = PicButton(QPixmap('service\micro.ico'), self)
        speak.setText('speak')
        speak.clicked.connect(self.SoundAnalizer)

        l_1 = QtWidgets.QLabel(' ')
        col_1 = QtWidgets.QVBoxLayout()
        col_1.addWidget(l_1)
        l_2 = QtWidgets.QLabel(' ')
        col_2 = QtWidgets.QVBoxLayout()
        col_2.addWidget(l_2)
        speak_line = QtWidgets.QHBoxLayout()

        speak_line.addLayout(col_1)
        speak_line.addWidget(speak)
        speak_line.addLayout(col_2)

        col.addWidget(image)
        col.addLayout(speak_line)

        self.window.addLayout(col)

    def SoundAnalizer(self):
        """ 
        keywords = []
        for animal in self.Animals.values():
            keywords.append((animal.lower(), 1.0))
        """
        res = (recognizer()).lower()
        if(res in self.CurrImg or res == self.CurrImg):
            print('Right answer')
            if(len((self.Order))):
                self.SoundRecognitionWindow()
            else:
                PlaySound(YOUWON, SND_FILENAME)
                self.clearLayout(self.window)
                self.MainMenuWindowStyle()
                self.MainMenuWindow()
        else:
            print('Wrong answer, try again')

    def ImageRecognitionWindowStyle(self):

        oImage = QImage("background/main_menu.jpg")
        sImage = oImage.scaled(QSize(1200, 600), Qt.KeepAspectRatioByExpanding)  # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))  # 10 = Windowrole
        self.setPalette(palette)
        #        self.setWindowTitle("Sound re")
        self.setGeometry(300, 200, 600, 600)

    def ImageRecognitionWindow(self):       # THREE
        self.clearLayout(self.window)
        self.ImageRecognitionWindowStyle()
        self.MakeTriplets()

        col = QtWidgets.QVBoxLayout()

        talk = PicButton(QPixmap('service\micro.ico'), self)
        talk.setText('speak')

        l_1 = QtWidgets.QLabel(' ')
        col_1 = QtWidgets.QVBoxLayout()
        col_1.addWidget(l_1)

        l_2 = QtWidgets.QLabel(' ')
        col_2 = QtWidgets.QVBoxLayout()
        col_2.addWidget(l_2)

        l_3 = QtWidgets.QLabel(' ')
        col_3 = QtWidgets.QVBoxLayout()
        col_3.addWidget(l_3)

        l_4 = QtWidgets.QLabel(' ')
        col_4 = QtWidgets.QVBoxLayout()
        col_4.addWidget(l_4)

        talk_line = QtWidgets.QHBoxLayout()

        talk_line.addLayout(col_1)
        talk_line.addLayout(col_2)
        talk_line.addWidget(talk)
        talk_line.addLayout(col_3)
        talk_line.addLayout(col_4)

        options_line = QtWidgets.QHBoxLayout()

        R_animals = self.GetTriplet()
        an_1 = 'pics\\' + R_animals[0][0]
        an_2 = 'pics\\' + R_animals[1][0]
        an_3 = 'pics\\' + R_animals[2][0]

        var_1 = PicButton(QPixmap(an_1).scaled(400, 300), self)
        var_1.setText(R_animals[0][1].lower())
        var_2 = PicButton(QPixmap(an_2).scaled(400, 300), self)
        var_2.setText(R_animals[1][1].lower())
        var_3 = PicButton(QPixmap(an_3).scaled(400, 300), self)
        var_3.setText(R_animals[2][1].lower())

        self.animal = random.choice([R_animals[0][1],R_animals[1][1],R_animals[2][1]])
        print(self.animal)

        var_1.clicked.connect(self.ImageAnswerCheck)
        var_2.clicked.connect(self.ImageAnswerCheck)
        var_3.clicked.connect(self.ImageAnswerCheck)
        talk.clicked.connect(self.SoundPlay)

        options_line.addWidget(var_1)
        options_line.addWidget(var_2)
        options_line.addWidget(var_3)

        col.addLayout(talk_line)
        col.addLayout(options_line)
        self.window.addLayout(col)

    def SoundPlay(self):
        file = 'sounds\\' + self.animal +'.wav'
        PlaySound( file, SND_FILENAME)

    def ImageAnswerCheck(self):
        ans_animal = self.sender().text()
        print(ans_animal)
        if(self.animal.lower() == ans_animal):
            PlaySound(NEXTROUND, SND_FILENAME)
            self.ImageRecognitionWindow()
        else:
            PlaySound(TRYAGAIN, SND_FILENAME)

    def clearLayout(self, layout):
        """
            Recursive deletion of all layouts and widgets that belongs to selected layout.
        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
        return 'Done'


def real_main():
    """
        Main function creates object of Interface class and runs it as window application.
    """
    app = QtWidgets.QApplication(sys.argv)
    a_window = Interface()
    sys.exit(app.exec_())

if __name__ == '__main__':
    real_main()
