# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 16:22:25 2021

@author: mWinter
"""

from remi import gui
import datetime
import os
from backend import ProcessingFilesBackEnd
from utils import getAtomNumber, estimateTemperatureLongDipoletrap, estimateTemperature2DGaussian
import time

DATA_DIR = '.'

class AtomNumberWidget():
    
    def __init__(self, master, name):
        self.master = master
        self.name = name
        
        try:
            self.variables = self.master.config[name]
        except:
            self.master.config[name] = {'AN_dropdown': 'default'}
            self.variables = self.master.config[name]
        
        # Define Menu Items
        self.settings = gui.MenuItem(name, width=100, height=30)
        self.settings.onclick.do(self.settings_pressed)
        
        self.available_AN_funcs = {'default' : getAtomNumber}
        self.func = self.available_AN_funcs[self.variables['AN_dropdown']]
        
    def settings_pressed(self, widget):
        self.AN_menu_dialog = gui.GenericDialog(title=self.name + ' Menu', message='Click Ok to transfer content to main page', width='500px')
        
        self.AN_dropdown = gui.DropDown.new_from_list(self.available_AN_funcs.keys(),
                                                    width=200, height=20)
        self.AN_dropdown.select_by_value(self.variables['AN_dropdown'])
        self.AN_dropdown.onchange.do(self.AN_dropdown_changed)
        self.AN_menu_dialog.add_field_with_label('AN_dropdown', 'Choose AN function', self.AN_dropdown)
        
        self.AN_menu_dialog.confirm_dialog.do(self.update_AN_menu)
        self.AN_menu_dialog.show(self.master)
        
    def update_AN_menu(self, widget):
        self.variables['AN_dropdown'] = self.AN_dropdown.get_value()
        
        
        self.func = self.available_AN_funcs[self.AN_dropdown.get_value()]
    
    def AN_dropdown_changed(self, widget, chosen_AN):
        pass
    
class TemperatureWidget():
    
    def __init__(self, master, name):
        self.master = master
        self.name = name
        
        try:
            self.variables = self.master.config[name]
        except:
            self.master.config[name] = {'T_dropdown': 'Long Dipole Trap'}
            self.variables = self.master.config[name]
        
        # Define Menu Items
        self.settings = gui.MenuItem(name, width=100, height=30)
        self.settings.onclick.do(self.settings_pressed)
        
        
        # Widgets:
        self.longdipoletrap = LongDipoleTrapWidget(self.master, 'Long Dipole Trap')
        self.longdipoletrap2D = LongDipoleTrap2DWidget(self.master, 'Long Dipole Trap 2D')
        
        self.available_T_widgets = {self.longdipoletrap.name: self.longdipoletrap,
                                    self.longdipoletrap2D.name: self.longdipoletrap2D}        
        self.T_widget = self.available_T_widgets[self.variables['T_dropdown']]
    
        self.func = self.T_widget.estimate_temperature
        
    def settings_pressed(self, widget):
        self.T_menu_dialog = gui.GenericDialog(title=self.name + ' Menu', message='Click Ok to transfer content to main page', width='500px')
        
        self.T_dropdown = gui.DropDown.new_from_list(self.available_T_widgets.keys(),
                                                    width=200, height=20)
        self.T_dropdown.select_by_value(self.variables['T_dropdown'])
        self.T_dropdown.onchange.do(self.T_dropdown_changed)
        self.T_menu_dialog.add_field_with_label('T_dropdown', 'Choose T function', self.T_dropdown)
        
        self.T_menu_dialog.add_field_with_label(self.T_widget.name, 'Choose guess params:', self.T_widget)
        
        self.T_menu_dialog.confirm_dialog.do(self.update_T_menu)
        self.T_menu_dialog.show(self.master)
        
    def update_T_menu(self, widget):
        self.T_widget.update_variables()
        
        self.func = self.T_widget.estimate_temperature
    
    def T_dropdown_changed(self, widget, chosen_T):
        self.T_menu_dialog.container.remove_child(self.T_menu_dialog.container.get_child(self.T_widget.name))
        
        self.variables['T_dropdown'] = self.T_dropdown.get_value()
        self.T_widget = self.available_T_widgets[self.variables['T_dropdown']]
        
        self.T_menu_dialog.add_field_with_label(self.T_widget.name, 'Choose guess params:', self.T_widget)

class InputLabel(gui.HBox):
    
    def __init__(self, label='Input', input_type='number', default_value='', **kwargs):
        super(InputLabel, self).__init__(**kwargs)
        
        self.label = gui.Label(label)
        self.input = gui.Input(input_type, default_value, width=200, height=30, margin='10px')
        
        self.append(self.label, 'label')
        self.append(self.input, 'input')
        
        self.set_value = self.input.set_value
        self.get_value = self.input.get_value
        
        
class DropDownLabel(gui.HBox):
    
    def __init__(self, label='DropDown', items=[''], default='', **kwargs):
        super(DropDownLabel, self).__init__(**kwargs)
        
        self.label = gui.Label(label)
        self.dropdown = gui.DropDown.new_from_list(items, width=200, height=30, margin='10px')
        self.dropdown.select_by_value(default)
        
        self.append(self.label, 'label')
        self.append(self.dropdown, 'dropdown')
        
        self.get_value = self.dropdown.get_value
        self.set_value = self.dropdown.set_value
        
class LongDipoleTrapWidget(gui.Container):
    
    def __init__(self, master, name, **kwargs):
        self.master = master
        self.name = name
        super(LongDipoleTrapWidget, self).__init__(**kwargs)
        
        try:
            self.variables = self.master.config[name]
        except:
            self.master.config[name] = {'axis': 1,
                                        'p0': [3, 500]}
            self.variables = self.master.config[name]
        
        self.axis = DropDownLabel('Axis: ', ['0','1'],'1', width=200, height=20)
        self.s_0 = InputLabel(label='sigma: ',input_type='number', default_value=str(self.variables['p0'][0]))
        self.off_0 = InputLabel(label='offset: ', input_type='number', default_value=str(self.variables['p0'][1]))
        
        self.append(self.axis, 'axis')
        self.append(self.s_0, 's_0')
        self.append(self.off_0, 'off_0')
        
    def update_variables(self):
        self.variables['axis'] = int(self.axis.get_value())
        self.variables['p0'] = [self.s_0.get_value(), self.off_0.get_value()]
        
    def estimate_temperature(self, *args):
        return estimateTemperatureLongDipoletrap(*args,axis=self.variables['axis'], p0 = [float(i) for i in self.variables['p0']])
    
class LongDipoleTrap2DWidget(gui.Container):
    
    def __init__(self, master, name, **kwargs):
        self.master = master
        self.name = name
        super(LongDipoleTrap2DWidget, self).__init__(**kwargs)
        
        try:
            self.variables = self.master.config[name]
        except:
            self.master.config[name] = {'p0':[0,50,10,500]}
            self.variables = self.master.config[name]
        
        
        self.theta = InputLabel(label='theta', input_type='number', default_value=str(self.variables['p0'][0]), width=200, height=30, margin='10px')
        self.sig_x = InputLabel(label='sig_x', input_type='number', default_value=str(self.variables['p0'][1]), width=200, height=30, margin='10px')
        self.sig_y = InputLabel(label='sig_y', input_type='number', default_value=str(self.variables['p0'][2]), width=200, height=30, margin='10px')
        self.offset = InputLabel(label='offset', input_type='number', default_value=str(self.variables['p0'][3]), width=200, height=30, margin='10px')
        
        self.append(self.theta, 'theta')
        self.append(self.sig_x, 'sig_x')
        self.append(self.sig_y, 'sig_y')
        self.append(self.offset, 'offset')
        
    def update_variables(self):
        self.variables['p0'] = [self.theta.get_value(), self.sig_x.get_value(), self.sig_y.get_value(), self.offset.get_value()]
        
    def estimate_temperature(self, *args):
        return estimateTemperature2DGaussian(*args, p0 = [float(i) for i in self.variables['p0']])

    
class DirectoryWidget():
    
    def __init__(self, master, name):
        self.master = master
        self.name = name
        
        try:
            self.variables = self.master.config[name]
        except:
            self.master.config[name] = {    'selected_directories':     ['.'],
                                            'today_dir_check_val':      False}
            self.variables = self.master.config[name]
        
        # Define Menu Items        
        self.settings = gui.MenuItem(name, width=100, height=30)
        self.settings.onclick.do(self.settings_pressed)
        
        
        self.directories = self.variables['selected_directories'][:] # create a copy of list
        
        self.today = str(datetime.date.today())
        year = self.today[0:4]
        month = self.today[5:7]
        day = self.today[8:10]
        self.today_directory = DATA_DIR + '{}/{}/{}/'.format(year, month, day+month+year[2:])
        
        if self.variables['today_dir_check_val']:
            self.directories += [self.today_directory + i for i in os.listdir(self.today_directory)]
        
    def settings_pressed(self, widget):
        self.directory_menu_dialog = gui.GenericDialog(title=self.name + ' Directory Menu', message='Click Ok to transfer content to main page', width='500px')
        
        self.today_dir_check = gui.CheckBox(self.variables['today_dir_check_val'], width=200, height=30, margin='10px')
        self.directory_menu_dialog.add_field_with_label('today_dir_check', 'Use today\'s ({}) folder'.format(str(datetime.date.today())), self.today_dir_check)
        
        self.directory_dialog_btn = gui.Button('Select Directories', width=200, height=30, margin='10px')
        self.directory_dialog_btn.onclick.do(self.directory_dialog_btn_pressed)
        self.directory_menu_dialog.add_field_with_label('directory_dialog_btn', 'Select Directories', self.directory_dialog_btn)
        
        self.directory_menu_dialog.confirm_dialog.do(self.update_directory_menu)
        self.directory_menu_dialog.show(self.master)
        
    def update_directory_menu(self, widget):
        self.variables['today_dir_check_val'] = self.today_dir_check.get_value()
        self.directories = self.variables['selected_directories'][:] # create a copy of list
        
        if self.today_dir_check.get_value():
            if self.today != str(datetime.date.today()):
                self.update_today_directory()
            today_directories = [self.today_directory + i for i in os.listdir(self.today_directory)]
            self.directories += today_directories
            
        print("SELECTED: ", self.variables['selected_directories'])
        print("ALL: ", self.directories)
        
    def update_today_directory(self):      
        self.today = str(datetime.date.today())
        year = self.today[0:4]
        month = self.today[5:7]
        day = self.today[8:10]
        self.today_directory = DATA_DIR + '{}/{}/{}/'.format(year, month, day+month+year[2:])
        
        self.today_dir_check.set_text('Use today\'s ({}) folder'.format(self.today))
    
    def directory_dialog_btn_pressed(self, widget):
        directory_dialog = gui.FileSelectionDialog('Select Directories', 'Select folders', multiple_selection=True, allow_file_selection=False, selection_folder=self.variables['selected_directories'][0])
        directory_dialog.confirm_value.do(self.directory_dialog_confirm)
        directory_dialog.show(self.master)
        
    def directory_dialog_confirm(self, widget, dirlist):
        print(dirlist)
        self.variables['selected_directories'] = dirlist
        #self.update_directories()
        #self.update_filelists()
    
class ProcessingFiles(ProcessingFilesBackEnd):
    
    def __init__(self, master, name):
        super(ProcessingFiles, self).__init__()
        self.master = master
        self.name = name
        self.settings = gui.MenuItem(name, width=100, height=30)
        
        self.directory = DirectoryWidget(self.master, 'Directory')        
        self.AN = AtomNumberWidget(master, 'Atom Number')
        self.T = TemperatureWidget(master, 'Temperature')
        
        self.settings.append([self.directory.settings, self.AN.settings, self.T.settings])
        
        self.running = False
        
    def run(self):
        self.fileLists = []
        for directory in self.directory.directories:
            self.fileLists.append(dict([(i, os.path.getmtime(os.path.join(directory, i))) \
                 for i in os.listdir(directory) if i.endswith('.hid')]))
                
        while(self.running):
            atomroi, refroi = self.master.main_container.get_child('Camera View').get_rois()
            if self.do_processing(self.directory.directories, self.fileLists, atomroi, refroi, AN_func=self.AN.func, T_func=self.T.func):
                self.update_plots()
                
            for i in range(5):
                self.master.progress.set_value(i)
                time.sleep(0.1)
                
            
                    
    def update_plots(self):
        
        if 'Simple Plot' in self.master.config.keys():
            for ID in self.master.config['Simple Plot']:
                sp = self.master.main_container.get_child('Simple Plot ' + ID)
                sp.update_plot()
        
        if '2D Plot' in self.master.config.keys():
            for ID in self.master.config['2D Plot']:
                tdp = self.master.main_container.get_child('2D Plot ' + ID)
                tdp.update_plot()
        
        cv = self.master.main_container.get_child('Camera View')
        cv.update_plot()
        
        AN_T = self.master.main_container.get_child('AN and T')
        AN_T.update_plot()