from . import tk_workspace
from .. import chip_db


PIN_WIDTH        = 12
PIN_LENGTH       = 20
PIN_LABEL_OFFSET = 2


class LQFPWorkspace(tk_workspace.Workspace):
    def __init__(self, *args):
        super().__init__(*args)

        cw        = self.chip.width - 2
        ch        = self.chip.height - 2
        w         = 2*PIN_WIDTH*cw + PIN_WIDTH
        h         = 2*PIN_WIDTH*ch + PIN_WIDTH

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
        b0 = l0 + ch
        r0 = b0 + cw
        t0 = r0 + ch
        m = c.add_rectangle(pad, pad, w, h, fill=self.elem_fill)
        for i, p in self.chip.pins.items():
            i = int(i)
            if l0 <= i < b0:
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

            elif b0 <= i < r0:
                # Bottom row.
                r = c.add_rectangle(
                        m.x + PIN_WIDTH*(2*(i - b0) + 1),
                        m.y + m.height,
                        PIN_WIDTH, PIN_LENGTH, fill=self.elem_fill)
                c.add_text(
                        r.x + r.width / 2,
                        r.y + r.height + 1 + PIN_LABEL_OFFSET,
                        font=self.label_font, text=p.name, anchor='e',
                        angle=90)
                c.add_text(
                        r.x + r.width / 2, r.y + r.height / 2,
                        font=self.pin_font, text='%u' % i,
                        anchor='c', angle=90)
                self.pin_elems.append(r)

            elif r0 <= i < t0:
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

            else:
                # Top row.
                r = c.add_rectangle(
                        m.x + m.width - PIN_WIDTH*(2*(i - t0) + 2),
                        m.y - PIN_LENGTH,
                        PIN_WIDTH, PIN_LENGTH, fill=self.elem_fill)
                c.add_text(
                        r.x + r.width / 2, r.y - PIN_LABEL_OFFSET,
                        font=self.label_font,
                        text=p.name, anchor='w', angle=90)
                c.add_text(
                        r.x + r.width / 2, r.y + r.height / 2,
                        font=self.pin_font, text='%u' % i,
                        anchor='c', angle=90)
                self.pin_elems.append(r)

            r.pin = p

        package_name = chip_db.package(self.chip.part)
        c.add_text(
                m.x + m.width / 2, m.y + m.height / 2,
                font=self.label_font,
                text='%s\n%s' % (self.chip.name, package_name),
                anchor='c')

        if 'LQFP' not in package_name:
            m.resize(pad - PIN_LENGTH, pad - PIN_LENGTH,
                     w + 2*PIN_LENGTH, h + 2*PIN_LENGTH)
