import os
import socket
import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QImage, QPalette, QBrush, QPixmap
from PyQt5 import QtWidgets
import subprocess
from robot import *
import time
from world_creation import *
from reset import *

class Interface(QtWidgets.QWidget):
    """
        Class Interface creates window application that serves
            as Baxter-robot interface for students.

        Interface is consisted of two windows:
            First one is Cubes configuration choice window.
            Second one is Robot control panel interface.

        Since those two windows are never exist on the same time,
             they are actually the same one: when we have chosen cubes configuration,
             app deletes all the objects of cubes configuration from the class member @window
             and adds all new objects from robot-control interface.

        Interface is inherited from Qt.QWidjet, so it may be useful to read
            documentation for Qt class to understand ideas of layouts, widgets etc.

        Important *** of the class:
            @detail
            @arm
            @curr_cube_pos
            @baxter
            @Valid_config

    """

    def __init__(self):
        """
            Init function runs a few functions one by one:
                Script_output - creates a new file for output of the program.
                Then we create object (@baxter) of the class Robot.
                @arm is arm that baxter use to replace cubes.
                The @window is created.
                init_ui adds all the objects of cube-choice to the @window.
                @time_for_action is used to prevent user from start new robot action,
                    while previous one wasn't finished.
        """
        super(QtWidgets.QWidget, self).__init__()
        self.Script_output()
        self.baxter = Robot()
        self.arm = 'left'
        self.window = QtWidgets.QHBoxLayout()
        self.init_ui()
        self.script_story.write('Script started at ' + str(time.asctime()) + '\n\n')
        self.time_for_action = time.time()

    def init_ui(self):
        """
            Adds all the objects of Cubes configuration choice window to the @window.
        """
        self.Cube_choice_window()
        self.setLayout(self.window)
        self.show()

    def Script_output(self):
        """
        Script_output creates a new file for output of the program by searching
            for previous runs of the application in output directory.

        Also name of each output file contain hostname of the computer,
            where script is running.
        """
        host_name = str(socket.gethostname()).split('.iem.technion.ac.il')[0]
        output_folder = os.listdir(str(os.getcwd()) + '/output')
        files_list = []
        if (len(output_folder) == 0):
            max_el = 0
        else:
            for file_name in output_folder:
                files_list.append(int(file_name.split('-')[-1].split('.')[0]))
            max_el = max(files_list)

        self.script_story = open('output/' + host_name + '-' + str(max_el + 1) + '.txt', 'w')

    def Cube_choice_window(self):
        """
            Creating of the interface for Cubes configuration choice window.

            Firstly method change window style using Cube_choice_window_style method.

            Cube_choice_window gives access to two functions:
                Start button redirects us to the Robot control panel interface
                    using Interface_window method.
                Close button starts closing process using CloseCmd method.
        """

        self.Cube_choice_window_style()

        self.col = QtWidgets.QVBoxLayout()

        self.Cubes_configuration = QtWidgets.QLabel('Choose cubes configuration:')
        self.Cubes_configuration.setStyleSheet("color: white; font: 18px")
        self.Cubes_configuration.setAlignment(Qt.AlignCenter)

        self.cubes_line = QtWidgets.QHBoxLayout()
        self.CUBE_1 = QtWidgets.QComboBox()
        self.CUBE_2 = QtWidgets.QComboBox()
        self.CUBE_3 = QtWidgets.QComboBox()

        self.CUBE_1.addItems(["1", "2", "3", "4", "5", "6"])
        self.CUBE_2.addItems(["1", "2", "3", "4", "5", "6"])
        self.CUBE_3.addItems(["1", "2", "3", "4", "5", "6"])

        self.cubes_line.addWidget(self.CUBE_1)
        self.cubes_line.addWidget(self.CUBE_2)
        self.cubes_line.addWidget(self.CUBE_3)

        self.Start = QtWidgets.QPushButton('Start')
        self.Start.clicked.connect(self.Interface_window)

        self.Close = QtWidgets.QPushButton('Close')
        self.Close.clicked.connect(self.CloseCmd)

        self.l_line = QtWidgets.QHBoxLayout()
        self.l_line.addWidget(self.Start)

        self.col.addWidget(self.Cubes_configuration)
        self.col.addLayout(self.cubes_line)
        self.col.addWidget(self.Start)
        self.col.addWidget(self.Close)

        self.window.addLayout(self.col)

    def Interface_window(self):
        """
            The Interface_window method represents Robot control-panel.

            Before providing access to robot commands to student this method make
                some preparational work:

                1) Method gets cubes configuration from ComboBoxes
                    using Get_cubes_config method and put them into @cubes_facet_numbers .

                2) Clears @window object to fill it then with objects of
                    Robot control panel interface.

                3) Thirdly change window style using Conrol_panel_window_style method.

                4) Creates set of flags to prevent impossible actions.

                5) Control panel window is separated on 4 parts (@col_1, @col_2, @col_3, @col_4)
                    with different method each:
                    @Input method is used to choose cube that we want to manipulate.
                    @Commands method is used to manipulate the chosen cube.
                    @Output method shows when user trying to perform impossible action.
                    @End_command method can reset cube position, return to cubes configuration window
                        or quit from the program.

                6) load_gazebo_models is a function from world_creation.py file.
                    It creates models of tables and cubes and places cubes on the tables
                    using their starting configuration that we've chosen on
                    cube choice window.
        """

        self.Valid_config = 1
        self.cubes_facet_numbers = self.Get_cubes_config()
        num1 = str(int(self.cubes_facet_numbers[0])) + ', '
        num2 = str(int(self.cubes_facet_numbers[1])) + ', '
        num3 = str(int(self.cubes_facet_numbers[2])) + '\n'
        self.script_story.write('Starting cubes configurarion: ' + num1  + num2 + num3 + '\n')
        print(self.cubes_facet_numbers)
        self.clearLayout(self.col)

        self.Conrol_panel_window_style()

        self.detail = 'None'

        self.Angle_enter = 1
        self.Type_enter = 0
        self.Crd_enter  = 1
        self.Detail_on_the_floor = 0
        self.Detail_on_the_buffer = 0
        self.Buffer_is_free = 1
        self.Cube_is_already_on_buffer = 0
        self.Cube_is_already_on_destination = 0

        self.Floor_flag = 0
        self.Type_flag  = 0
        self.Crd_flag = 0
        self.Nth_do_flag = 0
        self.Not_on_the_buffer_flag = 0
        self.Buffer_is_not_free_flag = 0
        self.Cube_is_already_on_buffer_flag = 0
        self.Cube_is_already_on_destination_flag = 0
        self.prev_command_finish = time.time()
        self.curr_command_start = time.time()

        self.col_1 = QtWidgets.QVBoxLayout()
        self.col_2 = QtWidgets.QVBoxLayout()
        self.col_3 = QtWidgets.QVBoxLayout()
        self.col_4 = QtWidgets.QVBoxLayout()

        self.Input()
        self.Commands()
        self.Output()
        self.End_commands()

        self.window.addLayout(self.col_1)
        self.window.addLayout(self.col_2)
        self.window.addLayout(self.col_3)
        self.window.addLayout(self.col_4)

        self.cur_cube_crd = [0,0,0]
        self.curr_finish_table = 0
        load_gazebo_models(self.cubes_facet_numbers)

    def Cube_choice_window_style(self):
        """
            Style function for cube choice window.
            Sets window geometry, title and background.
        """

        oImage = QImage("pics/back_3.jpg")
        sImage = oImage.scaled(QSize(500, 200), Qt.KeepAspectRatioByExpanding)  # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))  # 10 = Windowrole
        self.setPalette(palette)
        self.setWindowTitle("Baxter interface")
        self.setGeometry(200, 200, 450, 200)

    def Conrol_panel_window_style(self):
        """
            Style function for control panel window.
            Sets window geometry, title and background.
        """

        oImage = QImage("pics/back.jpg")
        sImage = oImage.scaled(700, 200, Qt.KeepAspectRatioByExpanding)  # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))  # 10 = Windowrole
        self.setPalette(palette)
        self.setWindowTitle("Baxter interface")
        self.setGeometry(200,200,700, 200)

    def Input(self):
        """
            @col_1

            Three buttons for each cube.

            When one of the buttons was chosen - Detail_choice method is activated.
        """

        Cube_sign = QtWidgets.QLabel('Cube type :')
        Cube_sign.setAlignment(Qt.AlignCenter)
        Cube_sign.setStyleSheet("color: white; font: 18px")
        cn_line = QtWidgets.QHBoxLayout()
        cn_line.addWidget(Cube_sign)
        cn_line.setAlignment(Qt.AlignTop)
        self.col_1.addLayout(cn_line)

        an_line = QtWidgets.QHBoxLayout()
        space = QtWidgets.QLabel(' ')
        space.setAlignment(Qt.AlignCenter)
        an_line.addWidget(space)
        self.col_1.addLayout(an_line)

        self.One    = QtWidgets.QPushButton('1')
        self.Two    = QtWidgets.QPushButton('2')
        self.Three  = QtWidgets.QPushButton('3')

        self.col_1.addWidget(self.One)
        self.col_1.addWidget(self.Two)
        self.col_1.addWidget(self.Three)

        self.One.clicked.connect(self.Detail_choice)
        self.Two.clicked.connect(self.Detail_choice)
        self.Three.clicked.connect(self.Detail_choice)

    def Commands(self):
        """
            @col_2

            Commands gives access to three functions:
                Put the cube from it's position to the buffer.
                Rotate the cube that is lying on the buffer using rotation vector that was set by user.
                Put the cube from it's position to it's final position.

                Every button is connected to the btn_click method, that definies that robot is
                    ready to execute chosen action.
        """

        self.TAKE_CUBE = QtWidgets.QPushButton('Put the cube on the buffer')
        self.PUT_CUBE = QtWidgets.QPushButton('Put the cube on the destination')
        self.TURN_CUBE = QtWidgets.QPushButton('Rotate the cube')

        t_box = QtWidgets.QVBoxLayout()
        t_box.setAlignment(Qt.AlignBottom)

        an_line = QtWidgets.QHBoxLayout()
        self.C_1 = QtWidgets.QComboBox()
        self.C_2 = QtWidgets.QComboBox()
        self.C_3 = QtWidgets.QComboBox()
        self.C_4 = QtWidgets.QComboBox()

        self.C_1.addItems(["X", "Y", "Z"])
        self.C_2.addItems(["0", "-1", "1", "2"])
        self.C_3.addItems(["X", "Y", "Z"])
        self.C_4.addItems(["0", "-1", "1", "2"])

        an_line.addWidget(self.C_1)
        an_line.addWidget(self.C_2)
        an_line.addWidget(self.C_3)
        an_line.addWidget(self.C_4)

        self.col_2.addWidget(self.TAKE_CUBE)
        t_box.addLayout(an_line)
        t_box.addWidget(self.TURN_CUBE)
        t_box.addWidget(self.PUT_CUBE)

        self.col_2.addLayout(t_box)

        self.TURN_CUBE.clicked.connect(self.btn_click)
        self.TAKE_CUBE.clicked.connect(self.btn_click)
        self.PUT_CUBE.clicked.connect(self.btn_click)

    def Output(self):
        """
            @col_3

            If user tries to execute impossible action, we send error sign
                to the output area.
        """
        Err_sign = QtWidgets.QLabel('Output :')
        Err_sign.setAlignment(Qt.AlignCenter)
        Err_sign.setStyleSheet("color: white; font: 18px")
        an_line = QtWidgets.QHBoxLayout()
        an_line.setAlignment(Qt.AlignTop)
        an_line.addWidget(Err_sign)
        self.col_3.addLayout(an_line)

    def End_commands(self):
        """
            @col_4

            This method gives access to three actions:
                Reset current cube pose:
                    Returns cube in the position (place and rotation) in which it was
                    created using Reset_curr_cube method.
                Reset initial sequence:
                    Returns to Cube configuration choice window using Back_to_number_choice method
                Quit the program:
                    Quits from program. Since we could quit from the application both from window
                    with cube configuration choice and also from control-panel window, I connected quit
                    button to the btn_click method.
        """

        col = QtWidgets.QVBoxLayout()
        col.setAlignment(Qt.AlignBottom)

        self.Reset_button = QtWidgets.QPushButton('Reset current cube pose')
        self.Reset_button.clicked.connect(self.Reset_curr_cube)

        self.Back_to_choice = QtWidgets.QPushButton('Reset initial sequence')
        self.Back_to_choice.clicked.connect(self.Back_to_number_choice)
        self.END = QtWidgets.QPushButton('Quit the program')
        self.END.clicked.connect(self.btn_click)

        col.addWidget(self.Reset_button)
        col.addWidget(self.Back_to_choice)
        col.addWidget(self.END)
        self.col_4.addLayout(col)

    def Reset_curr_cube(self):
        """
            First of all function checks if exicution of the previous command
                wasn't finished. If so, we reset cube position using reset_one_cube function
                from world_creation.py

            If previous command is still executes, method sends message to the terminal.
        """
        now = time.time()
        if(now - self.prev_command_finish > Time_for_break):
            self.Er_clean()
            if(self.detail!= 'None'):
                self.script_story.write('Cube ' + str(self.detail.split('_')[1]) + ' ' + 'was reseted\n\n')
                cube_num = int(str(self.detail.split('_')[1]))
                reset_one_cube(self.detail, cube_num, self.cubes_facet_numbers[cube_num-1])
        else:
            print('Previous command was running')

    def Back_to_number_choice(self):
        """
            First of all function checks if exicution of the previous command
                wasn't finished. If so, we delete cubes from the simulation and then
                transform Robot control panel interface into Cubes configuration choice window
                using clearLayout and Cube_choice_window methods.

            If previous command is still executes, method sends message to the terminal.
        """
        now = time.time()
        if(now - self.prev_command_finish > Time_for_break):
            self.script_story.write('= = = = = = = = = = = = = = = =\n\n')
            self.script_story.write('Cubes configuration was reseted\n')
            self.Er_clean()
            delete_gazebo_models('cubes')
            self.clearLayout(self.window)
            self.Cube_choice_window()
        else:
            print('Previous command was running')

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

    def Get_arguments(self):
        """
            Function that gets rotation vector from user, checks that it's valid and
            returns input as a list.
        """
        self.Valid_config = 1
        c_1 = self.C_1.currentText().encode('ascii')
        c_2 = float(self.C_2.currentText())
        c_3 = self.C_3.currentText().encode('ascii')
        c_4 = float(self.C_4.currentText())
        if((c_1 == 'X' or c_1 == 'Y') and ((c_2 == 1) or (c_2 == -1)) ):
            self.Valid_config = 0
        if ((c_3 == 'X' or c_3 == 'Y') and ((c_4 == 1) or (c_4 == -1))):
            self.Valid_config = 0
        return [c_1, c_2, c_3, c_4]

    def Get_cubes_config(self):
        """
            Function that gets cubes configuration vector from Cubes configuration choice window.
        """
        cube_1 = int(self.CUBE_1.currentText())
        cube_2 = int(self.CUBE_2.currentText())
        cube_3 = int(self.CUBE_3.currentText())
        return [cube_1, cube_2, cube_3]

    def btn_click(self):
        """
            First of all function checks if exicution of the previous command wasn't finished.
            If previous command is still executes, method sends message to the terminal.

            Else:
                The basic idea is that to perform the action requested by the user, the conditions
                necessary for this action must be met in the simulation world. For example, in order for
                the robot to transfer the cube from the initial position to the buffer, the cube must
                be selected, the cube must not yet be on the buffer, the cube must be in the robot's
                access zone (in our case, not on the floor) and the buffer must be free.

                In case every condition for action is satisfied, function will execute it. Otherwise,
                it will return Error message to the Output area.

            For future programmers, all "if" cases could be merged together, but separation of the cases
                by the action that we have to execute, makes code more readable.
        """
        now = time.time()
        if(now - self.prev_command_finish > Time_for_break):
            # Every time user executes any action, program deletes error message at the output
            #   area (if was there) and checks current configuration in every 'if' down the road.
            self.Er_clean()

            arm = 'left'
            sender = self.sender()
            self.angle = self.Get_arguments()

            if (self.Type_enter): # If we pressed button 1 or 2 or 3:
                temp_pos = get_actual_pose(self.detail)
                if( temp_pos[2] - 0.92 < - 0.2):
                    self.Detail_on_the_floor = 1
                else:
                    self.Detail_on_the_floor = 0

                if( temp_pos[0] > 0.53 and temp_pos[0] < 0.63 and
                        temp_pos[1] > 0.57 and temp_pos[1] <  0.715):
                    self.Detail_on_the_buffer = 1
                else:
                    self.Detail_on_the_buffer = 0

            if sender.text() == 'Put the cube on the buffer':
                self.Cube_is_already_on_buffer = 0
                self.Buffer_is_free = 1

                for detail in details:
                    temp_pos = get_actual_pose(detail)
                    if (temp_pos[0] > 0.53 and temp_pos[0] < 0.63 and
                            temp_pos[1] > 0.57 and temp_pos[1] < 0.715 and temp_pos[2] - 0.92 > - 0.2):
                        self.Buffer_is_free = 0
                        if (detail == self.detail):
                            self.Cube_is_already_on_buffer = 1

                if (self.Type_enter):
                    if( not self.Detail_on_the_floor):
                        if (not self.Cube_is_already_on_buffer):
                            if(self.Buffer_is_free):
                                self.ToBuffCmd(arm)
                                self.script_story.write(
                                    'Cube ' + str(self.detail.split('_')[1]) + '  was taken to the buffer at ' +
                                    time.asctime().split(' ')[-2] + '\n')
                                print('Cube ' + str(self.detail.split('_')[1]) + '  was taken to the buffer at ' +
                                    time.asctime().split(' ')[-2] + '\n')
                                self.time_for_action = time.time()
                                self.prev_command_finish = time.time()
                            else:
                                self.Error('Buffer is already occupied')
                        else:
                            self.Error('Cube is already on buffer')
                    else:
                        self.Error('Detail is on the floor')
                else:
                    self.Error('Detail')

            if sender.text() == 'Rotate the cube':
                if(self.Type_enter):
                    if (self.Valid_config):
                        if (not self.Detail_on_the_floor):
                            angle = self.angle
                            if (self.Detail_on_the_buffer):
                                if (angle[0] != angle[2] or angle[1] != angle[3]):
                                    angle1 = angle[0] + ', '
                                    angle2 = str(int(angle[1])) + ', '
                                    angle3 = angle[2] + ', '
                                    angle4 = str(int(angle[3]))
                                    str_angle = angle1 + angle2 + angle3 + angle4
                                    self.script_story.write('Rotating by ' + str_angle + '\n')
                                    self.TurnCmd(arm)
                                    self.prev_command_finish = time.time()
                                else:
                                    self.Error('Nothing to do')
                            else:
                                self.Error('Detail is not on the buffer')
                        else:
                            self.Error('Detail is on the floor')
                    else:
                        self.Error('Configuration')
                else:
                    self.Error('Detail')

            if sender.text() == 'Put the cube on the destination':

                self.Cube_is_already_on_destination = 0
                temp_pos = get_actual_pose(self.detail)
                if (temp_pos[0] > -0.1 and temp_pos[0] < -0.053988 and
                        temp_pos[1] > 0.720928 and temp_pos[1] < 0.977914 and temp_pos[2] - 0.92 > - 0.2):
                            self.Cube_is_already_on_destination = 1

                if(self.Type_enter):
                    if (not self.Detail_on_the_floor):
                        if(not self.Cube_is_already_on_destination):
                            if (self.Detail_on_the_buffer):
                                self.script_story.write(
                                    'Cube ' + str(self.detail.split('_')[1]) + ' was taken to the destination at ' + time.asctime().split(' ')[-2] + '\n')
                                print('Cube ' + str(self.detail.split('_')[1]) + ' was taken to the destination at ' + time.asctime().split(' ')[-2] + '\n')
                                time_for_one_cube = time.time() - self.time_for_action
                                self.script_story.write('Time spent on '
                                                        'Cube ' + str(self.detail.split('_')[1]) + ' : ' + str(
                                    round(time_for_one_cube, 2)) + ' seconds' + '\n\n')
                                print('Time spent on '
                                                        'Cube ' + str(self.detail.split('_')[1]) + ' : ' + str(
                                    round(time_for_one_cube, 2)) + ' seconds' + '\n')
                                self.ToFinCmd(arm)
                                self.prev_command_finish = time.time()
                            else:
                                self.Error('Detail is not on the buffer')
                        else:
                            self.Error('Cube is already on destination')
                    else:
                        self.Error('Detail is on the floor')
                else:
                    self.Error('Detail')

            if sender.text() == 'Quit the program':
                self.CloseCmd()
        else:
            print('Previous command was running')

    def ToBuffCmd(self, arm ='left'):
        """
            Gets position of the cube that we want to take.
            Sends command to the @baxter to move it to the buffer using chosen hand.
        """
        print("Moves detail to the buffer")
        temp = get_actual_pose(self.detail)
        self.baxter.l_gripper.open()
        self.baxter.take_the_cube_from_start(arm, temp, self.detail)
        print('Done!')

    def TurnCmd(self, arm = 'left'):
        """
            Gets position of the cube that we want to rotate for more accurate grab.
            Sends command to the @baxter to rotate the cube using rotation vector.
        """
        angle = self.angle
        print("Turns cube by angle: ", angle)
        temp = get_actual_pose(self.detail)
        self.baxter.l_gripper.open()
        self.baxter.turn_the_cube_on_buffer(angle, temp, arm )
        print('Done!')

    def ToFinCmd(self, arm='left'):
        """
            Gets position of the cube that we want to take.
            Sends command to the @baxter to move it to the final position using chosen hand.
        """
        print("Moves detail to the buffer")
        temp = get_actual_pose(self.detail)
        cube_type = int(self.detail.split('_')[1])
        self.baxter.l_gripper.open()
        self.baxter.take_the_cube_to_finish(arm, temp, cube_type)
        print('Done!')

    def CloseCmd(self):
        """
            Safe way to exit from the program. It checkes that robot finished execution of
            the previous action and close output file before closing the application.
        """
        now = time.time()
        if (now - self.prev_command_finish > Time_for_break):
            delete_gazebo_models('all')
            self.script_story.close()
            print('Bye!')
            self.close()
        else:
            print('Previous command was running')

    def Error(self, er_type):
        """
            Sends error message to the output area using error type, from btn_click method.
        """
        if (er_type == 'Nothing to do'):
            if (self.Nth_do_flag == 0) :
                self.Nth_do_sign = QtWidgets.QLabel('Pointless action')
                self.Nth_do_sign.setStyleSheet("color: red; font: 18px")
                self.Nth_do_sign.setAlignment(Qt.AlignCenter)
                self.col_3.addWidget(self.Nth_do_sign)
                self.Nth_do_flag = 1
        if (er_type == 'Configuration'):
            if (self.Crd_flag == 0 and self.Valid_config == 0) :
                self.Crd_sign = QtWidgets.QLabel('Invalid command')
                self.Crd_sign.setAlignment(Qt.AlignCenter)
                self.Crd_sign.setStyleSheet("color: red; font: 18px")
                self.col_3.addWidget(self.Crd_sign)
                self.Crd_flag = 1
        if (er_type == 'Detail'):
            if (self.Type_flag == 0 and self.Type_enter == 0):
                self.Type_sign = QtWidgets.QLabel('Detail type \nwasn\'t chosen')
                self.Type_sign.setAlignment(Qt.AlignCenter)
                self.Type_sign.setStyleSheet("color: red; font: 18px")
                self.col_3.addWidget(self.Type_sign)
                self.Type_flag = 1
        if (er_type == 'Detail is on the floor'):
            if (self.Floor_flag == 0):
                self.Floor_sign = QtWidgets.QLabel('Detail is on\n the floor')
                self.Floor_sign.setAlignment(Qt.AlignCenter)
                self.Floor_sign.setStyleSheet("color: red; font: 18px")
                self.col_3.addWidget(self.Floor_sign)
                self.Floor_flag = 1
        if (er_type == 'Detail is not on the buffer'):
            if (self.Not_on_the_buffer_flag == 0):
                self.Not_on_the_buffer_sign = QtWidgets.QLabel('Cube is not\n on the buffer')
                self.Not_on_the_buffer_sign.setAlignment(Qt.AlignCenter)
                self.Not_on_the_buffer_sign.setStyleSheet("color: red; font: 18px")
                self.col_3.addWidget(self.Not_on_the_buffer_sign)
                self.Not_on_the_buffer_flag = 1
        if (er_type == 'Buffer is already occupied'):
            if (self.Buffer_is_not_free_flag == 0):
                self.Buffer_is_not_free_sign = QtWidgets.QLabel('Buffer is\n already occupied')
                self.Buffer_is_not_free_sign.setAlignment(Qt.AlignCenter)
                self.Buffer_is_not_free_sign.setStyleSheet("color: red; font: 18px")
                self.col_3.addWidget(self.Buffer_is_not_free_sign)
                self.Buffer_is_not_free_flag = 1
        if (er_type == 'Cube is already on buffer'):
            if (self.Cube_is_already_on_buffer_flag == 0):
                self.Cube_is_already_on_buffer_sign = QtWidgets.QLabel('Cube is already\n on buffer')
                self.Cube_is_already_on_buffer_sign.setAlignment(Qt.AlignCenter)
                self.Cube_is_already_on_buffer_sign.setStyleSheet("color: red; font: 18px")
                self.col_3.addWidget(self.Cube_is_already_on_buffer_sign)
                self.Cube_is_already_on_buffer_flag = 1
        if (er_type == 'Cube is already on destination'):
            if (self.Cube_is_already_on_destination_flag == 0):
                self.Cube_is_already_on_destination_sign = QtWidgets.QLabel('Cube is already\n on destination')
                self.Cube_is_already_on_destination_sign.setAlignment(Qt.AlignCenter)
                self.Cube_is_already_on_destination_sign.setStyleSheet("color: red; font: 18px")
                self.col_3.addWidget(self.Cube_is_already_on_destination_sign)
                self.Cube_is_already_on_destination_flag = 1

    def Er_clean(self):
        """
            Deletes any error messages that appears to be in the output area.
        """
        if(self.Type_flag):
            self.Type_sign.deleteLater()
            self.Type_flag = 0
        if (self.Crd_flag):
            self.Crd_sign.deleteLater()
            self.Crd_flag = 0
        if (self.Floor_flag):
            self.Floor_sign.deleteLater()
            self.Floor_flag = 0
        if (self.Nth_do_flag):
            self.Nth_do_sign.deleteLater()
            self.Nth_do_flag = 0
        if (self.Not_on_the_buffer_flag):
            self.Not_on_the_buffer_sign.deleteLater()
            self.Not_on_the_buffer_flag = 0
        if (self.Buffer_is_not_free_flag):
            self.Buffer_is_not_free_sign.deleteLater()
            self.Buffer_is_not_free_flag = 0
        if (self.Cube_is_already_on_buffer_flag):
            self.Cube_is_already_on_buffer_sign.deleteLater()
            self.Cube_is_already_on_buffer_flag = 0
        if (self.Cube_is_already_on_destination_flag):
            self.Cube_is_already_on_destination_sign.deleteLater()
            self.Cube_is_already_on_destination_flag = 0

    def Detail_choice(self):
        """
            First of all function checks if exicution of the previous command
                wasn't finished. If so, @detail becomes chosen cube,
                pushed button highlights in orange, and @curr_cube_pos gets
                @detail position in simulator using gms_client function from world_creation.py.

            If previous command is still executes, method sends message to the terminal.
        """
        now = time.time()
        if(now - self.prev_command_finish > Time_for_break):
            self.Type_enter = 1
            self.Er_clean()
            sender = self.sender()
            self.detail = 'cube_' + str(sender.text())

            if(int(str(sender.text())) == 1):
                self.One.setStyleSheet("color: black; background-color: orange;")
                self.Two.setStyleSheet("color: black; ")
                self.Three.setStyleSheet("color: black; ")
            if(int(str(sender.text())) == 2):
                self.One.setStyleSheet("color: black; ")
                self.Two.setStyleSheet("color: black; background-color: orange;")
                self.Three.setStyleSheet("color: black; ")
            if(int(str(sender.text())) == 3):
                self.One.setStyleSheet("color: black;")
                self.Two.setStyleSheet("color: black;")
                self.Three.setStyleSheet("color: black; background-color: orange;")

            self.curr_cube_pos = [gms_client(self.detail, "world").pose.position.x,
            gms_client(self.detail, "world").pose.position.y,
            gms_client(self.detail, "world").pose.position.z]
            print(self.curr_cube_pos)
        else:
            print('Previous command was running')

def real_main():
    """
        Main function creates object of Interface class and runs it as window application.
    """
    app = QtWidgets.QApplication(sys.argv)
    a_window = Interface()
    sys.exit(app.exec_())

if __name__ == '__main__':
    real_main()

"""
Cubes configuration choice window
Robot control panel interface
"""