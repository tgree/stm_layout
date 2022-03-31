from . import tk_edgy
from .. import chip_db


class LQFPWorkspace(tk_edgy.Workspace):
    def __init__(self, *args):
        super().__init__(*args)

    def _make_mcu_canvas(self):
        cw        = self.chip.width - 2
        ch        = self.chip.height - 2
        w         = 2*self.pin_width*cw + self.pin_width
        h         = 2*self.pin_width*ch + self.pin_width

        pad  = 0
        for _, p in self.chip.pins.items():
            pad = max(pad, self.label_font.measure(p.name))
        pad += self.pin_length + 5 + self.pin_label_offset
        self.set_geometry(50, 50, w + 2*pad + self.info_width,
                          max(h + 2*pad, self.info_height))

        c = self.mcu_canvas = self.add_canvas(w + 2*pad, h + 2*pad, takefocus=1)
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)

        l0 = 1
        b0 = l0 + ch
        r0 = b0 + cw
        t0 = r0 + ch
        m = c.add_rectangle(pad, pad, w, h, fill=self.elem_fill)
        for _, p in self.chip.pins.items():
            i = int(p.key)
            if l0 <= i < b0:
                r = self.add_l_pin(p, m.x - self.pin_length, m.ty, m.by, i - l0)
            elif b0 <= i < r0:
                r = self.add_b_pin(p, m.lx, m.rx, i - b0, m.y + m.height)
            elif r0 <= i < t0:
                r = self.add_r_pin(p, m.x + m.width, m.by, m.ty, i - r0)
            else:
                r = self.add_t_pin(p, m.rx, m.lx, i - t0, m.y - self.pin_length)

            self.pin_elems.append(r)
            r.pin = p

        package_name = chip_db.package(self.chip.part)
        c.add_text(
                m.x + m.width / 2, m.y + m.height / 2,
                font=self.label_font,
                text='%s\n%s\n%s' % (self.chip.name, package_name,
                                     self.max_freq_mhz),
                anchor='c')

        if 'LQFP' not in package_name:
            m.resize(pad - self.pin_length, pad - self.pin_length,
                     w + 2*self.pin_length, h + 2*self.pin_length)

        return c

    def handle_up(self):
        cw = self.chip.width - 2
        ch = self.chip.height - 2
        p  = self.selected_pin.pin
        i  = int(p.key) - 1
        if i < ch:
            # Left side.
            i = (i - 1) % len(self.pin_elems)
        elif i < ch + cw:
            # Bottom side.
            i = 2*cw + 3*ch - i - 1
            pass
        elif i < 2*ch + cw:
            # Right side.
            i = i + 1
        else:
            # Top side.
            pass
        self.select_pin(self.pin_elems[i])

    def handle_down(self):
        cw = self.chip.width - 2
        ch = self.chip.height - 2
        p  = self.selected_pin.pin
        i  = int(p.key) - 1
        if i < ch:
            # Left side.
            i = i + 1
        elif i < ch + cw:
            # Bottom side.
            pass
        elif i < 2*ch + cw:
            # Right side.
            i = i - 1
        else:
            # Top side.
            i = 2*cw + 3*ch - i - 1
        self.select_pin(self.pin_elems[i])

    def handle_left(self):
        cw = self.chip.width - 2
        ch = self.chip.height - 2
        p  = self.selected_pin.pin
        i  = int(p.key) - 1
        if i < ch:
            # Left side.
            pass
        elif i < ch + cw:
            # Bottom side.
            i = i - 1
        elif i < 2*ch + cw:
            # Right side.
            i = ch - (i + 1 - (ch + cw))
        else:
            # Top side.
            i = (i + 1) % len(self.pin_elems)
        self.select_pin(self.pin_elems[i])

    def handle_right(self):
        cw = self.chip.width - 2
        ch = self.chip.height - 2
        p  = self.selected_pin.pin
        i  = int(p.key) - 1
        if i < ch:
            # Left side.
            i = ch - (i + 1 - (ch + cw))
        elif i < ch + cw:
            # Bottom side.
            i = i + 1
        elif i < 2*ch + cw:
            # Right side.
            pass
        else:
            # Top side.
            i = i - 1
        self.select_pin(self.pin_elems[i])
