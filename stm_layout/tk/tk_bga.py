from . import tk_workspace


PIN_DIAM        = 30
PIN_SPACE       = 22
PIN_DELTA       = (PIN_DIAM + PIN_SPACE)


class BGAWorkspace(tk_workspace.Workspace):
    def __init__(self, *args):
        super().__init__(*args)

        cw  = self.chip.width
        ch  = self.chip.height
        w   = cw*PIN_DELTA + PIN_SPACE
        h   = ch*PIN_DELTA + PIN_SPACE + self.label_font.metrics('ascent')
        pad = 15
        self.set_geometry(50, 50, w + 2*pad + self.info_width,
                          max(h + 2*pad, self.info_height))

        c = self.mcu_canvas = self.add_canvas(w + 2*pad, h + 2*pad)
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)

        m = c.add_rectangle(pad, pad, w, h, fill=self.elem_fill)
        for x in range(cw):
            for y in range(ch):
                p = self.chip.chip.pins[x][y]
                if p is None:
                    continue

                o = c.add_oval(
                        m.x + PIN_SPACE + x*PIN_DELTA,
                        m.y + PIN_SPACE + y*PIN_DELTA,
                        PIN_DIAM, PIN_DIAM,
                        fill=self.elem_fill)
                self.pin_elems.append(o)
                c.add_text(
                        o.x + o.width / 2, o.y + o.height,
                        font=self.label_font, text=p.name, anchor='n')
                c.add_text(
                        o.x + o.width / 2 + 1, o.y + o.height / 2,
                        font=self.pin_font, text=p.key, anchor='c')
                o.pin = p
