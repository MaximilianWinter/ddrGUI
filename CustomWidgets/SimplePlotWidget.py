# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 16:20:15 2021

@author: mWinter
"""

from remi import gui
from MatplotImage import MatplotImage
import matplotlib.pyplot as plt


class LinePlotDataTabbox(gui.TabBox):
    
    def __init__(self, master, variables, style={'align-content':'center', 'width': '80%','margin':'auto'}, **kwargs):
        super(LinePlotDataTabbox, self).__init__(style=style, **kwargs)
        self.master = master
        self.variables = variables
        
        for key in self.variables['color'].keys():
            container = gui.VBox(width=200, height=200,style={'align-content':'center', 'margin':'auto'})
            colorpicker = gui.ColorPicker(self.variables['color'][key], width=200, height=20, margin='10px')
            
            linestyle_dropdown = gui.DropDown.new_from_list(['-', '--', '-.', '.', '.-'], width=200, height=20)
            linestyle_dropdown.select_by_value(self.variables['linestyle'][key])
            
            plotdata_dropdown = gui.DropDown.new_from_list(self.master.processingfiles.plot_data['1D'].keys(), width=200, height=20)
            plotdata_dropdown.select_by_value(self.variables['plotdata_dropdown'][key])
            
            container.append({'color' : colorpicker, 'linestyle': linestyle_dropdown, 'plot_data': plotdata_dropdown})
            
            self.append(container, str(key))
        
    def add_tab(self, widget):
        key = str(len(self.children)-1)
        
        self.variables['color'][key] = 'black'
        self.variables['plotdata_dropdown'][key] = 'AN'
        self.variables['linestyle'][key] = '-'
        
        container = gui.VBox(width=200, height=200,style={'align-content':'center','margin':'auto'})
        colorpicker = gui.ColorPicker(self.variables['color'][key], width=200, height=20, margin='10px')
        
        linestyle_dropdown = gui.DropDown.new_from_list(['-', '--', '-.', '.', '.-'], width=200, height=20)
        linestyle_dropdown.select_by_value(self.variables['linestyle'][key])
        
        plotdata_dropdown = gui.DropDown.new_from_list(self.master.processingfiles.plot_data['1D'].keys(), width=200, height=20)
        plotdata_dropdown.select_by_value(self.variables['plotdata_dropdown'][key])
        
        container.append({'color' : colorpicker, 'linestyle': linestyle_dropdown, 'plot_data': plotdata_dropdown})
        
        self.append(container, key)
        
    def remove_tab(self, widget):
        if len(self.children) < 3:
            return
        
        key = str(len(self.children) - 2)
        
        self.remove_child(self.children[key])
        
        del self.variables['color'][key]
        del self.variables['plotdata_dropdown'][key]
        del self.variables['linestyle'][key]
        
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
                                                'plotdata_dropdown': {'0': 'AN'},
                                                'color': {'0': 'black'},
                                                 'linestyle': {'0':'-'}}
            self.variables = self.master.config['Simple Plot'][ID]
        
        px = 1/plt.rcParams['figure.dpi']
        style['width'], style['height'] = gui.to_pix(self.variables['width']), gui.to_pix(self.variables['height']) 
        figsize = (self.variables['width']*px, self.variables['height']*px)
        super(SimplePlotWidget, self).__init__(figsize=figsize, style=style, **kwargs)
        
        # Define Menu Items        
        self.view = gui.MenuItem('Simple Plot ' + ID, width=100, height=30)
        self.view.onclick.do(self.view_pressed)
        
        # Define widget content
        self.ax = self.fig.add_subplot(1,1,1)
        self.ax.set_title('Simple Plot ' + ID)
        self.redraw()
        
        # TODO fix this
        self.plot_data = {}
        for key in self.variables['plotdata_dropdown'].keys():
            self.plot_data[key] = self.master.processingfiles.plot_data['1D'][self.variables['plotdata_dropdown'][key]]
    
        # View Dialog
        self.view_dialog = gui.GenericDialog(title='Simple Plot ' + self.ID, message='Click Ok to transfer content to main page', width='500px')
        
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
        
        
        # Tabbing for multiple data sources
        self.tabbox = LinePlotDataTabbox(self.master, self.variables)
        
        self.add_datasource_btn = gui.Button('Add datasource', width=200, height=30, margin='10px')
        self.view_dialog.add_field_with_label('add_datasource_btn', 'Add datasource', self.add_datasource_btn)
        self.add_datasource_btn.onclick.do(self.tabbox.add_tab)
        
        self.remove_datasource_btn = gui.Button('Remove datasource', width=200, height=30, margin='10px')
        self.view_dialog.add_field_with_label('remove_datasource_btn', 'Remove datasource', self.remove_datasource_btn)
        self.remove_datasource_btn.onclick.do(self.tabbox.remove_tab)
        
        self.view_dialog.add_field('tabbox', self.tabbox)
        
        self.view_dialog.confirm_dialog.do(self.update_view)
        
        
    def view_pressed(self, widget):
        self.view_dialog.show(self.master)
        
    def update_plot(self):
        self.ax.clear()
        
        for key in self.plot_data.keys():
            x = self.plot_data[key]['data']['x']
            y = self.plot_data[key]['data']['y']
            label = self.plot_data[key]['label']
            
            if x is None:
                self.ax.plot(y, self.variables['linestyle'][key], color=self.variables['color'][key], label=label)
            else:
                self.ax.plot(x, y, self.variables['linestyle'][key], color=self.variables['color'][key], label=label)
            
        if not self.variables['xlim_check']:
            self.ax.set_xlim(*self.variables['xlim'])
        if not self.variables['ylim_check']:
            self.ax.set_ylim(*self.variables['ylim'])
            
        self.ax.set_title('Simple Plot ' + self.ID)
        self.ax.legend()
        self.redraw()                          
    
    def update_view(self, widget):
        if self.remove_check.get_value():
            self.master.main_container.remove_pane(self)
            self.master.view.sub_container.remove_child(self.view)
            del self.master.config['Simple Plot'][self.ID]
            return
        
        self.update_variables()
        
        if self.variables['mpi_check']:
            self.master.main_container.add_pane(self, self.variables['x'],self.variables['y'], 'Simple Plot ' + self.ID)
        else:
            self.master.main_container.remove_pane(self)
            
        self.update_plot()
        
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
        
        self.plot_data = {}
        print('plotdata_dropdown: ', self.variables['plotdata_dropdown'].keys())
        for key in self.variables['plotdata_dropdown'].keys():
            data_val = self.tabbox.get_child(key).get_child('plot_data').get_value()
            
            self.variables['plotdata_dropdown'][key] = data_val
            self.plot_data[key] = self.master.processingfiles.plot_data['1D'][data_val]
            
            self.variables['color'][key] = self.tabbox.get_child(key).get_child('color').get_value()
            self.variables['linestyle'][key] = self.tabbox.get_child(key).get_child('linestyle').get_value()
            
        
    
    def clear_btn_pressed(self, widget):
        for key in self.plot_data.keys():
            self.plot_data[key]['data']['y'] = []
            
            if self.plot_data[key]['data']['x'] is not None:
                self.plot_data[key]['data']['x'] = []