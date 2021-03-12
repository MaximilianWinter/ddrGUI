# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 18:11:16 2021

@author: mWinter
"""
from remi import gui, App, start
from MatplotImage import MatplotImage
import numpy as np
import matplotlib.pyplot as plt
from CustomWidgets import CameraView, TimelinePlot, SimplePlotWidget, FloatingPanesContainer
        
        
class MyApp(App):
    
    def __init__(self, *args):
        self.config = {'CameraView': {'atomroi': {'x': 100, 'y': 100, 'w': 100, 'h': 100},
                                      'refroi': {'x': 200, 'y': 100, 'w': 100, 'h': 100},
                                      'mpi_x_check': True,
                                      'mpi_y_check': True,
                                      'vmin': 0,
                                      'vmax': 1},
                       'TimeLinePlot': {},
                       'Simple Plot': {'mpi_check': True,
                                       'x': 0,
                                       'y': 680}}
        super(MyApp, self).__init__(*args)
        
        
    def main(self):
        
        
        self.main_container = FloatingPanesContainer(width='1250px', height='1000px',margin='0px auto')
        
        menu = gui.Menu(width='100%', height='30px')
        settings = gui.MenuItem('Settings', width=100, height=30)
        view = gui.MenuItem('View', width=100, height=30)
        menu.append([settings, view])
        
        menubar = gui.MenuBar(width='100%', height='30px')
        menubar.append(menu)
        
        # define content
        camview = CameraView(self, 'CameraView')
        view.append(camview.view)
        
        timelineplot = TimelinePlot(self, 'TimeLinePlot')
        view.append(timelineplot.view)
        
        simpleplot = SimplePlotWidget(self, 'Simple Plot')
        view.append(simpleplot.view)
        
        self.main_container.append([menubar])#, camview])
        self.main_container.add_pane(camview, 0, 30)
        self.main_container.add_pane(simpleplot, 0, 680)
        
        return self.main_container
    

if __name__ == "__main__":
    # starts the webserver
    # optional parameters
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    start(MyApp, debug=False, address='0.0.0.0', port=8081, start_browser=False, multiple_instance=False)        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        