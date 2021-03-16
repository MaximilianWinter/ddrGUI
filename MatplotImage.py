#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 11:40:59 2021

@author: maximilian
"""
from remi import gui
import threading
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import io
import time

class MatplotImage(gui.Image):
    ax = None

    def __init__(self, figsize=(8,8), **kwargs):
        super(MatplotImage, self).__init__("/%s/get_image_data?update_index=0" % id(self), **kwargs)
        self._buf = None
        self._buflock = threading.Lock()

        self.fig = Figure(figsize=figsize)

        self.redraw()

    def redraw(self):
        canv = FigureCanvasAgg(self.fig)
        buf = io.BytesIO()
        canv.print_figure(buf, format='png')
        with self._buflock:
            if self._buf is not None:
                self._buf.close()
            self._buf = buf

        i = int(time.time() * 1e6)
        self.attributes['src'] = "/%s/get_image_data?update_index=%d" % (id(self), i)

        super(MatplotImage, self).redraw()

    def get_image_data(self, update_index):
        with self._buflock:
            if self._buf is None:
                return None
            self._buf.seek(0)
            data = self._buf.read()

        return [data, {'Content-type': 'image/png'}]