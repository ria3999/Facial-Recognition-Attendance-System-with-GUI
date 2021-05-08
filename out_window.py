from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QTimer, QDate
from PyQt5.QtWidgets import QDialog,QMessageBox
import cv2
import face_recognition
import numpy as np
import datetime
import os
import csv

class Ui_OutputDialog(QDialog):
    class_names = []
    encode_list = []
    TimeList1 = []
    TimeList2 = []
    def __init__(self):
        super(Ui_OutputDialog, self).__init__()
        loadUi("C:\\Users\\riago\\6thSemMiniProject\\outputwindow.ui", self)
        now = QDate.currentDate()
        current_date = now.toString('yyyy.MM.dd')
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.Date_Label.setText(current_date)
        self.Time_Label.setText(current_time)
        self.image = None

    @pyqtSlot()
    def startVideo(self, camera_name):
        if len(camera_name) == 1:
        	self.capture = cv2.VideoCapture(int(camera_name))
        else:
        	self.capture = cv2.VideoCapture(camera_name)
        self.timer = QTimer(self)
        path = "C:\\Users\\riago\\6thSemMiniProject\\TrainingImage"
        if not os.path.exists(path):
            os.mkdir(path)
        images = []
        attendance_list = os.listdir(path)
        for cl in attendance_list:
            cur_img = cv2.imread(f'{path}/{cl}')
            images.append(cur_img)
            self.class_names.append(os.path.splitext(cl)[0])
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(img)
            encodes_cur_frame = face_recognition.face_encodings(img, boxes)[0]
            self.encode_list.append(encodes_cur_frame)
        self.timer.timeout.connect(self.update_frame)  
        self.timer.start(10)  

    def face_rec_(self, frame, encode_list_known, class_names):
        def mark_attendance(name):
            if self.ClockInButton.isChecked():
                self.ClockInButton.setEnabled(False)
                with open('C:\\Users\\riago\\6thSemMiniProject\\Attendance.csv', 'a') as f:
                        if (name != 'unknown'):
                            buttonReply = QMessageBox.question(self, 'Welcome ' + name, 'Are you Clocking In?' ,
                                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if buttonReply == QMessageBox.Yes: 
                                k=datetime.datetime.now()
                                date_time_string = k.strftime("%m/%d/%Y %H:%M:%S")
                                #print(date_time_string)
                                f.writelines(f'\n{name},{date_time_string},Clock In')
                                self.ClockInButton.setChecked(False)
                                self.NameLabel.setText(name)
                                self.StatusLabel.setText('Clocked In')
                                self.HoursLabel.setText('  Measuring')
                                self.MinLabel.setText('')
                                #self.CalculateElapse(name)
                                #print('Yes clicked and detected')
                                self.Time1 = datetime.datetime.now()
                                #print(self.Time1)
                                self.ClockInButton.setEnabled(True)
                            else:
                                #print('Not clicked.')
                                self.ClockInButton.setEnabled(True)
            elif self.ClockOutButton.isChecked():
                self.ClockOutButton.setEnabled(False)
                with open('C:\\Users\\riago\\6thSemMiniProject\\Attendance.csv', 'a') as f:
                        if (name != 'unknown'):
                            buttonReply = QMessageBox.question(self, 'Cheers ' + name, 'Are you Clocking Out?',
                                                              QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if buttonReply == QMessageBox.Yes:
                                date_time_string = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                                f.writelines(f'\n{name},{date_time_string},Clock Out')
                                self.ClockOutButton.setChecked(False)
                                self.NameLabel.setText(name)
                                self.StatusLabel.setText('Clocked Out')
                                self.Time2 = datetime.datetime.now()
                                #print('HH')
                                #print(self.TimeList2)
                                self.ElapseList(name)
                                #print("afterelapse")
                                #print(self.TimeList2)
                                self.TimeList2.append(datetime.datetime.now())
                                #print(self.TimeList1[-1]);
                                CheckInTime = self.TimeList1[-1]
                                #print("Check in time"+CheckInTime)
                                #print("Check in time")
                                #print(CheckInTime)
                                CheckOutTime = self.TimeList2[-1]
                                #print("Check out time")
                                #print(CheckOutTime)
                                self.ElapseHours = (CheckOutTime - CheckInTime)
                                #print("Elapse hours")
                                #print(self.ElapseHours)
                                self.HoursLabel.setText("{:.0f}".format(abs(self.ElapseHours.total_seconds() / 60**2)) + 'h')
                                self.MinLabel.setText("{:.0f}".format(abs(self.ElapseHours.total_seconds() / 60)%60) + 'm')
                                self.ClockOutButton.setEnabled(True)
                            else:
                                #print('Not clicked.')
                                self.ClockOutButton.setEnabled(True)

  
        faces_cur_frame = face_recognition.face_locations(frame)
        encodes_cur_frame = face_recognition.face_encodings(frame, faces_cur_frame)

        for encodeFace, faceLoc in zip(encodes_cur_frame, faces_cur_frame):
            match = face_recognition.compare_faces(encode_list_known, encodeFace, tolerance=0.50)
            face_dis = face_recognition.face_distance(encode_list_known, encodeFace)
            name = "unknown"
            best_match_index = np.argmin(face_dis)
            # print("s",best_match_index)
            if match[best_match_index]:
                name = class_names[best_match_index].upper()
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            mark_attendance(name)

        return frame


    def ElapseList(self,name):
        #print("in elapse list")
        with open('C:\\Users\\riago\\6thSemMiniProject\\Attendance.csv', "r+") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            #Time1 = datetime.datetime.now()
            #print(Time1)
            #Time2 = datetime.datetime.now()
            #print(Time2)
            for row in csv_reader:
                for field in row:
                    if field in row:
                        if field == 'Clock In':
                            if row[0] == name:
                                Time1 = (datetime.datetime.strptime(row[1], '%m/%d/%Y %H:%M:%S'))
                                self.TimeList1.append(Time1)
                               # print(self.TimeList1)
                        if field == 'Clock Out':
                            if row[0] == name:
                                #print(row[0])
                                #print(row[1])
                                Time2 = (datetime.datetime.strptime(row[1], '%m/%d/%Y %H:%M:%S'))
                                self.TimeList2.append(Time2)
                                #print(self.TimeList2)
            
                                

    def update_frame(self):
        ret, self.image = self.capture.read()
        self.displayImage(self.image, self.encode_list, self.class_names, 1)

    def displayImage(self, image, encode_list, class_names, window=1): 
        image = cv2.resize(image, (640, 480))
        try:
            image = self.face_rec_(image, encode_list, class_names)
        except Exception as e:
            print(e)
        qformat = QImage.Format_Indexed8
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel.setScaledContents(True)
