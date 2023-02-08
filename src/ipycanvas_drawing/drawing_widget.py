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
    prev_canvas = None
    tool_selection = ToggleButtons(description="Tool:",
                                   options=[('Brush ', Tools.BRUSH), ('Square ', Tools.SQUARE), ('Circle ', Tools.CIRCLE)],
                                   value=Tools.BRUSH,
                                   icons=['brush', 'square', 'circle'])
    
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
        self.canvas = MultiCanvas(n_canvases=3, width=width, height=height, sync_image_data=True)
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
        with hold_canvas(): 
            if type(self.background) is np.ndarray:
                self.canvas[0].put_image_data(self.background)
            else:
                self.canvas[0].fill_style = self.background
                self.canvas[0].fill_rect(0, 0, self.canvas.width, self.canvas.height)

    def show(self):
        # UI controls
        picker = ColorPicker(description="Color:", value=self.default_style)
        radius_slider = IntSlider(description="Brush radius:", value=self.default_radius, min=1, max=100)
        clear_button = Button(description="Clear")
        clear_button.on_click(self.clear_canvas)
        undo_button = Button(description="Undo")
        undo_button.on_click(self.undo)
        background_button = Button(description="Reset background")
        background_button.on_click(self.reset_background)

        # Link UI controls to canvas
        link((picker, "value"), (self.canvas[1], "stroke_style"))
        link((picker, "value"), (self.canvas[1], "fill_style"))
        link((radius_slider, "value"), (self.canvas[1], "line_width"))

        # Display in grid
        return HBox((self.canvas, VBox((self.tool_selection, picker, radius_slider, clear_button, undo_button, background_button))))
        
    def on_mouse_down(self, x, y):
        self.drawing = True
        self.position = (x, y)
        self.shape = [self.position]
        self.prev_canvas = copy.copy(self.canvas._canvases[1].get_image_data())

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
        with hold_canvas():
            self.canvas[1].clear()
        
    def undo(self, *args):
        if self.prev_canvas is not None:
            with hold_canvas():
                self.canvas[1].put_image_data(self.prev_canvas)

    def get_image(self, background=False):
        if background:
            return self.canvas.get_image_data()
        return self.canvas._canvases[1].get_image_data()
