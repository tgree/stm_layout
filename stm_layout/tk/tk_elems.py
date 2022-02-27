import tkinter
import ctypes


class Elem:
    def __init__(self, elem_id):
        self._elem_id = elem_id


class CanvasElem(Elem):
    def __init__(self, canvas, elem_id, x, y, width=None, height=None):
        super().__init__(elem_id)
        self._canvas = canvas
        self.x       = x
        self.y       = y
        if width is not None:
            self.width = width
            self.lx    = x
            self.rx    = x + width
        if height is not None:
            self.height = height
            self.ty     = y
            self.by     = y + height

    def bbox(self):
        return self._canvas._bbox(self)

    def tag_lower(self, bottom_elem):
        self._canvas._tag_lower(self, bottom_elem)

    def set_fill(self, fill):
        self._canvas._set_fill(self, fill)

    def contains(self, x, y):
        w = getattr(self, 'width', 0)
        h = getattr(self, 'height', 0)
        return self.x <= x <= self.x + w and self.y <= y <= self.y + h

    def distance_squared(self, x, y):
        cx = self.x + getattr(self, 'width', 0) / 2
        cy = self.y + getattr(self, 'height', 0) / 2
        dx = (x - cx)
        dy = (y - cy)
        return dx*dx + dy*dy

    def move_to(self, x, y):
        self.x = x
        self.y = y
        if self.height is not None:
            self._canvas._move_to(self, x, y, x + self.width, y + self.height)
        else:
            self._canvas._move_to(self, x, y)

    def resize(self, x, y, width, height):
        assert self.width is not None
        assert self.height is not None
        self.x      = x
        self.y      = y
        self.width  = width
        self.height = height
        self._canvas._move_to(self, x, y, x + width, y + height)


class TextElem(CanvasElem):
    def set_text(self, text):
        self._canvas._set_text(self, text)


class Widget:
    def __init__(self, widget):
        self._widget = widget


class Entry(Widget):
    def focus_set(self):
        self._widget.focus_set()


class Canvas:
    def __init__(self, canvas):
        self._canvas = canvas

    def _bbox(self, elem):
        return self._canvas.bbox(elem._elem_id)

    def _tag_lower(self, bottom_elem, top_elem):
        self._canvas.tag_lower(bottom_elem._elem_id, top_elem._elem_id)

    def _set_fill(self, elem, fill):
        self._canvas.itemconfig(elem._elem_id, fill=fill)

    def _move_to(self, elem, *args):
        self._canvas.coords(elem._elem_id, *args)

    def _set_text(self, elem, text):
        self._canvas.itemconfig(elem._elem_id, text=text)

    def add_rectangle(self, x, y, width, height, **kwargs):
        elem_id = self._canvas.create_rectangle(
                (x, y, x + width, y + height), **kwargs)
        return CanvasElem(self, elem_id, x, y, width=width, height=height)

    def add_oval(self, x, y, width, height, **kwargs):
        elem_id = self._canvas.create_oval(
                (x, y, x + width, y + height), **kwargs)
        return CanvasElem(self, elem_id, x, y, width=width, height=height)

    def add_text(self, x, y, **kwargs):
        elem_id = self._canvas.create_text((x, y), **kwargs)
        return TextElem(self, elem_id, x, y)

    def add_window(self, x, y, widget, **kwargs):
        self._canvas.create_window(x, y, window=widget._widget, **kwargs)

    def add_entry(self, **kwargs):
        return Entry(tkinter.Entry(self._canvas, **kwargs))


class TKBase:
    def __init__(self):
        # Windows hack #1.
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except AttributeError:
            pass
        self._root = tkinter.Tk()

        # Windows hack #2.
        self._root.tk.call('tk', 'scaling', 1.0)

    def set_geometry(self, x, y, width, height):
        self._root.geometry('%ux%u+%u+%u' % (width, height, x, y))

    def mainloop(self):
        self._root.mainloop()

    def add_canvas(self, width, height, column=0, row=0, sticky=None):
        c = tkinter.Canvas(self._root, bd=0, highlightthickness=0, width=width,
                           height=height)
        c.grid(column=column, row=row, sticky=sticky)
        return Canvas(c)

    def register_handler(self, event_type, handler):
        self._root.bind(event_type, lambda e: handler(self, e, e.x, e.y))

    def register_mouse_moved(self, handler):
        self.register_handler('<Motion>', handler)

    def register_mouse_down(self, handler):
        self.register_handler('<Button-1>', handler)

    def register_mouse_up(self, handler):
        self.register_handler('<ButtonRelease-1>', handler)
