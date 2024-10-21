import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore
import os
import psutil
import time

class RenderValidatorUI(QtWidgets.QDialog):
    
    def __init__(self, parent = None):
        super(RenderValidatorUI, self).__init__(parent)
        self.setWindowTitle("Render Settings Validator")
        self.setMinimumSize(300, 400)
        self.setMaximumSize(700, 600)

        #all the labels 
        self.frame_range_label = QtWidgets.QLabel("Frame range: ")
        self.resolution_label = QtWidgets.QLabel("Resolution: ")
        self.render_camera_label = QtWidgets.QLabel("Render cameras: ")
        self.memory_usage_label = QtWidgets.QLabel("Memory usage: ")
        self.render_time_label = QtWidgets.QLabel("Render time: ")
        self.result = QtWidgets.QLabel(" ")
        self.result_01 = QtWidgets.QLabel(" ")
        self.result_02 = QtWidgets.QLabel(" ")

        #buttons 
        self.check_button = QtWidgets.QPushButton("Check")
        self.check_button.clicked.connect(self.get_attributes)

        self.validation_button = QtWidgets.QPushButton("Validate")
        self.validation_button.clicked.connect(self.validation_check)

        self.file_path_button = QtWidgets.QPushButton("Textures file path")
        self.file_path_button.clicked.connect(self.texture_check)

        self.abc_cache_button = QtWidgets.QPushButton("Abc cache")
        self.abc_cache_button.clicked.connect(self.abc_check)

        #separator 
        self.my_separator = QtWidgets.QFrame()
        self.my_separator.setFrameShape(QtWidgets.QFrame.HLine)
        self.my_separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.my_separator.setFixedHeight(10)

        self.new_separator = QtWidgets.QFrame()
        self.new_separator.setFrameShape(QtWidgets.QFrame.HLine)
        self.new_separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.new_separator.setFixedHeight(10)


        #layout 
        my_layout = QtWidgets.QVBoxLayout()
        my_layout.addWidget(self.frame_range_label)
        my_layout.addWidget(self.resolution_label)
        my_layout.addWidget(self.render_camera_label)
        my_layout.addWidget(self.memory_usage_label)
        my_layout.addWidget(self.render_time_label)
        my_layout.addWidget(self.check_button)
        my_layout.addWidget(self.validation_button)
        my_layout.addWidget(self.file_path_button)
        my_layout.addWidget(self.abc_cache_button)
        my_layout.addWidget(self.result)
        my_layout.addWidget(self.my_separator)
        my_layout.addWidget(self.result_01)
        my_layout.addWidget(self.new_separator)
        my_layout.addWidget(self.result_02)
        self.setLayout(my_layout)


    
    #maya default attribute parameters 
    def get_attributes(self):
        global global_dictionary
        start_frame = cmds.playbackOptions(query=True, min=True)
        end_frame = cmds.playbackOptions(query=True, max=True)
        resolution_width = cmds.getAttr("defaultResolution.width")
        resolution_height = cmds.getAttr("defaultResolution.height")
        renderable_cameras = [cmds.listRelatives(cam, parent=True, fullPath=False)[0] for cam in cmds.ls(type='camera') if cmds.getAttr(f"{cam}.renderable")]

        #get the process id of maya
        maya_id = os.getpid()
        process = psutil.Process(maya_id)
        initial_memory = process.memory_info().rss / (1024 ** 2)
        start_time = time.time()

        cmds.render()

        end_memory = process.memory_info().rss / (1024 ** 2)
        end_time = time.time()

        #update the labels information
        self.frame_range_label.setText(f"Frame range: {start_frame} - {end_frame}")
        self.resolution_label.setText(f"Resolution: {resolution_width} x {resolution_height}")
        self.render_camera_label.setText(f"Render cameras: {renderable_cameras}")
        self.memory_usage_label.setText(f"Memory usage: {end_memory - initial_memory}")
        self.render_time_label.setText(f"Render time: {end_time - start_time}")

        global_dictionary = {
            'start_frame': start_frame, 
            'end_frame': end_frame,
            'resolution_width': resolution_width,
            'resolution_height': resolution_height,
            'renderable cameras': renderable_cameras, 
            'memory_usage': end_memory - initial_memory,
            'render time': end_time - start_time

        }
    
    #the requirements 
    def validation_check(self):
        
        warnings = []

        #required values
        req_start_frame = 1
        req_end_frame = 50
        req_res_width = 1920
        req_res_height = 1080
        req_camera = "perspShape"
        req_RAM = 0.5
        req_time = 0.1

        if global_dictionary['start_frame'] != req_start_frame or global_dictionary['end_frame'] != req_end_frame:
            warnings.append(f"Not the right start and/or end frame. It should be from {req_start_frame} to {req_end_frame}")
        if global_dictionary['resolution_width'] != req_res_width or global_dictionary['resolution_height'] != req_res_height:
            warnings.append(f"Not the right resolution. It should be {req_res_width} x {req_res_height}")
        if global_dictionary['renderable cameras'] != req_camera:
            warnings.append(f"Not the right camera. It should be {req_camera}")
        if global_dictionary['memory_usage'] >= req_RAM:
            warnings.append(f"Ram should not be over {req_RAM}GB")
        if global_dictionary['render time'] >= req_time:
            warnings.append(f"Time should not be over {req_time}")

        if warnings:
            self.result.setText("\n".join(warnings))
        else:
            self.result.setText("All settings are correct!")

    def texture_check(self):
        #identify the texture files
        texture_warning = []

        file_nodes = cmds.ls(type = 'file')
        for node in file_nodes:
            file_path = cmds.getAttr(f"{node}.fileTextureName")
            if not os.path.exists(file_path):
                texture_warning.append(f"File not found at: {file_path}")
        if texture_warning:
            self.result_01.setText("\n".join(texture_warning))
        else:
            self.result_01.setText("All settings are correct!")

    def abc_check(self):

        abc_warning = []
        abc_list  = cmds.ls(type='AlembicNode')
        cache_directory = "C:/Users/aluaa/Desktop/pipeline td projects/Laika interview/cache/"
        cache_file = "spiderman_cache.abc"
        cache_path = os.path.join(cache_directory, cache_file)

        if os.path.exists(cache_path): 
            self.result_02.setText(f"Cache is already at {cache_path}")
        else:
        # Create a Yes/No dialog
            msg_box = QtWidgets.QMessageBox()
            msg_box.setIcon(QtWidgets.QMessageBox.Warning)
            msg_box.setText("No Alembic cache found.")
            msg_box.setInformativeText("Do you want to cache?")
            msg_box.setWindowTitle("Alembic Cache Missing")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            msg_box.setDefaultButton(QtWidgets.QMessageBox.No)

            # user's response
            response = msg_box.exec_()

            if response == QtWidgets.QMessageBox.Yes:
                self.create_cache()
            else:
                self.result_02.setText("Please add an Alembic cache.")
        
    
    def create_cache(self):
        export_object = "|spiderman"

        if not cmds.objExists(export_object):
            self.result_02.setText(f"Object {export_object} does not exist in the scene.")
            return

        start_frame = cmds.playbackOptions(q=True, min=True)
        end_frame = cmds.playbackOptions(q=True, max=True)

        cache_directory = "C:/Users/aluaa/Desktop/pipeline td projects/Laika interview/cache/"
        cache_file = "spiderman_cache.abc"
        cache_path = os.path.join(cache_directory, cache_file)

        alembic_command = f'-frameRange {start_frame} {end_frame} -dataFormat ogawa -root {export_object} -file "{cache_path}"'
        cmds.AbcExport(j=alembic_command)

        self.result_02.setText(f"Cache is created at {cache_path}")

my_window = RenderValidatorUI()
my_window.show()
