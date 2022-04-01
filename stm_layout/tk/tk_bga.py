from . import tk_workspace
from . import xplat


PIN_DIAM        = 30
PIN_SPACE       = 22
PIN_DELTA       = (PIN_DIAM + PIN_SPACE)


class BGAWorkspace(tk_workspace.Workspace):
    def __init__(self, *args):
        super().__init__(*args)

    def _make_mcu_canvas(self):
        dy  = self.label_font.metrics('linespace')
        cw  = self.chip.geometry.width
        ch  = self.chip.geometry.height
        w   = cw*PIN_DELTA + PIN_SPACE
        h   = ch*PIN_DELTA + PIN_SPACE + self.label_font.metrics('ascent')
        pad = 15
        self.set_geometry(50, 50, w + 2*pad + self.info_width,
                          max(h + 2*pad + dy, self.info_height))

        c = self.mcu_canvas = self.add_canvas(w + 2*pad, h + 2*pad + dy,
                                              takefocus=1, highlightthickness=1)
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)

        m = c.add_rectangle(pad, pad + dy, w, h, fill=self.elem_fill)
        for x in range(cw):
            for y in range(ch):
                p = self.chip.geometry.get_pin(x, y)
                if p is None:
                    continue

                o = c.add_oval(
                        m.x + PIN_SPACE + x*PIN_DELTA,
                        m.y + PIN_SPACE + y*PIN_DELTA,
                        PIN_DIAM, PIN_DIAM,
                        fill=self.elem_fill)
                self.pin_elems.append(o)
                c.add_text(
                        o.x + o.width / 2,
                        o.y + o.height + xplat.BGA_PIN_NAME_DY,
                        font=self.label_font, text=p.name, anchor='n')
                c.add_text(
                        o.x + o.width / 2 + xplat.BGA_PIN_KEY_DX,
                        o.y + o.height / 2 + xplat.BGA_PIN_KEY_DY,
                        font=self.pin_font, text=p.key, anchor='c')
                o.pin = p
                p.pin_elem = o

        c.add_text(m.x, m.y, font=self.label_font, text=self.chip.name,
                   anchor='sw')
        c.add_text(m.x + m.width / 2, m.y, font=self.label_font,
                   text=self.max_freq_mhz, anchor='s')
        c.add_text(m.rx, m.y, font=self.label_font,
                   text=self.chip.geometry.name, anchor='se')

        return c

    def handle_up(self):
        self.select_pin(self.chip.geometry.up(self.selected_pin.pin).pin_elem)

    def handle_down(self):
        self.select_pin(self.chip.geometry.down(self.selected_pin.pin).pin_elem)

    def handle_left(self):
        self.select_pin(self.chip.geometry.left(self.selected_pin.pin).pin_elem)

    def handle_right(self):
        self.select_pin(
            self.chip.geometry.right(self.selected_pin.pin).pin_elem)
