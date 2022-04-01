from . import tk_workspace
from . import xplat


PIN_WIDTH        = 12
PIN_DELTA        = 2*PIN_WIDTH
PIN_LENGTH       = 20
PIN_LABEL_OFFSET = 2


def pin_d(t0, t1, i):
    if t0 < t1:
        return t0 + PIN_WIDTH + i*PIN_DELTA
    return t0 - (i + 1)*PIN_DELTA


class Workspace(tk_workspace.Workspace):  # pylint: disable=W0223
    def __init__(self, *args):
        self.pin_width        = PIN_WIDTH
        self.pin_length       = PIN_LENGTH
        self.pin_label_offset = PIN_LABEL_OFFSET
        super().__init__(*args)

    def add_h_pin(self, p, x, y):
        c = self.mcu_canvas
        r = c.add_rectangle(x, y, PIN_LENGTH, PIN_WIDTH, fill=self.elem_fill)
        c.add_text(x + PIN_LENGTH / 2 + xplat.EDGE_PIN_H_KEY_DX,
                   y + PIN_WIDTH / 2 + xplat.EDGE_PIN_H_KEY_DY,
                   font=self.pin_font, text=p.key, anchor='c')
        return r

    def add_v_pin(self, p, x, y):
        c = self.mcu_canvas
        r = c.add_rectangle(x, y, PIN_WIDTH, PIN_LENGTH, fill=self.elem_fill)
        c.add_text(x + PIN_WIDTH / 2 + xplat.EDGE_PIN_V_KEY_DX,
                   y + PIN_LENGTH / 2, font=self.pin_font, text=p.key,
                   anchor='c', angle=90)
        return r

    def add_l_pin(self, p, x, y0, y1, i):
        y = pin_d(y0, y1, i)
        self.mcu_canvas.add_text(x - PIN_LABEL_OFFSET, y + PIN_WIDTH / 2,
                                 font=self.label_font, text=p.name, anchor='e')
        return self.add_h_pin(p, x, y)

    def add_r_pin(self, p, x, y0, y1, i):
        y = pin_d(y0, y1, i)
        self.mcu_canvas.add_text(x + PIN_LENGTH + 1 + PIN_LABEL_OFFSET,
                                 y + PIN_WIDTH / 2, font=self.label_font,
                                 text=p.name, anchor='w')
        return self.add_h_pin(p, x, y)

    def add_t_pin(self, p, x0, x1, i, y):
        x = pin_d(x0, x1, i)
        self.mcu_canvas.add_text(x + PIN_WIDTH / 2, y - PIN_LABEL_OFFSET,
                                 font=self.label_font, text=p.name, anchor='w',
                                 angle=90)
        return self.add_v_pin(p, x, y)

    def add_b_pin(self, p, x0, x1, i, y):
        x = pin_d(x0, x1, i)
        self.mcu_canvas.add_text(x + PIN_WIDTH / 2,
                                 y + PIN_LENGTH + 1 + PIN_LABEL_OFFSET,
                                 font=self.label_font, text=p.name, anchor='e',
                                 angle=90)
        return self.add_v_pin(p, x, y)
