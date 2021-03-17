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
    
class ResizeHelper(gui.Widget, gui.EventSource):
    EVENT_ONDRAG = "on_drag"

    def __init__(self, project, **kwargs):
        super(ResizeHelper, self).__init__(**kwargs)
        gui.EventSource.__init__(self)
        self.style['float'] = 'none'
        self.style['background-color'] = "transparent"
        self.style['border'] = '1px dashed grey'
        self.style['position'] = 'absolute'
        self.style['left']='0px'
        self.style['top']='0px'
        self.project = project
        self.parent = None
        self.refWidget = None
        self.active = False
        self.onmousedown.do(self.start_drag, js_stop_propagation=True, js_prevent_default=True)

        self.origin_x = -1
        self.origin_y = -1
        
    def setup(self, refWidget, newParent):
        #refWidget is the target widget that will be resized
        #newParent is the container
        if self.parent:
            try:
                self.parent.remove_child(self)
            except Exception:
                #there was no ResizeHelper placed
                pass
        if newParent==None:
            return
        self.parent = newParent
        self.refWidget = refWidget
        try:
            self.parent.append(self)
        except Exception:
            #the selected widget's parent can't contain a ResizeHelper
            pass
        #self.refWidget.style['position'] = 'relative'
        self.update_position()
            
    def start_drag(self, emitter, x, y):
        self.active = True
        self.project.onmousemove.do(self.on_drag, js_stop_propagation=True, js_prevent_default=True)
        self.project.onmouseup.do(self.stop_drag)
        self.project.onmouseleave.do(self.stop_drag, 0, 0)
        self.origin_x = -1
        self.origin_y = -1

    def stop_drag(self, emitter, x, y):
        self.active = False
        self.update_position()

    @gui.decorate_event
    def on_drag(self, emitter, x, y):
        if self.active:
            if self.origin_x == -1:
                self.origin_x = float(x)
                self.origin_y = float(y)
                self.refWidget_origin_w = gui.from_pix(self.refWidget.style['width'])
                self.refWidget_origin_h = gui.from_pix(self.refWidget.style['height'])
            else:
                self.refWidget.style['width'] = gui.to_pix(self.refWidget_origin_w + float(x) - self.origin_x )
                self.refWidget.style['height'] = gui.to_pix(self.refWidget_origin_h + float(y) - self.origin_y)
                self.update_position()
            return ()

    def update_position(self):
        self.style['position']='absolute'
        self.style['left']=gui.to_pix(gui.from_pix(self.refWidget.style['left']) + gui.from_pix(self.refWidget.style['width']) - gui.from_pix(self.style['width'])/2)
        self.style['top']=gui.to_pix(gui.from_pix(self.refWidget.style['top']) + gui.from_pix(self.refWidget.style['height']) - gui.from_pix(self.style['height'])/2)



class DragHelper(gui.Widget, gui.EventSource):
    EVENT_ONDRAG = "on_drag"

    def __init__(self, project, **kwargs):
        super(DragHelper, self).__init__(**kwargs)
        gui.EventSource.__init__(self)
        self.style['float'] = 'none'
        self.style['background-color'] = "transparent"
        self.style['border'] = '1px dashed grey'
        self.style['position'] = 'absolute'
        self.style['left']='0px'
        self.style['top']='0px'
        self.project = project
        self.parent = None
        self.refWidget = None
        self.active = False
        self.onmousedown.do(self.start_drag, js_stop_propagation=True, js_prevent_default=True)

        self.origin_x = -1
        self.origin_y = -1
        
    def setup(self, refWidget, newParent):
        #refWidget is the target widget that will be resized
        #newParent is the container
        if self.parent:
            try:
                self.parent.remove_child(self)
            except Exception:
                #there was no ResizeHelper placed
                pass
        if newParent==None:
            return
        self.parent = newParent
        self.refWidget = refWidget
        try:
            self.parent.append(self)
        except Exception:
            #the selected widget's parent can't contain a ResizeHelper
            pass
        #self.refWidget.style['position'] = 'relative'
        self.update_position()
            
    def start_drag(self, emitter, x, y):
        self.active = True
        self.project.onmousemove.do(self.on_drag, js_stop_propagation=True, js_prevent_default=True)
        self.project.onmouseup.do(self.stop_drag)
        self.project.onmouseleave.do(self.stop_drag, 0, 0)
        self.origin_x = -1
        self.origin_y = -1
    
    def stop_drag(self, emitter, x, y):
        self.active = False
        self.update_position()

    @gui.decorate_event
    def on_drag(self, emitter, x, y):
        if self.active:
            if self.origin_x == -1:
                self.origin_x = float(x)
                self.origin_y = float(y)
                self.refWidget_origin_x = gui.from_pix(self.refWidget.style['left'])
                self.refWidget_origin_y = gui.from_pix(self.refWidget.style['top'])
            else:
                self.refWidget.style['left'] = gui.to_pix(self.refWidget_origin_x + float(x) - self.origin_x )
                self.refWidget.style['top'] = gui.to_pix(self.refWidget_origin_y + float(y) - self.origin_y)
                self.update_position()
            return ()

    def update_position(self):
        self.style['position']='absolute'
        self.style['left']=gui.to_pix(gui.from_pix(self.refWidget.style['left']) - gui.from_pix(self.style['width'])/2)
        self.style['top']=gui.to_pix(gui.from_pix(self.refWidget.style['top']) - gui.from_pix(self.style['height'])/2)


class FloatingPanesContainer(gui.Container):

    def __init__(self, **kwargs):
        super(FloatingPanesContainer, self).__init__(**kwargs)
        self.resizeHelper = ResizeHelper(self, width=16, height=16)
        self.dragHelper = DragHelper(self, width=15, height=15)
        self.resizeHelper.on_drag.do(self.on_helper_dragged_update_the_latter_pos, self.dragHelper)
        self.dragHelper.on_drag.do(self.on_helper_dragged_update_the_latter_pos, self.resizeHelper)

        self.style['position'] = 'relative'    
        self.style['overflow'] = 'auto'

        self.append(self.resizeHelper)
        self.append(self.dragHelper)

    def add_pane(self, pane, x, y, key = None): # add key
        pane.style['left'] = gui.to_pix(x)
        pane.style['top'] = gui.to_pix(y)
        pane.onclick.do(self.on_pane_selection)
        pane.style['position'] = 'absolute'
        
        if key is None:
            self.append(pane)
        else:
            self.append(pane, key)
        self.on_pane_selection(pane)
    
    def remove_pane(self, pane):
        self.remove_child(pane)
        self.resizeHelper.setup(None,None)
        self.dragHelper.setup(None,None)

    def on_pane_selection(self, emitter):
        print('on pane selection')
        self.resizeHelper.setup(emitter,self)
        self.dragHelper.setup(emitter,self)
        self.resizeHelper.update_position()
        self.dragHelper.update_position()

    def on_helper_dragged_update_the_latter_pos(self, emitter, widget_to_update):
        widget_to_update.update_position()







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
        self.im = self.ax_im.imshow(self.plot_data, vmin = self.variables['vmin'], vmax = self.variables['vmax'])
        self.cbar.remove()
        self.cbar = plt.colorbar(self.im, ax=self.ax_im)
        self.mpi_im.redraw()
        
    def get_rois(self):
        return self.get_roi_from_panel(self.atomroi), self.get_roi_from_panel(self.refroi)
        
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
        roi[-1] *= -1
        
        return roi
        

class CameraView(gui.Widget):
    """
    an example for a custom widget class
    """
    
    def __init__(self, master, ID, **kwargs):
        super(CameraView, self).__init__(style={'width': '550px', 'height': '550px', 'background-color': 'white', 'position':'absolute', 'border': '2px solid grey'}, **kwargs)
        
        self.master = master
        self.ID = ID
        
        try:
            self.variables = self.master.config['Camera View'][ID]
        except:
            self.master.config['Camera View'][ID] = {'atomroi': {'x': 100, 'y': 100, 'w': 100, 'h': 100},
                                                     'refroi': {'x': 200, 'y': 100, 'w': 100, 'h': 100},
                                                     'mpi_check': True,
                                                     'x': 0,
                                                     'y': 30,
                                                     'vmin': 0,
                                                     'vmax': 1}
            
            self.variables = self.master.config['Camera View'][ID]
        
        # Define Menu Items        
        self.view = gui.MenuItem('Camera View ' + str(ID), width=100, height=30)
        self.view.onclick.do(self.view_pressed)
        
        # Define Container and its content
        self.mpi_roi = MatplotImageROI(self.variables, width = '550px', height = '550px', margin='0px')
        self.mpi_roi.style['background-color'] = 'white'
        
        # add widgets to container
        self.add_child('mpi_roi', self.mpi_roi)
        
        self.children['mpi_roi'].style['position'] = 'absolute'
    
    def view_pressed(self, widget):
        self.view_dialog = gui.GenericDialog(title='Camera View' + str(self.ID), message='Click Ok to transfer content to main page', width='500px')
        
        self.mpi_check = gui.CheckBox(self.variables['mpi_check'], width=200, height=30)
        self.view_dialog.add_field_with_label('mpi_check', 'Visible', self.mpi_check)
        
        self.vmin_spinbox = gui.SpinBox(default_value=self.variables['vmin'], min_value=0, max_value=1, step=0.05, width=200, height=20)
        self.view_dialog.add_field_with_label('vmin_spinbox', 'Vmin', self.vmin_spinbox)
        
        self.vmax_spinbox = gui.SpinBox(default_value=self.variables['vmax'], min_value=0, max_value=1, step=0.05, width=200, height=20)
        self.view_dialog.add_field_with_label('vmax_spinbox', 'Vmax', self.vmax_spinbox)

        self.view_dialog.confirm_dialog.do(self.update_view)
        self.view_dialog.show(self.master)
        
    def update_view(self, widget):
        self.variables['mpi_check'] = self.mpi_check.get_value()
        self.variables['x'] = gui.from_pix(self.style['left'])
        self.variables['y'] = gui.from_pix(self.style['top'])
        
        self.variables['vmin'] = self.vmin_spinbox.get_value()
        self.variables['vmax'] = self.vmax_spinbox.get_value()
        
        self.mpi_roi.update_plot()
        
        if self.variables['mpi_check']:
            self.master.main_container.add_pane(self, self.variables['x'],self.variables['y'])
        else:
            self.master.main_container.remove_pane(self)
        
class SimplePlotWidget(gui.Widget):
    
    def __init__(self, master, ID, figsize=(10,3), style={'width': '1100px', 'height': '300px', 'background-color': 'blue', 'position':'absolute', 'border': '2px solid grey'}, **kwargs):
        super(SimplePlotWidget, self).__init__(style=style, **kwargs)
        self.master = master
        self.ID = ID
        
        try:
            self.variables = self.master.config['Simple Plot'][ID]
        except:
            self.master.config['Simple Plot'][ID] = {'mpi_check': True,
                                                    'x': 0,
                                                    'y': 680,
                                                    'xmin':0,
                                                    'xmax':1,
                                                    'ymin':0,
                                                    'ymax':1}
            self.variables = self.master.config['Simple Plot'][ID]
        
        # Define Menu Items        
        self.view = gui.MenuItem('Simple Plot ' + str(ID), width=100, height=30)
        self.view.onclick.do(self.view_pressed)
        
        # Define widget contentpyt
        self.mpi = MatplotImage(figsize=figsize, width = style['width'], height = style['height'], margin='0px')
        self.ax = self.mpi.fig.add_subplot(1,1,1)
        self.mpi.redraw()

        # add to main widget
        self.add_child('mpi', self.mpi)
        
        # set children's position
        self.children['mpi'].style['position'] = 'absolute'
    
    def view_pressed(self, widget):
        self.view_dialog = gui.GenericDialog(title='Simple Plot ' + str(self.ID), message='Click Ok to transfer content to main page', width='500px')
        
        self.mpi_check = gui.CheckBox(self.variables['mpi_check'], width=200, height=30)
        self.view_dialog.add_field_with_label('mpi_check', 'Visible', self.mpi_check)
        
        self.xmin_spinbox = gui.SpinBox(default_value=self.variables['xmin'], min_value=0, max_value=2**16-1, step=1, width=200, height=20)
        self.view_dialog.add_field_with_label('xmin_spinbox', 'xmin', self.xmin_spinbox)
    
        self.xmax_spinbox = gui.SpinBox(default_value=self.variables['xmax'], min_value=0, max_value=2**16-1, step=1, width=200, height=20)
        self.view_dialog.add_field_with_label('xmax_spinbox', 'xmin', self.xmax_spinbox)
        
        self.ymin_spinbox = gui.SpinBox(default_value=self.variables['ymin'], min_value=0, max_value=2**16-1, step=1, width=200, height=20)
        self.view_dialog.add_field_with_label('ymin_spinbox', 'ymin', self.ymin_spinbox)
    
        self.ymax_spinbox = gui.SpinBox(default_value=self.variables['ymax'], min_value=0, max_value=2**16-1, step=1, width=200, height=20)
        self.view_dialog.add_field_with_label('ymax_spinbox', 'ymin', self.ymax_spinbox)
        
        self.clear_btn = gui.Button('Clear Data', width=200, height=30, margin='10px')
        self.view_dialog.add_field_with_label('clear_btn', 'Clear Data', self.clear_btn)
        self.clear_btn.onclick.do(self.clear_btn_pressed)
        
        self.remove_check = gui.CheckBox(False, width=200, height=30)
        self.view_dialog.add_field_with_label('remove_check', 'Remove Instance', self.remove_check)
        
        self.view_dialog.confirm_dialog.do(self.update_view)
        self.view_dialog.show(self.master)
    
    def update_view(self, widget):
        if self.remove_check.get_value():
            self.master.main_container.remove_pane(self)
            self.master.view.sub_container.remove_child(self.view)
            del self.master.config['Simple Plot'][self.ID]
            return
        
        self.variables['mpi_check'] = self.mpi_check.get_value()
        self.variables['x'] = gui.from_pix(self.style['left'])
        self.variables['y'] = gui.from_pix(self.style['top'])
        self.variables['xmin'] = self.xmin_spinbox.get_value()
        self.variables['xmax'] = self.xmax_spinbox.get_value()
        self.variables['ymin'] = self.ymin_spinbox.get_value()
        self.variables['ymax'] = self.ymax_spinbox.get_value()
        
        if self.variables['mpi_check']:
            self.master.main_container.add_pane(self, self.variables['x'],self.variables['y'])
        else:
            self.master.main_container.remove_pane(self)
            
        self.ax.clear()
        self.ax.set_xlim(self.variables['xmin'], self.variables['xmax'])
        self.ax.set_ylim(self.variables['ymin'], self.variables['ymax'])
        self.mpi.redraw()
    
    def clear_btn_pressed(self, widget):
        self.plot_data = []
        self.ax.clear()
        self.mpi.redraw()
        
DATA_DIR = '.'
class ProcessingFiles(ProcessingFilesBackEnd):
    
    def __init__(self, master, name):
        super(ProcessingFiles, self).__init__()
        self.master = master
        self.name = name
        self.variables = self.master.config[name]
        self.settings = gui.MenuItem(name, width=100, height=30)
        
        self.directory = DirectoryWidget(self.master, 'Directory')        
        self.fits = FitsWidget(self.master, 'Fits')
        self.settings.append([self.directory.settings, self.fits.settings])
        
        self.AN = AtomNumberWidget()
        self.T = TemperatureWidget()
        
        self.running = False
        
    def run(self):
        self.fileLists = []
        for directory in self.directory.directories:
            self.fileLists.append(dict([(i, os.path.getmtime(os.path.join(directory, i))) \
                 for i in os.listdir(directory) if i.endswith('.hid')]))
                
        while(self.running):
            atomroi, refroi = self.master.main_container.get_child('Camera View').mpi_roi.get_rois()
            self.do_processing(self.directory.directories, self.fileLists, atomroi, refroi, AN_func=self.AN.func, T_func=self.T.func)
            
                    
    def update_plots(self):
        for ID in self.master.config['Camera View']:
                cv = self.master.main_container.get_child('Camera View ' + str(ID))
                cv.mpi_roi.update_plot()
        
        for ID in self.master.config['Simple Plot']:
                sp = self.master.main_container.get_child('Simple Plot ' + str(ID))
                sp.update_plot()
                
class AtomNumberWidget():
    
    def __init__(self):
        pass
    
class TemperatureWidget():
    
    def __init__(self):
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
    

class TimelinePlot(gui.Widget):
    
    def __init__(self, master, name, **kwargs):
        super(TimelinePlot, self).__init__(style={'width': '1100px', 'height': '350px', 'background-color': 'blue', 'position':'absolute', 'border': '2px solid grey'}, **kwargs)
        self.master = master
        self.name = name
        self.variables = self.master.config[name]
        
        # Define Menu Items        
        self.view = gui.MenuItem(name, width=100, height=30)
        self.view.onclick.do(self.view_pressed)
        
        # Define widget content
        self.mpi = MatplotImage(figsize=(10,3))
        self.ax_AN = self.mpi.fig.add_subplot(1,1,1)
        self.ax_T = self.ax_AN.twinx()
        self.mpi.redraw()
        
        # add to main widget
        self.add_child('mpi', self.mpi)
        
        # set children's position
        self.children['mpi'].style['position'] = 'absolute'
        
        
    def view_pressed(self, widget):
        pass
        
        