from . import tk_edgy


PKG_WIDTH = 100


class TSSOPWorkspace(tk_edgy.Workspace):
    def __init__(self, *args):
        super().__init__(*args)

    def _make_mcu_canvas(self):
        ch = self.chip.geometry.height
        w  = PKG_WIDTH
        h  = 2*self.pin_width*ch + self.pin_width

        pad  = 0
        for _, p in self.chip.pins.items():
            pad = max(pad, self.label_font.measure(p.name))
        pad += self.pin_length + 5 + self.pin_label_offset
        self.set_geometry(50, 50, w + 2*pad + self.info_width,
                          max(h + 2*pad, self.info_height))

        c = self.mcu_canvas = self.add_canvas(w + 2*pad, h + 2*pad, takefocus=1,
                                              highlightthickness=1)
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)

        l0 = 1
        r0 = l0 + ch
        m = c.add_rectangle(pad, pad, w, h, fill=self.elem_fill)
        for _, p in self.chip.pins.items():
            i = int(p.key)
            if l0 <= i < r0:
                r = self.add_l_pin(p, m.x - self.pin_length, m.ty, m.by, i - l0)
            else:
                r = self.add_r_pin(p, m.x + m.width, m.by, m.ty, i - r0)

            self.pin_elems.append(r)
            r.pin = p
            p.pin_elem = r

        c.add_text(
                m.x + m.width / 2, m.y + m.height / 2,
                font=self.label_font,
                text='%s\n%s\n%s' % (self.chip.name, self.chip.geometry.name,
                                     self.max_freq_mhz),
                anchor='c')

        return c
