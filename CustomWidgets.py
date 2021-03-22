# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 15:22:06 2021

@author: mWinter

winter.maximilian (at) physik.lmu.de
or
mwinter (at) mpq.mpg.de
"""

from remi import gui
from MatplotImage import MatplotImage
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os
from backend import ProcessingFilesBackEnd
from utils import getAtomNumber, estimateTemperatureLongDipoletrap
from FloatingPanesContainer import FloatingPanesContainer
import time

class GenericWidgetClass():
    """Note: any variable that should be stored in a config file is accessed via the variable dict"""
    
    def __init__(self, master, name):
        
        self.master = master
        self.name = name
        
        # Define Menu Items
        self.settings = gui.MenuItem(name, width=100, height=30)
        self.settings.onclick.do(self.settings_pressed)
        
        self.view = gui.MenuItem(name, width=100, height=30)
        self.view.onclick.do(self.view_pressed)
        
        # Define Container and its content
        self.container = gui.Container(style={'width': '220px', 'display': 'block', 'overflow': 'auto', 'text-align': 'center'})
        
        
        self.progress = gui.Progress(1, 100, width=200, height=5)
        self.container.append(self.progress, 'progress')
        
        # load variable dict from config
        # then do update settings
        # and update view
        #self.variables = {'progress': self.progress}
        
        #for key in self.master.config[name]['view']:
        #    self.container.append(self.widgets[key], key)
    
    def settings_pressed(self, widget):
        self.settings_dialog = gui.GenericDialog(title='Settings Box', message='Click Ok to transfer content to main page', width='500px')
            
        self.dcheck = gui.CheckBox(False, width=200, height=30)
        self.settings_dialog.add_field_with_label('dcheck', 'Label Checkbox', self.dcheck)
        
        self.settings_dialog.confirm_dialog.do(self.update_settings)
        self.settings_dialog.show(self.master)
        
    def update_settings(self, widget=None):
        pass
    
    def view_pressed(self, widget):
        self.view_dialog = gui.GenericDialog(title='View Box', message='Click Ok to transfer content to main page', width='500px')
            
        self.view_check = gui.CheckBox(True, width=200, height=30)
        self.view_dialog.add_field_with_label('dcheck', 'Label Checkbox', self.view_check)
        
        self.view_dialog.confirm_dialog.do(self.update_view)
        self.view_dialog.show(self.master)
    
    def update_view(self, widget=None):
        if not self.view_check.get_value():
            self.container.remove_child(self.progress)
        else:
            self.container.add_child('progress', self.progress)
            
class MatplotImageROI(FloatingPanesContainer):
    """
    MatplotImage widget with two ROIS
    
    """
    
    def __init__(self, variables, **kwargs):
        super(MatplotImageROI, self).__init__(**kwargs)
        self.variables = variables
    
        self.atomroi = gui.Container(width=self.variables['atomroi']['w'], height=self.variables['atomroi']['h'])
        self.atomroi.style['background-color'] = 'transparent'
        self.atomroi.style['border'] = '2px solid white'
        
        self.refroi = gui.Container(width=self.variables['refroi']['w'], height=self.variables['refroi']['h'])
        self.refroi.style['background-color'] = 'transparent'
        self.refroi.style['border'] = '2px dotted white'
        
        self.mpi_im = MatplotImage(figsize=(7.5,7.5))
        self.ax_im = self.mpi_im.fig.add_subplot(1,1,1)
        self.plot_data = np.zeros((512,512))
        self.im = self.ax_im.imshow(self.plot_data, vmin = self.variables['vmin'], vmax = self.variables['vmax'])
        self.cbar = plt.colorbar(self.im, ax=self.ax_im)
        self.mpi_im.redraw()
        self.add_pane(self.atomroi, self.variables['atomroi']['x'], self.variables['atomroi']['y'])
        self.add_pane(self.refroi, self.variables['refroi']['x'], self.variables['refroi']['y'])
        self.append(self.mpi_im)
        
    def update_plot(self):
        # make stable for empty plot_data['data']
        self.im = self.ax_im.imshow(self.plot_data['data'][0], vmin = self.variables['vmin'], vmax = self.variables['vmax'])
        self.cbar.remove()
        self.cbar = plt.colorbar(self.im, ax=self.ax_im)
        self.mpi_im.redraw()
        
    def get_rois(self, as_dict=False):
        if as_dict:
            x, y, w, h = self.get_roi_from_panel(self.atomroi)
            atomroi = {'x': x, 'y': y, 'w': w, 'h': h}
            
            x, y, w, h = self.get_roi_from_panel(self.refroi)
            refroi = {'x': x, 'y': y, 'w': w, 'h': h}
            
            return atomroi, refroi
        else:
            return self.get_roi_from_panel(self.atomroi), self.get_roi_from_panel(self.refroi)
    def get_rois_px(self, as_dict=False):
        
        atomroi = {'x': gui.from_pix(self.atomroi.style['left']),
                    'y': gui.from_pix(self.atomroi.style['top']),
                    'w': gui.from_pix(self.atomroi.style['width']),
                    'h': gui.from_pix(self.atomroi.style['height'])}
        
        refroi = {'x': gui.from_pix(self.refroi.style['left']),
                    'y': gui.from_pix(self.refroi.style['top']),
                    'w': gui.from_pix(self.refroi.style['width']),
                    'h': gui.from_pix(self.refroi.style['height'])}
        
        if as_dict:
            return atomroi, refroi
        else:
            return atomroi.values(), refroi.values()
        

    def get_roi_from_panel(self, panel):
        """
        works if ax is used with imshow
        
        returns x, y, w, h (all ints, in data coordinates)
        
        :                +------------------+
        :                |                  |
        :              height               |
        :                |                  |
        :               (xy)---- width -----+
        
        """
        
        fig_w, fig_h = self.mpi_im.fig.canvas.get_width_height()
        
        w, h = gui.from_pix(panel.style['width']), gui.from_pix(panel.style['height'])
        x, y = gui.from_pix(panel.style['left']), fig_h - (gui.from_pix(panel.style['top']) + h)
        
        x0, y0 = self.ax_im.transData.transform((0, 0))
        inv = self.ax_im.transData.inverted()
        
        roi = [int(i) for i in inv.transform([x, y, w+x0, h+y0])]
        roi[1] = roi[1]+roi[-1] # TODO: more elegant solution
        roi[-1] *= -1
        
        return roi
        

class CameraView(MatplotImageROI):
    """
    an example for a custom widget class
    """
    
    def __init__(self, master, name, **kwargs):        
        self.master = master
        self.name = name
        
        try:
            self.variables = self.master.config[self.name]
        except:
            self.master.config[self.name] = {'atomroi': {'x': 100, 'y': 100, 'w': 100, 'h': 100},
                                                     'refroi': {'x': 200, 'y': 100, 'w': 100, 'h': 100},
                                                     'mpi_check': True,
                                                     'width': 550,
                                                     'height': 550,
                                                     'x': 0,
                                                     'y': 30,
                                                     'vmin': 0,
                                                     'vmax': 1}
            
            self.variables = self.master.config[self.name]
        
        super(CameraView, self).__init__(variables=self.variables, style={'width': gui.to_pix(self.variables['width']), 'height': gui.to_pix(self.variables['height']), 'position':'absolute', 'border': '2px solid grey'}, **kwargs)
        
        # Define Menu Items        
        self.view = gui.MenuItem(self.name, width=100, height=30)
        self.view.onclick.do(self.view_pressed)
    
        self.view_dialog = gui.GenericDialog(title=self.name, message='Click Ok to transfer content to main page', width='500px')
        
        self.mpi_check = gui.CheckBox(self.variables['mpi_check'], width=200, height=30)
        self.view_dialog.add_field_with_label('mpi_check', 'Visible', self.mpi_check)
        
        self.vmin_spinbox = gui.SpinBox(default_value=self.variables['vmin'], min_value=0, max_value=1, step=0.05, width=200, height=20)
        self.view_dialog.add_field_with_label('vmin_spinbox', 'Vmin', self.vmin_spinbox)
        
        self.vmax_spinbox = gui.SpinBox(default_value=self.variables['vmax'], min_value=0, max_value=1, step=0.05, width=200, height=20)
        self.view_dialog.add_field_with_label('vmax_spinbox', 'Vmax', self.vmax_spinbox)

        self.view_dialog.confirm_dialog.do(self.update_view)
        
        self.plot_data = self.master.processingfiles.plot_data['OD']
        
    def view_pressed(self, widget):
        
        self.view_dialog.show(self.master)
        
    def update_view(self, widget):
        self.update_variables()
        
        self.update_plot()
        
        if self.variables['mpi_check']:
            self.master.main_container.add_pane(self, self.variables['x'],self.variables['y'], 'Camera View')
        else:
            self.master.main_container.remove_pane(self)
            
    def update_variables(self):
        self.variables['atomroi'], self.variables['refroi'] = self.get_rois_px(as_dict=True)
        self.variables['mpi_check'] = self.mpi_check.get_value()
        self.variables['width'] = gui.from_pix(self.style['width'])
        self.variables['height'] = gui.from_pix(self.style['height'])
        self.variables['x'] = gui.from_pix(self.style['left'])
        self.variables['y'] = gui.from_pix(self.style['top'])
        
        self.variables['vmin'] = self.vmin_spinbox.get_value()
        self.variables['vmax'] = self.vmax_spinbox.get_value()
        
    #def update_plot(self):
        #self.ax_im.clear()
        #self.ax_im.imshow(self.plot_data['data'][0], vmin=self.variables['vmin'], vmax=self.variables['vmax'])
        #self.mpi_im.redraw()
        
class SimplePlotWidget(MatplotImage):
    
    def __init__(self, master, ID, figsize=(10,3), style={'position':'absolute', 'border': '2px solid grey'}, **kwargs):
        self.master = master
        self.ID = ID
        
        try:
            self.variables = self.master.config['Simple Plot'][ID]
        except:
            self.master.config['Simple Plot'][ID] = {'mpi_check': True,
                                                 'width': 1200,
                                                 'height': 300,
                                                'x': 0,
                                                'y': 680,
                                                'xlim_check': True,
                                                'xlim':(0,1),
                                                'ylim_check': True,
                                                'ylim':(0,1),
                                                'plotdata_dropdown': 'AN',
                                                'color': 'blue',
                                                 'linestyle': '-'}
            self.variables = self.master.config['Simple Plot'][ID]
        
        px = 1/plt.rcParams['figure.dpi']
        style['width'], style['height'] = gui.to_pix(self.variables['width']), gui.to_pix(self.variables['height']) 
        figsize = (self.variables['width']*px, self.variables['height']*px)
        super(SimplePlotWidget, self).__init__(figsize=figsize, style=style, **kwargs)
        
        # Define Menu Items        
        self.view = gui.MenuItem('Simple Plot ' + str(ID), width=100, height=30)
        self.view.onclick.do(self.view_pressed)
        
        # Define widget contentpyt
        self.ax = self.fig.add_subplot(1,1,1)
        self.redraw()
        
        self.plot_data = self.master.processingfiles.plot_data[self.variables['plotdata_dropdown']]
    
        self.view_dialog = gui.GenericDialog(title='Simple Plot ' + str(self.ID), message='Click Ok to transfer content to main page', width='500px')
        
        self.mpi_check = gui.CheckBox(self.variables['mpi_check'], width=200, height=30)
        self.view_dialog.add_field_with_label('mpi_check', 'Visible', self.mpi_check)
        
        self.xlim_check = gui.CheckBox(self.variables['xlim_check'], width=200, height=30)
        self.view_dialog.add_field_with_label('xlim_check', 'xlim auto', self.xlim_check)
        
        self.xlim_text = gui.TextInput(width=200, height=30, margin='10px')
        self.xlim_text.set_text(str(self.variables['xlim'])[1:-1])
        self.view_dialog.add_field_with_label('xlim_text', 'xlim (sep. by comma)', self.xlim_text)

        self.ylim_check = gui.CheckBox(self.variables['ylim_check'], width=200, height=30)
        self.view_dialog.add_field_with_label('ylim_check', 'ylim auto', self.ylim_check)
        
        self.ylim_text = gui.TextInput(width=200, height=30, margin='10px')
        self.ylim_text.set_text(str(self.variables['ylim'])[1:-1])
        self.view_dialog.add_field_with_label('ylim_text', 'ylim (sep. by comma)', self.ylim_text)
        
        self.clear_btn = gui.Button('Clear Data', width=200, height=30, margin='10px')
        self.view_dialog.add_field_with_label('clear_btn', 'Clear Data', self.clear_btn)
        self.clear_btn.onclick.do(self.clear_btn_pressed)
        
        self.remove_check = gui.CheckBox(False, width=200, height=30)
        self.view_dialog.add_field_with_label('remove_check', 'Remove Instance', self.remove_check)
        
        self.update_fig_btn = gui.Button('Update Figure', width=200, height=30, margin='10px')
        self.view_dialog.add_field_with_label('update_fig_btn', 'Update Figure', self.update_fig_btn)
        self.update_fig_btn.onclick.do(self.update_fig_btn_pressed)
        
        self.colorpicker = gui.ColorPicker(self.variables['color'], width=200, height=20, margin='10px')
        self.view_dialog.add_field_with_label('colorpicker', 'Color', self.colorpicker)
        
        self.linestyle_dropdown = gui.DropDown.new_from_list(['-', '--', '-.', '.', '.-'], width=200, height=20)
        self.linestyle_dropdown.select_by_value(self.variables['linestyle'])
        self.view_dialog.add_field_with_label('linestyle_dropdown', 'Choose linestyle', self.linestyle_dropdown)
        
        self.plotdata_dropdown = gui.DropDown.new_from_list(self.master.processingfiles.plot_data.keys(), width=200, height=20)
        self.plotdata_dropdown.select_by_value(self.variables['plotdata_dropdown'])
        self.plotdata_dropdown.onchange.do(self.plotdata_dropdown_changed)
        self.view_dialog.add_field_with_label('plotdata_dropdown', 'Choose plotdata source', self.plotdata_dropdown)
        
        #self.add_plotdata_btn = gui.Button('Add plotdata source', width=200, height=30, margin='10px')
        #self.view_dialog.add_field_with_label('add_plotdata_btn', 'Add plotdata source', self.add_plotdata_btn)
        #self.add_plotdata_btn.onclick.do(self.add_plotdata_btn_pressed)
        
        self.view_dialog.confirm_dialog.do(self.update_view)
        
    ##def add_plotdata_btn_pressed(self, widget):
        
        
    def view_pressed(self, widget):
        self.view_dialog.show(self.master)
        
    def plotdata_dropdown_changed(self, widget, new_selection):
        self.plot_data = self.master.processingfiles.plot_data[new_selection]
        self.update_plot()
        
    def update_plot(self):
        self.ax.clear()
        
        # TODO: fix to make generic
        if self.plotdata_dropdown.get_value() == 'fit':
            self.ax.plot(self.plot_data['data'][1], self.plot_data['data'][-1], self.variables['linestyle'], color=self.variables['color'])
            self.ax.plot(self.plot_data['data'][0], '.', color='black')
        else:
            self.ax.plot(self.plot_data['data'], self.variables['linestyle'], color=self.variables['color'])
        self.ax.set_ylabel(self.plot_data['ylabel'])
        if not self.variables['xlim_check']:
            self.ax.set_xlim(*self.variables['xlim'])
        if not self.variables['ylim_check']:
            self.ax.set_ylim(*self.variables['ylim'])
        self.redraw()                          
    
    def update_view(self, widget):
        if self.remove_check.get_value():
            self.master.main_container.remove_pane(self)
            self.master.view.sub_container.remove_child(self.view)
            del self.master.config['Simple Plot'][self.ID]
            return
        
        self.update_variables()
        
        if self.variables['mpi_check']:
            self.master.main_container.add_pane(self, self.variables['x'],self.variables['y'], 'Simple Plot ' + str(self.ID))
        else:
            self.master.main_container.remove_pane(self)
            
        self.update_plot()
        #self.ax.set_xlim(self.variables['xmin'], self.variables['xmax'])
        #self.ax.set_ylim(self.variables['ymin'], self.variables['ymax'])
        
    def update_variables(self):
        self.variables['mpi_check'] = self.mpi_check.get_value()
        self.variables['width'] = gui.from_pix(self.style['width'])
        self.variables['height'] = gui.from_pix(self.style['height'])
        self.variables['x'] = gui.from_pix(self.style['left'])
        self.variables['y'] = gui.from_pix(self.style['top'])
        self.variables['xlim_check'] = self.xlim_check.get_value()
        self.variables['xlim'] = tuple(map(float, self.xlim_text.get_value().split(',')))
        self.variables['ylim_check'] = self.ylim_check.get_value()
        self.variables['ylim'] = tuple(map(float, self.ylim_text.get_value().split(',')))
        self.variables['color'] = self.colorpicker.get_value()
        self.variables['linestyle'] = self.linestyle_dropdown.get_value()
        self.variables['plotdata_dropdown'] = self.plotdata_dropdown.get_value()
    
    def clear_btn_pressed(self, widget):
        #self.plot_data = []
        self.ax.clear()
        self.redraw()
        
    def update_fig_btn_pressed(self, widget):
        
        px = 1/plt.rcParams['figure.dpi']
        
        figsize = (gui.from_pix(self.style['width'])*px, gui.from_pix(self.style['height'])*px)
        self.fig.set_size_inches(figsize)
        print('new figsize ', figsize)
        self.update_plot()
        
DATA_DIR = '.'
class ProcessingFiles(ProcessingFilesBackEnd):
    
    def __init__(self, master, name):
        super(ProcessingFiles, self).__init__()
        self.master = master
        self.name = name
        self.variables = self.master.config[name]
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
            time.sleep(0.5)
            print(atomroi, refroi)
            
                    
    def update_plots(self):
        #for ID in self.master.config['Camera View']:
        #        cv = self.master.main_container.get_child('Camera View ' + str(ID))
        #        cv.mpi_roi.update_plot()
        
        for ID in self.master.config['Simple Plot']:
                sp = self.master.main_container.get_child('Simple Plot ' + str(ID))
                sp.update_plot()
        
        cv = self.master.main_container.get_child('Camera View')
        cv.update_plot()
                
class AtomNumberWidget():
    
    def __init__(self, master, name):
        self.master = master
        self.name = name
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
        self.variables = self.master.config[name]
        
        # Define Menu Items
        self.settings = gui.MenuItem(name, width=100, height=30)
        self.settings.onclick.do(self.settings_pressed)
        
        self.available_T_funcs = {'Long Dipole Trap' : estimateTemperatureLongDipoletrap}
        self.func = self.available_T_funcs[self.variables['T_dropdown']]
    
    def settings_pressed(self, widget):
        self.T_menu_dialog = gui.GenericDialog(title=self.name + ' Menu', message='Click Ok to transfer content to main page', width='500px')
        
        self.T_dropdown = gui.DropDown.new_from_list(self.available_T_funcs.keys(),
                                                    width=200, height=20)
        self.T_dropdown.select_by_value(self.variables['T_dropdown'])
        self.T_dropdown.onchange.do(self.T_dropdown_changed)
        self.T_menu_dialog.add_field_with_label('T_dropdown', 'Choose T function', self.T_dropdown)
        
        self.T_menu_dialog.confirm_dialog.do(self.update_T_menu)
        self.T_menu_dialog.show(self.master)
        
    def update_T_menu(self, widget):
        self.variables['T_dropdown'] = self.T_dropdown.get_value()
        
        self.func = self.available_T_funcs[self.T_dropdown.get_value()]
    
    def T_dropdown_changed(self, widget, chosen_T):
        pass

class FitsWidget():
    
    def __init__(self, master, name):
        self.master = master
        self.name = name
        self.variables = self.master.config[name]
        
        # Define Menu Items        
        self.settings = gui.MenuItem(name, width=100, height=30)
        self.settings.onclick.do(self.settings_pressed)
        
        self.oneDgauss = OneDGaussFit(self.master, '1D Gaussian')
        self.twoDgauss = TwoDGaussFit(self.master, '2D Gaussian')
        
        self.available_fits = {'1D Gaussian': self.oneDgauss, '2D Gaussian': self.twoDgauss}
    
    def settings_pressed(self, widget):
        self.fits_menu_dialog = gui.GenericDialog(title=self.name + ' Menu', message='Click Ok to transfer content to main page', width='500px')
        
        self.fits_dropdown = gui.DropDown.new_from_list(self.available_fits.keys(),
                                                    width=200, height=20)
        self.fits_dropdown.onchange.do(self.fits_dropdown_changed)
        self.fits_menu_dialog.add_field_with_label('fits_dropdown', 'Choose Fit', self.fits_dropdown)
        
        self.fits_menu_dialog.confirm_dialog.do(self.update_fits_menu)
        self.fits_menu_dialog.show(self.master)
        
    def update_fits_menu(self, widget):
        pass
    
    def fits_dropdown_changed(self, widget, chosen_fit):
        print('changed to' + chosen_fit)
        for key, fit in self.available_fits.items():
            self.fits_menu_dialog.container.remove_child(fit)
        self.fits_menu_dialog.container.add_child(chosen_fit, self.available_fits[chosen_fit])
        
class TwoDGaussFit(gui.Widget):
    
    def __init__(self, master, name, **kwargs):
        super(TwoDGaussFit, self).__init__(style={'width': '500px', 'height': '550px', 'background-color': 'white', 'position':'absolute', 'border': '2px solid grey'}, **kwargs)
        self.master = master
        self.name = name
        self.variables = self.master.config[name]
        
        self.label = gui.Label(name)
        
        self.symmetric_check = gui.CheckBoxLabel('Symmetric', self.variables['symmetric_check'], width=200, height=30)
        
        self.axes_aligned_check = gui.CheckBoxLabel('Axes aligned', self.variables['axes_aligned_check'], width=200, height=30)
        self.add_child('label', self.label)
        self.add_child('symmetric_check', self.symmetric_check) 
        self.add_child('axes_aligned_check', self.axes_aligned_check)
        
        
        self.style['top'] = '150px'
    
    def fit_func_full(self, data, A, x0, y0, theta, sig_x, sig_y, off):
        x = data[0]
        y = data[1]
        a = np.cos(theta)**2/(2*sig_x**2) + np.sin(theta)**2/(2*sig_y**2)
        b = -np.sin(2*theta)/(4*sig_x**2) + np.sin(2*theta)/(4*sig_y**2)
        c = np.sin(theta)**2/(2*sig_x**2) + np.cos(theta)**2/(2*sig_y**2)
        return A*np.exp(-(a*(x-x0)**2 + 2*b*(x-x0)*(y-y0) + c*(y-y0)**2)) + off
    
    def update_params(self):
        pass
    #def fit_func_
        
    #def do_fit(self, data)
    
class OneDGaussFit(gui.Widget):
    
    def __init__(self, master, name, **kwargs):
        super(OneDGaussFit, self).__init__(style={'width': '500px', 'height': '550px', 'background-color': 'white', 'position':'absolute', 'border': '2px solid grey'}, **kwargs)
        self.master = master
        self.name = name
        self.variables = self.master.config[name]
        
        self.style['top'] = '150px'
        
    def fit_func_full(self, data, A, x0, y0, theta, sig_x, sig_y, off):
        x = data[0]
        y = data[1]
        a = np.cos(theta)**2/(2*sig_x**2) + np.sin(theta)**2/(2*sig_y**2)
        b = -np.sin(2*theta)/(4*sig_x**2) + np.sin(2*theta)/(4*sig_y**2)
        c = np.sin(theta)**2/(2*sig_x**2) + np.cos(theta)**2/(2*sig_y**2)
        return A*np.exp(-(a*(x-x0)**2 + 2*b*(x-x0)*(y-y0) + c*(y-y0)**2)) + off
    
    
class DirectoryWidget():
    
    def __init__(self, master, name):
        self.master = master
        self.name = name
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
        
class PlotData():
    """Class for storing plot data."""
    def __init__(self, is_2d = False):
        self.is_2d=is_2d
        if is_2d: 
            self.data = None
        else:
            self.data = []
        