# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 16:18:23 2021

@author: mWinter
"""

from remi import gui
from MatplotImage import MatplotImage
import numpy as np
import matplotlib.pyplot as plt
from FloatingPanesContainer import FloatingPanesContainer

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
        
        self.mpi_im = MatplotImage(**kwargs)
        self.mpi_im.update_fig()
        self.ax_im = self.mpi_im.fig.add_subplot(1,1,1)
        self.plot_data = np.zeros((512,512))
        self.im = self.ax_im.imshow(self.plot_data, vmin = self.variables['vmin'], vmax = self.variables['vmax'])
        self.cbar = plt.colorbar(self.im, ax=self.ax_im)
        self.mpi_im.redraw()
        self.append(self.mpi_im)
        self.add_pane(self.atomroi, self.variables['atomroi']['x'], self.variables['atomroi']['y'])
        self.add_pane(self.refroi, self.variables['refroi']['x'], self.variables['refroi']['y'])
        
        
    def update_plot(self):
        # make stable for empty plot_data['data']
        self.im = self.ax_im.imshow(self.plot_data['data'][0], vmin = self.variables['vmin'], vmax = self.variables['vmax'])
        self.cbar.remove()
        self.cbar = plt.colorbar(self.im, ax=self.ax_im)
        self.ax_im.set_title(self.plot_data['path'],fontsize=7,pad=12)
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
        
        self.plot_data = self.master.processingfiles.plot_data['2D']['OD']
        
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
        
    def update_fig(self):
        self.mpi_im.style['width'] = self.style['width']
        self.mpi_im.style['height'] = self.style['height']                                      
        self.mpi_im.update_fig()
        
    # def unselect_panes(self): # tried to improve dragging and scaling of camview after rois are selected
    #     print('unselect panes')
    #     self.update_pane(self.atomroi)
    #     self.update_pane(self.refroi)
