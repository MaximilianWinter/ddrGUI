"""
Created on Thu Mar 11 18:11:16 2021

@author: mWinter

todo:
    1. add ax labels, xlim, ylim, linestyle, color for Simple Plot; done
    2. add fit plot, add plotsources in simple plot; done
    3. automatic figure update when resized; done
    4. use class with view for AN/T function choices # TODO
    5. add animation when loop is running; done
    6. add Text Widget for AN, T; done
    7. bring widget to front when selected; done
    8. add plot title; done
    9. make camview resizeable; done
    10. find/fix dragging issue of camview
    11. add try/except for init for each widget; done
    12. resize ROIs automatically
"""
from remi import gui, App, start

from CameraView import CameraView
from SimplePlotWidget import SimplePlotWidget
from FloatingPanesContainer import FloatingPanesContainer
from ProcessingFiles import ProcessingFiles
from AtomnumberTemperatureWidget import AtomnumberTemperatureWidget

from threading import Thread
import json
        
class CamWebGUI(App):
    
    def __init__(self, *args):
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {}
            
        super(CamWebGUI, self).__init__(*args)
        
        
    def main(self):
        
        
        self.main_container = FloatingPanesContainer(width='1250px', height='1000px',margin='0px auto')
        
        menu = gui.Menu(width='100%', height='30px')
        start_stop_btn = gui.MenuItem('Start', width=100, height=30)
        start_stop_btn.onclick.do(self.start_stop_btn_pressed)
        settings = gui.MenuItem('Settings', width=100, height=30)
        
        self.view = gui.MenuItem('View', width=100, height=30)        
        menu.append([start_stop_btn, settings, self.view])
        
        menubar = gui.MenuBar(width='100%', height='30px')
        menubar.append(menu)
        
        self.progress = gui.Progress(0, 4, width=1250, height=5)
        menubar.append(self.progress)
        
        # define content
        add_widget = gui.MenuItem('Add widget', width=100, height=30)#
        
        add_lineplot = gui.MenuItem('Line Plot', width=100, height=30)
        add_lineplot.onclick.do(self.add_lineplot_pressed)
        
        add_widget.append([add_lineplot])
        
        self.view.append(add_widget)
        
        self.processingfiles = ProcessingFiles(self, 'Processing Files')
        settings.append(self.processingfiles.settings)
        
        save = gui.MenuItem('Save', width=100, height=30)
        save.onclick.do(self.save_pressed)
        settings.append(save)
        
        self.main_container.append([menubar])
        
        AN_T = AtomnumberTemperatureWidget(self, 'AN and T')
        self.view.append(AN_T.view)
        self.main_container.add_pane(AN_T, self.config['AN and T']['x'], self.config['AN and T']['y'], 'AN and T')
        
        camview = CameraView(self, 'Camera View')
        self.view.append(camview.view)
        self.main_container.add_pane(camview, self.config['Camera View']['x'], self.config['Camera View']['y'], 'Camera View')
        #self.main_container.add_pane(camview.mpi_im, self.config['Camera View']['x'], self.config['Camera View']['y'], 'Camera View')
        
        if 'Simple Plot' in self.config.keys():
            for ID in self.config['Simple Plot'].keys():
                simpleplot = SimplePlotWidget(self, ID)
                self.view.append(simpleplot.view)
                self.main_container.add_pane(simpleplot, self.config['Simple Plot'][ID]['x'], self.config['Simple Plot'][ID]['y'], 'Simple Plot ' + str(ID))
            
        return self.main_container
    
    # TODO: undo add_camview and ID for camview
    
    def add_lineplot_pressed(self, widget):
        try:
            ID = str(int(max(self.config['Simple Plot'].keys())) + 1)
        except:
            ID = '0'
        simpleplot = SimplePlotWidget(self, ID)
        self.view.append(simpleplot.view)
        self.main_container.add_pane(simpleplot, self.config['Simple Plot'][ID]['x'], self.config['Simple Plot'][ID]['y'], 'Simple Plot ' + ID)
        
    def start_stop_btn_pressed(self, widget):
        if self.processingfiles.running:
            print('stop...')
            self.processingfiles.running = False
            widget.set_text('Start')
        else:
            print('start...')
            self.processingfiles.running = True
            thread = Thread(target=self.processingfiles.run)
            thread.start()
            widget.set_text('Stop')
        
    def save_pressed(self, widget=None):
        for child in self.main_container.children.values():
            try:
                child.update_variables()
            except:
                pass
        with open('config.json', 'w') as f:
            json.dump(self.config, f)
        print('Settings saved.')
            
    def on_close(self):
        # save config file
        self.processingfiles.running = False
        
        self.save_pressed()
        
        super(CamWebGUI, self).on_close()
    

if __name__ == "__main__":
    # starts the webserver
    # optional parameters
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    start(CamWebGUI, debug=False, address='130.183.94.217', port=8081, start_browser=False, multiple_instance=False)        
    #start(MyApp, debug=False, address='192.1.2.20', port=8081, start_browser=False, multiple_instance=False) 
    #start(MyApp, debug=False, address='0.0.0.0', port=8081, start_browser=False, multiple_instance=False)        
        