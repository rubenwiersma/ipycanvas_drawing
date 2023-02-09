from enum import Enum
import copy

import numpy as np
from ipywidgets import Image
from ipywidgets import ColorPicker, IntSlider, link, HBox, VBox, Button, ToggleButtons
from ipycanvas import MultiCanvas, hold_canvas


class Tools(Enum):
    BRUSH = 0
    SQUARE = 1
    CIRCLE = 2
    
class DrawingWidget(object):
    drawing = False
    position = None
    shape = []
    output_array = None
    drawing_line_width = 3
    history = []
    future = []
    max_history = 100
    tool_selection = None
    
    def __init__(self, width, height, background="#FFFFFF", alpha=1.0, default_style="#000000", default_radius=10):
        """
        Create a MultiCanvas with three layers: a background layer, the drawing layer, and a temporary layer during drawing.

        params:
            width (int): Width of the canvas.
            height (int): Height of the canvas.
            background (string, np.Array): background in the first layer.
                Can be given as a hex-code (str) or a numpy array with values to fill in.
            alpha (float): Transparency of the drawing layer. Helpful for masking.
            default_style (str): Hex-code (str) of the default color in the colorpicker.
        """
        # Initialization
        self.background = background
        self.alpha = alpha
        self.default_style = default_style
        self.default_radius = default_radius
        self.init_canvas(width, height)

    def init_canvas(self, width, height):
        self.canvas = MultiCanvas(n_canvases=3, width=width, height=height)
        self.canvas._canvases[1].sync_image_data = True
        self.reset_background()

        self.canvas.on_mouse_down(self.on_mouse_down)
        self.canvas.on_mouse_move(self.on_mouse_move)
        self.canvas.on_mouse_up(self.on_mouse_up)

        self.canvas[2].stroke_style = "#4287F5"
        self.canvas[2].fill_style = "#4287F5"
        self.canvas[2].line_cap = 'round'
        self.canvas[2].line_width = self.drawing_line_width
        
        self.canvas[1].stroke_style = self.default_style
        self.canvas[1].line_cap = 'round'
        self.canvas[1].line_join = 'round'
        self.canvas[1].line_width = self.default_radius
        self.canvas[1].global_alpha = self.alpha
    
    def reset_background(self, *args):
        self.canvas._canvases[0].sync_image_data = True
        with hold_canvas(): 
            if type(self.background) is np.ndarray:
                self.canvas[0].put_image_data(self.background)
            else:
                self.canvas[0].fill_style = self.background
                self.canvas[0].fill_rect(0, 0, self.canvas.width, self.canvas.height)
        self.canvas._canvases[0].sync_image_data = False

    def show(self):
        # UI controls
        self.tool_selection = ToggleButtons(options=[('Brush ', Tools.BRUSH), ('Square ', Tools.SQUARE), ('Circle ', Tools.CIRCLE)],
                                            value=Tools.BRUSH,
                                            icons=['brush', 'square', 'circle'])
        picker = ColorPicker(description="Color:", value=self.default_style)
        radius_slider = IntSlider(description="Brush radius:", value=self.default_radius, min=1, max=100)
        clear_button = Button(description="Clear")
        clear_button.on_click(self.clear_canvas)
        undo_button = Button(description="Undo", icon="rotate-left")
        undo_button.on_click(self.undo)
        redo_button = Button(description="Redo", icon="rotate-right")
        redo_button.on_click(self.redo)

        # Link UI controls to canvas
        link((picker, "value"), (self.canvas[1], "stroke_style"))
        link((picker, "value"), (self.canvas[1], "fill_style"))
        link((radius_slider, "value"), (self.canvas[1], "line_width"))

        # Display in grid
        return HBox((self.canvas, VBox((self.tool_selection, picker, radius_slider, clear_button, HBox((undo_button, redo_button))))))

    def save_to_history(self):
        self.history.append(self.canvas._canvases[1].get_image_data())
        if len(self.history) > self.max_history:
            self.history = self.history[1:]
        self.future = []
        
    def on_mouse_down(self, x, y):
        self.drawing = True
        self.position = (x, y)
        self.shape = [self.position]
        self.save_to_history()

    def on_mouse_move(self, x, y):
        if not self.drawing:
            return

        tool = self.tool_selection.value
        with hold_canvas():
            if (tool == Tools.BRUSH):
                self.canvas[2].line_width = self.canvas[1].line_width
                self.canvas[2].stroke_line(self.position[0], self.position[1], x, y)
                self.canvas[2].line_width = self.drawing_line_width
            elif (tool == Tools.SQUARE):
                self.canvas[2].clear()
                self.canvas[2].stroke_rect(self.shape[0][0], self.shape[0][1], x - self.shape[0][0], y - self.shape[0][1])
            elif (tool == Tools.CIRCLE):
                self.canvas[2].clear()
                self.canvas[2].fill_circle(self.shape[0][0], self.shape[0][1], self.drawing_line_width)
                self.canvas[2].stroke_circle(self.shape[0][0], self.shape[0][1], ((x - self.shape[0][0])**2 + (y - self.shape[0][1])**2)**0.5)

            self.position = (x, y)
            
        self.shape.append(self.position)

    def on_mouse_up(self, x, y):
        self.drawing = False

        tool = self.tool_selection.value
        with hold_canvas():
            self.canvas[2].clear()
            if (tool == Tools.BRUSH):
                self.canvas[1].stroke_lines(self.shape)
            elif (tool == Tools.SQUARE):
                self.canvas[1].fill_rect(self.shape[0][0], self.shape[0][1], x - self.shape[0][0], y - self.shape[0][1])
            elif (tool == Tools.CIRCLE):
                self.canvas[1].fill_circle(self.shape[0][0], self.shape[0][1], ((x - self.shape[0][0])**2 + (y - self.shape[0][1])**2)**0.5)

        self.shape = []

    def clear_canvas(self, *args):
        self.save_to_history()
        with hold_canvas():
            self.canvas[1].clear()
        
    def undo(self, *args):
        if self.history:
            with hold_canvas():
                self.future.append(self.canvas._canvases[1].get_image_data())
                self.canvas[1].clear()
                self.canvas[1].put_image_data(self.history[-1])
                self.history = self.history[:-1]

    def redo(self, *args):
        if self.future:
            with hold_canvas():
                self.history.append(self.canvas._canvases[1].get_image_data())
                self.canvas[1].clear()
                self.canvas[1].put_image_data(self.future[-1])
                self.future = self.future[:-1]

    def get_image_data(self, background=False):
        if background:
            return self.canvas.get_image_data()
        return self.canvas._canvases[1].get_image_data()
