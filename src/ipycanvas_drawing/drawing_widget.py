from enum import Enum

from ipywidgets import Image
from ipywidgets import ColorPicker, IntSlider, link, AppLayout, HBox, VBox, Button, Label, ToggleButtons, ToggleButtonsStyle
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
    tool_selection = ToggleButtons(description="Tool:",
                                   options=[('Brush ', Tools.BRUSH), ('Square ', Tools.SQUARE), ('Circle ', Tools.CIRCLE)],
                                   value=Tools.BRUSH,
                                   icons=['brush', 'square', 'circle'])
    drawing_line_width = 3
    prev_canvas = None
    
    def __init__(self, width, height, background="#FFFFFF"):
        # Initialization
        self.background = background
        self.init_canvas(width, height, background)

    def init_canvas(self, width, height, background):
        self.canvas = MultiCanvas(n_canvases=3, width=width, height=height, sync_image_data=True)
        self.canvas[0].fill_style = background
        self.canvas[0].fill_rect(0, 0, self.canvas.width, self.canvas.height)
        
        self.canvas.on_mouse_down(self.on_mouse_down)
        self.canvas.on_mouse_move(self.on_mouse_move)
        self.canvas.on_mouse_up(self.on_mouse_up)

        self.canvas[2].stroke_style = "#4287F5"
        self.canvas[2].fill_style = "#4287F5"
        self.canvas[2].line_cap = 'round'
        self.canvas[2].line_width = self.drawing_line_width
        self.canvas[2].global_alpha = 0.5
        
        self.canvas[1].stroke_style = "#000000"
        self.canvas[1].line_cap = 'round'
        self.canvas[1].line_join = 'round'
        self.canvas[1].line_width = 10
    
    def show(self):
        # UI controls
        picker = ColorPicker(description="Color:", value="#000000")
        radius_slider = IntSlider(description="Brush radius:", value=10, min=1, max=50)
        clear_button = Button(description="Clear")
        clear_button.on_click(self.clear_canvas)
        undo_button = Button(description="Undo")
        undo_button.on_click(self.undo)

        # Link UI controls to canvas
        link((picker, "value"), (self.canvas[1], "stroke_style"))
        link((picker, "value"), (self.canvas[1], "fill_style"))
        link((radius_slider, "value"), (self.canvas[1], "line_width"))

        # Display in grid
        return HBox((self.canvas, VBox((self.tool_selection, picker, radius_slider, clear_button, undo_button))))
        
    def on_mouse_down(self, x, y):
        self.drawing = True
        self.position = (x, y)
        self.shape = [self.position]
        self.prev_canvas = self.canvas.get_image_data()

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
        self.canvas[1].clear()
        
    def undo(self, *args):
        if self.prev_canvas is not None:
            self.canvas[1].put_image_data(self.prev_canvas)