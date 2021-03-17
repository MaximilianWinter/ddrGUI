# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 18:11:16 2021

@author: mWinter
"""
from remi import gui, App, start
from CustomWidgets import CameraView, TimelinePlot, SimplePlotWidget, FloatingPanesContainer, ProcessingFiles
        
        
class MyApp(App):
    
    def __init__(self, *args):
        self.config = {'Camera View': {0:    {'atomroi': {'x': 100, 'y': 100, 'w': 100, 'h': 100},
                                             'refroi': {'x': 200, 'y': 100, 'w': 100, 'h': 100},
                                              'mpi_check': True,
                                              'x': 0,
                                              'y': 30,
                                              'vmin': 0,
                                              'vmax': 1}},
                       'Simple Plot': {0:   {'mpi_check': True,
                                            'x': 0,
                                            'y': 680,
                                            'xmin':0,
                                            'xmax':1,
                                            'ymin':0,
                                            'ymax':1}},
                       'Processing Files': {},
                       'Directory': {'selected_directories': ['.'],
                                            'today_dir_check_val': False},
                       'Fits': {},
                       '1D Gaussian': {'symmetric_check': True, 'axes_aligned_check': False},
                       '2D Gaussian': {'symmetric_check': False, 'axes_aligned_check': False}}
        super(MyApp, self).__init__(*args)
        
        
    def main(self):
        
        
        self.main_container = FloatingPanesContainer(width='1250px', height='1000px',margin='0px auto')
        
        menu = gui.Menu(width='100%', height='30px')
        start_stop_btn = gui.MenuItem('Start/Stop', width=100, height=30)
        settings = gui.MenuItem('Settings', width=100, height=30)
        self.view = gui.MenuItem('View', width=100, height=30)        
        menu.append([start_stop_btn, settings, self.view])
        
        menubar = gui.MenuBar(width='100%', height='30px')
        menubar.append(menu)
        
        # define content
        add_widget = gui.MenuItem('Add widget', width=100, height=30)#
        
        add_camview = gui.MenuItem('Camera View', width=100, height=30)
        add_camview.onclick.do(self.add_camview_pressed)
        
        add_lineplot = gui.MenuItem('Line Plot', width=100, height=30)
        add_lineplot.onclick.do(self.add_lineplot_pressed)
        
        add_widget.append([add_camview, add_lineplot])
        
        self.view.append(add_widget)
        
        processingfiles = ProcessingFiles(self, 'Processing Files')
        settings.append(processingfiles.settings)
        
        self.main_container.append([menubar])
        
        for ID in self.config['Camera View'].keys():
            camview = CameraView(self, ID)
            self.view.append(camview.view)
            self.main_container.add_pane(camview, self.config['Camera View'][ID]['x'], self.config['Camera View'][ID]['y'], 'Camera View ' + str(ID))
        
        for ID in self.config['Simple Plot'].keys():
            simpleplot = SimplePlotWidget(self, ID)
            self.view.append(simpleplot.view)
            self.main_container.add_pane(simpleplot, self.config['Simple Plot'][ID]['x'], self.config['Simple Plot'][ID]['y'], 'Simple Plot ' + str(ID))
            
        return self.main_container
    
    # TODO: undo add_camview and ID for camview
    def add_camview_pressed(self, widget):
        try:
            ID = max(self.config['Camera View'].keys()) + 1
        except:
            ID = 0 
        camview = CameraView(self, ID)
        self.view.append(camview.view)
        self.main_container.add_pane(camview, 0, 30, 'Camera View ' + str(ID))
    
    def add_lineplot_pressed(self, widget):
        try:
            ID = max(self.config['Simple Plot'].keys()) + 1
        except:
            ID = 0
        simpleplot = SimplePlotWidget(self, ID)
        self.view.append(simpleplot.view)
        self.main_container.add_pane(simpleplot, 0, 680, 'Simple Plot ' + str(ID))
        
    def on_close(self):
        # save config file
        pass
    

if __name__ == "__main__":
    # starts the webserver
    # optional parameters
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    start(MyApp, debug=False, address='130.183.94.217', port=8081, start_browser=False, multiple_instance=False)        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        