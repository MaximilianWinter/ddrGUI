# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 16:21:39 2021

@author: mWinter
"""

from remi import gui
from MatplotImage import MatplotImage
import matplotlib.pyplot as plt


class AtomnumberTemperatureWidget(MatplotImage):
    
    def __init__(self, master, name, style={'width': '500', 'height': '200', 'position':'absolute', 'border': '2px solid grey'}, **kwargs):
        self.master = master
        self.name = name        
        
        try:
            self.variables = self.master.config[name]
        except:
            self.master.config[name] = {'visible': True,
                                                  'width': 500,
                                                  'height': 200,
                                                'x': 0,
                                                'y': 680,
                                                }
            self.variables = self.master.config[name]
        
        px = 1/plt.rcParams['figure.dpi']
        style['width'], style['height'] = gui.to_pix(self.variables['width']), gui.to_pix(self.variables['height']) 
        figsize = (self.variables['width']*px, self.variables['height']*px)
        super(AtomnumberTemperatureWidget, self).__init__(figsize=figsize, style=style, **kwargs)
        

        
        # Content
        self.ax = self.fig.add_subplot(1,1,1)
        self.update_plot()
        self.redraw()
        
        # Define Menu Items        
        self.view = gui.MenuItem(self.name, width=100, height=30)
        self.view.onclick.do(self.view_pressed)
        
        # View dialog
        self.view_dialog = gui.GenericDialog(title=self.name, message='Click Ok to transfer content to main page', width='500px')
        
        self.visible = gui.CheckBox(self.variables['visible'], width=200, height=30)
        self.view_dialog.add_field_with_label('visible', 'Visible', self.visible)
        
        self.view_dialog.confirm_dialog.do(self.update_view)
    
    def update_variables(self):
        self.variables['visible'] = self.visible.get_value()
        self.variables['width'] = gui.from_pix(self.style['width'])
        self.variables['height'] = gui.from_pix(self.style['height'])
        self.variables['x'] = gui.from_pix(self.style['left'])
        self.variables['y'] = gui.from_pix(self.style['top'])
        
    def view_pressed(self, widget):
        self.view_dialog.show(self.master)
    
    def update_view(self, widget):
        
        self.update_variables()
        
        if self.variables['visible']:
            self.master.main_container.add_pane(self, self.variables['x'],self.variables['y'], self.name)
        else:
            self.master.main_container.remove_pane(self)
            
        self.update_plot()
        
    def update_plot(self):
        self.ax.clear()
        fontsize = int(5*gui.from_pix(self.style['width'])/plt.rcParams['figure.dpi'])
        try:
            AN = self.master.processingfiles.plot_data['1D']['AN']['data']['y'][-1]
        except:
            AN = 0
        self.ax.text(0,.8, "Atomnumber: {:.2e}".format(AN), fontsize=fontsize)
        
        #self.ax.table([["Atomnumber: {:.2e}".format(AN)]])
        
        try:
            T = self.master.processingfiles.plot_data['1D']['T']['data']['y'][-1]
        except:
            T = 0
        self.ax.text(0,.4, u"Temperature: {:.2f} µK".format(T*1e6), fontsize=fontsize)
        self.ax.axis("off")
        self.redraw()
        
    def update_fig(self):
        px = 1/plt.rcParams['figure.dpi']
        
        figsize = (gui.from_pix(self.style['width'])*px, gui.from_pix(self.style['height'])*px)
        self.fig.set_size_inches(figsize)
        self.update_plot()
        self.redraw()
        print('update fig ', figsize)