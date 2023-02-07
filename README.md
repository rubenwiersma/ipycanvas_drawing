# Drawing utility in ipycanvas
Small utility to make simple drawings in Jupyter notebooks with ipycanvas and ipywidgets.
Useful for getting quick user input in research prototypes, e.g., for masking, annotation, etc.

![Example usage](img/example_screenshot.png)


## Install
```bash
pip install ipycanvas-drawing
```

## Usage
Create a simple drawing interface. Check out the notebook in `examples` for a more complete example.

```python
from ipycanvas_drawing import DrawingWidget

drawing_widget = DrawingWidget(width=500, height=500)
drawing_widget.show()
```

## Credits
Based on the [hand drawing example](https://github.com/martinRenou/ipycanvas/blob/master/examples/hand_drawing.ipynb) provided by @martinRenou, but adds some additional functionality like adding squares and ellipses and a 1-step undo.
