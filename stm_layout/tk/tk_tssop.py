from . import tk_workspace
from .. import chip_db


PKG_WIDTH        = 100
PIN_WIDTH        = 12
PIN_LENGTH       = 20
PIN_LABEL_OFFSET = 2


class TSSOPWorkspace(tk_workspace.Workspace):
    def __init__(self, *args):
        super().__init__(*args)

        ch = self.chip.height
        w  = PKG_WIDTH
        h  = 2*PIN_WIDTH*ch + PIN_WIDTH

        pad  = 0
        for _, p in self.chip.pins.items():
            pad = max(pad, self.label_font.measure(p.name))
        pad += PIN_LENGTH + 5 + PIN_LABEL_OFFSET
        self.set_geometry(50, 50, w + 2*pad + self.info_width,
                          max(h + 2*pad, self.info_height))

        c = self.mcu_canvas = self.add_canvas(w + 2*pad, h + 2*pad)
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)

        l0 = 1
        r0 = l0 + ch
        m = c.add_rectangle(pad, pad, w, h, fill=self.elem_fill)
        for k, p in self.chip.pins.items():
            i = int(k)
            if l0 <= i < r0:
                # Left row.
                r = c.add_rectangle(
                        m.x - PIN_LENGTH,
                        m.y + PIN_WIDTH*(2*(i - l0) + 1),
                        PIN_LENGTH, PIN_WIDTH, fill=self.elem_fill)
                c.add_text(
                        r.x - PIN_LABEL_OFFSET, r.y + r.height / 2,
                        font=self.label_font, text=p.name, anchor='e')
                c.add_text(
                        r.x + r.width / 2 + 1, r.y + r.height / 2,
                        font=self.pin_font, text='%u' % i, anchor='c')
                self.pin_elems.append(r)

            else:
                # Right row.
                r = c.add_rectangle(
                        m.x + m.width,
                        m.y + m.height - PIN_WIDTH*(2*(i - r0) + 2),
                        PIN_LENGTH, PIN_WIDTH, fill=self.elem_fill)
                c.add_text(
                        r.x + r.width + 1 + PIN_LABEL_OFFSET,
                        r.y + r.height / 2,
                        font=self.label_font, text=p.name, anchor='w')
                c.add_text(
                        r.x + r.width / 2, r.y + r.height / 2,
                        font=self.pin_font, text='%u' % i,
                        anchor='c')
                self.pin_elems.append(r)

            r.pin = p

        package_name = chip_db.package(self.chip.part)
        c.add_text(
                m.x + m.width / 2, m.y + m.height / 2,
                font=self.label_font,
                text='%s\n%s' % (self.chip.name, package_name),
                anchor='c')
