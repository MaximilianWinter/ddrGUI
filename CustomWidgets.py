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

    def add_pane(self, pane, x, y):
        pane.style['left'] = gui.to_pix(x)
        pane.style['top'] = gui.to_pix(y)
        pane.onclick.do(self.on_pane_selection)
        pane.style['position'] = 'absolute'
        
        self.append(pane)
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
    
    def __init__(self, master, name):
        
        self.master = master
        self.name = name
        
        # Define Menu Items
        self.settings = gui.MenuItem(name, width=100, height=30)
        self.settings.onclick.do(self.settings_clicked)
        
        self.view = gui.MenuItem(name, width=100, height=30)
        self.view.onclick.do(self.view_clicked)
        
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
    
    def settings_clicked(self, widget):
        self.settings_dialog = gui.GenericDialog(title='Settings Box', message='Click Ok to transfer content to main page', width='500px')
            
        self.dcheck = gui.CheckBox(False, width=200, height=30)
        self.settings_dialog.add_field_with_label('dcheck', 'Label Checkbox', self.dcheck)
        
        self.settings_dialog.confirm_dialog.do(self.update_settings)
        self.settings_dialog.show(self.master)
        
    def update_settings(self, widget=None):
        pass
    
    def view_clicked(self, widget):
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
        

class CameraView(gui.Widget):
    """
    an example for a custom widget class
    """
    
    def __init__(self, master, name, **kwargs):
        super(CameraView, self).__init__(style={'width': '550px', 'height': '550px', 'background-color': 'white', 'position':'absolute', 'border': '2px solid grey'}, **kwargs)
        
        self.master = master
        self.name = name
        
        self.variables = self.master.config[name]
        
        # Define Menu Items        
        self.view = gui.MenuItem(name, width=100, height=30)
        self.view.onclick.do(self.view_clicked)
        
        # Define Container and its content
        self.mpi_roi = MatplotImageROI(self.variables, width = '550px', height = '550px', margin='0px')
        self.mpi_roi.style['background-color'] = 'white'
        
        # add widgets to container
        self.add_child('mpi_roi', self.mpi_roi)
        
        self.children['mpi_roi'].style['position'] = 'absolute'
    
    def view_clicked(self, widget):
        self.view_dialog = gui.GenericDialog(title=self.name + 'View', message='Click Ok to transfer content to main page', width='500px')
        
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
    
    def __init__(self, master, name, figsize=(10,3), style={'width': '1100px', 'height': '300px', 'background-color': 'blue', 'position':'absolute', 'border': '2px solid grey'}, **kwargs):
        super(SimplePlotWidget, self).__init__(style=style, **kwargs)
        self.master = master
        self.name = name
        self.variables = self.master.config[name]
        
        # Define Menu Items        
        self.view = gui.MenuItem(name, width=100, height=30)
        self.view.onclick.do(self.view_clicked)
        
        # Define widget content
        self.mpi = MatplotImage(figsize=figsize, width = style['width'], height = style['height'], margin='0px')
        self.ax = self.mpi.fig.add_subplot(1,1,1)
        self.mpi.redraw()

        # add to main widget
        self.add_child('mpi', self.mpi)
        
        # set children's position
        self.children['mpi'].style['position'] = 'absolute'
    
    def view_clicked(self, widget):
        self.view_dialog = gui.GenericDialog(title=self.name + ' View', message='Click Ok to transfer content to main page', width='500px')
        
        self.mpi_check = gui.CheckBox(self.variables['mpi_check'], width=200, height=30)
        self.view_dialog.add_field_with_label('mpi_check', 'Visible', self.mpi_check)
    
        self.view_dialog.confirm_dialog.do(self.update_view)
        self.view_dialog.show(self.master)
    
    def update_view(self, widget):
        self.variables['mpi_check'] = self.mpi_check.get_value()
        self.variables['x'] = gui.from_pix(self.style['left'])
        self.variables['y'] = gui.from_pix(self.style['top'])
        
        if self.variables['mpi_check']:
            self.master.main_container.add_pane(self, self.variables['x'],self.variables['y'])
        else:
            self.master.main_container.remove_pane(self)
    

class TimelinePlot(gui.Widget):
    
    def __init__(self, master, name, **kwargs):
        super(TimelinePlot, self).__init__(style={'width': '1100px', 'height': '350px', 'background-color': 'blue', 'position':'absolute', 'border': '2px solid grey'}, **kwargs)
        self.master = master
        self.name = name
        self.variables = self.master.config[name]
        
        # Define Menu Items        
        self.view = gui.MenuItem(name, width=100, height=30)
        self.view.onclick.do(self.view_clicked)
        
        # Define widget content
        self.mpi = MatplotImage(figsize=(10,3))
        self.ax_AN = self.mpi.fig.add_subplot(1,1,1)
        self.ax_T = self.ax_AN.twinx()
        self.mpi.redraw()
        
        # add to main widget
        self.add_child('mpi', self.mpi)
        
        # set children's position
        self.children['mpi'].style['position'] = 'absolute'
        
        
    def view_clicked(self, widget):
        pass
        
        