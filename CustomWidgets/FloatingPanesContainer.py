# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 17:32:14 2021

@author: mWinter
"""
from remi import gui

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
        
        
        try:
            refWidget.style['z-index'] = '1' # bring new selected widget to front
            self.refWidget.style['z-index'] = '0' # bring old selected widget to back
        except:
            pass
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
        
        try:
            self.refWidget.update_fig()
            print('updating figure')
        except:
            print('no figure for updating')

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
            # try:
            #     self.refWidget.unselect_panes()
            # except:
            #     print('nope')
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
        self.style['overflow'] = 'hidden'

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
        
    def update_pane(self, pane):
        x = gui.from_pix(pane.style['left'])
        y = gui.from_pix(pane.style['top'])
        
        self.remove_pane(pane)
        self.add_pane(pane, x, y)

    def on_pane_selection(self, emitter):
        print('on pane selection')
        self.resizeHelper.setup(emitter,self)
        self.dragHelper.setup(emitter,self)
        self.resizeHelper.update_position()
        self.dragHelper.update_position()

    def on_helper_dragged_update_the_latter_pos(self, emitter, widget_to_update):
        widget_to_update.update_position()
        