import re
import tkinter.font

from .tk_elems import TKBase
from . import xplat


class InfoText:
    def __init__(self, canvas, x, y, **kwargs):
        self.text      = canvas.add_text(x, y, **kwargs)
        bbox           = self.text.bbox()
        width          = canvas._canvas.winfo_reqwidth() - bbox[0] - 5
        height         = bbox[3] - bbox[1]
        self.fill_rect = canvas.add_rectangle(bbox[0], bbox[1], width, height,
                                              outline='')
        self.fill_rect.tag_lower(self.text)

    def set_text(self, text):
        self.text.set_text(text)

    def set_bg(self, bg_color):
        self.fill_rect.set_fill(bg_color)


class Workspace(TKBase):
    def __init__(self, chip, elem_fill, hilite_fill, select_fill, re_fill):
        super().__init__()

        self.chip         = chip
        self.elem_fill    = elem_fill
        self.hilite_fill  = hilite_fill
        self.select_fill  = select_fill
        self.re_fill      = re_fill
        self.hilited_pin  = None
        self.selected_pin = None
        self.re_pins      = set()
        self.pin_elems    = []
        self.regex        = None

        d = chip.part.get_driver('rcc')
        if d and 'max-frequency' in d:
            self.max_freq_mhz = '%.0f MHz' % (int(d['max-frequency'][-1]) / 1e6)
        else:
            self.max_freq_mhz = ''

        self.label_font = tkinter.font.Font(family=xplat.LABEL_FONT[0],
                                            size=xplat.LABEL_FONT[1])
        self.pin_font   = tkinter.font.Font(family=xplat.PIN_FONT[0],
                                            size=xplat.PIN_FONT[1])
        self.info_font  = tkinter.font.Font(family=xplat.INFO_FONT[0],
                                            size=xplat.INFO_FONT[1])
        dy = self.info_font.metrics('linespace')

        w = 300
        h = 0
        for _, p in self.chip.pins.items():
            for f in p.alt_fns:
                w = max(w, self.info_font.measure(f))
            for f in p.add_fns:
                w = max(w, self.info_font.measure(f))
            h = max(h, len(p.add_fns))
        self.info_width   = w + 5
        self.info_height  = 15 + 30 + (h + 25) * dy + 15
        self.info_canvas  = self.add_canvas(self.info_width,
                                            self.info_height, 1, 0,
                                            sticky='nes')
        self.mcu_canvas   = self._make_mcu_canvas()
        self.mcu_canvas.register_key_pressed(self.mcu_key_pressed)

        sv = tkinter.StringVar()
        sv.trace_add('write', lambda n, i, m: self.set_regex(sv.get()))
        e = self.info_canvas.add_entry(font=self.label_font, width=40,
                                       textvariable=sv)
        e._widget.configure(highlightthickness=3)
        #print(e._widget.configure())

        y  = 15
        self.info_canvas.add_text(
                15, y, font=self.info_font, text='Regex:', anchor='nw')
        y += dy
        self.info_canvas.add_window(15, y, e, anchor='nw')
        e.focus_set()
        y += 30

        y += dy
        self.info_canvas.add_text(
                15, y, font=self.info_font, text='Pin Info', anchor='nw')
        y += dy
        self.pin_name_text = InfoText(
                self.info_canvas, 15, y, font=self.info_font, anchor='nw')
        y += dy
        self.pin_pos_text = InfoText(
                self.info_canvas, 15, y, font=self.info_font, anchor='nw')
        y += 2*dy

        self.info_canvas.add_text(
                15, y, font=self.info_font, text='Alternate Functions',
                anchor='nw')
        self.info_af_texts = []
        for _ in range(16):
            y += dy
            self.info_af_texts.append(InfoText(
                self.info_canvas, 15, y, font=self.info_font, anchor='nw'))

        self.max_add_fns = 0
        for _, p in chip.pins.items():
            self.max_add_fns = max(self.max_add_fns, len(p.add_fns))

        y += 2*dy
        self.info_canvas.add_text(
                15, y, font=self.info_font, text='Additional Functions',
                anchor='nw')
        self.info_add_fns_texts = []
        for _ in range(self.max_add_fns):
            y += dy
            self.info_add_fns_texts.append(InfoText(
                self.info_canvas, 15, y, font=self.info_font, anchor='nw'))

        self.update_info(None)

        self.register_mouse_moved(self.mouse_moved)
        self.register_mouse_down(self.mouse_down)
        #self.register_key_pressed(self.key_pressed)
        #self.register_key_released(self.key_released)

    def update_info(self, pin_elem):
        if pin_elem is None:
            self.pin_name_text.set_text('')
            self.pin_name_text.set_bg('')
            self.pin_pos_text.set_text('')
            self.pin_pos_text.set_bg('')
            for i, t in enumerate(self.info_af_texts):
                t.set_text('')
                t.set_bg('')
            for t in self.info_add_fns_texts:
                t.set_text('')
                t.set_bg('')
            return

        self.pin_name_text.set_text(' Name: %s' % pin_elem.pin.full_name)
        if self.regex and self.regex.search(pin_elem.pin.full_name):
            self.pin_name_text.set_bg(self.re_fill)
        else:
            self.pin_name_text.set_bg('')
        self.pin_pos_text.set_text('  Pos: %s' % pin_elem.pin.key)
        if self.regex and self.regex.search(pin_elem.pin.key):
            self.pin_pos_text.set_bg(self.re_fill)
        else:
            self.pin_pos_text.set_bg('')

        for i, f in enumerate(pin_elem.pin.alt_fns):
            self.info_af_texts[i].set_text(' %2u: %s' % (i, f))
            if self.regex and self.regex.search(f):
                self.info_af_texts[i].set_bg(self.re_fill)
            else:
                self.info_af_texts[i].set_bg('')
        for i in range(len(pin_elem.pin.alt_fns), 16):
            self.info_af_texts[i].set_text('')
            self.info_af_texts[i].set_bg('')

        for i, f in enumerate(pin_elem.pin.add_fns):
            self.info_add_fns_texts[i].set_text(' %s' % f)
            if self.regex and self.regex.search(f):
                self.info_add_fns_texts[i].set_bg(self.re_fill)
            else:
                self.info_add_fns_texts[i].set_bg('')
        for i in range(len(pin_elem.pin.add_fns), self.max_add_fns):
            self.info_add_fns_texts[i].set_text('')
            self.info_add_fns_texts[i].set_bg('')

    def color_pin(self, pin_elem):
        if self.hilited_pin == pin_elem:
            pin_elem.set_fill(self.hilite_fill)
        elif self.selected_pin == pin_elem:
            pin_elem.set_fill(self.select_fill)
        elif pin_elem in self.re_pins:
            pin_elem.set_fill(self.re_fill)
        else:
            pin_elem.set_fill(self.elem_fill)

    def color_all_pins(self):
        for pe in self.pin_elems:
            self.color_pin(pe)

    def select_pin(self, pin_elem):
        prev_selected_pin = self.selected_pin
        self.selected_pin = pin_elem
        if prev_selected_pin:
            self.color_pin(prev_selected_pin)
        if self.selected_pin:
            self.color_pin(self.selected_pin)

        self.update_info(self.selected_pin)
        self.mcu_canvas.focus_set()

    def mouse_moved(self, _ws, ev, x, y):
        if ev.widget != self.mcu_canvas._canvas:
            prev_hilited_pin = self.hilited_pin
            self.hilited_pin = None
            if prev_hilited_pin:
                self.color_pin(prev_hilited_pin)
            return

        closest  = self.pin_elems[-1]
        distance = closest.distance_squared(x, y)
        for e in reversed(self.pin_elems):
            d = e.distance_squared(x, y)
            if d < distance:
                distance = d
                closest  = e

        if self.hilited_pin is not None:
            if closest == self.hilited_pin:
                return

        prev_hilited_pin = self.hilited_pin
        self.hilited_pin = closest
        if prev_hilited_pin:
            self.color_pin(prev_hilited_pin)
        self.color_pin(self.hilited_pin)

    def mouse_down(self, _ws, ev, _x, _y):
        if ev.widget != self.mcu_canvas._canvas:
            return
        if not self.hilited_pin:
            return

        self.select_pin(None if self.hilited_pin == self.selected_pin else
                        self.hilited_pin)

    def set_regex(self, regex):
        try:
            self.regex = re.compile(regex) if regex else None
        except Exception:
            self.regex = None

        self.re_pins.clear()
        if self.regex is not None:
            r = self.regex
            for pe in self.pin_elems:
                match = r.search(pe.pin.full_name)
                match = match or r.search(pe.pin.key)
                match = match or any(r.search(f) for f in pe.pin.alt_fns)
                match = match or any(r.search(f) for f in pe.pin.add_fns)
                if match:
                    self.re_pins.add(pe)

        self.color_all_pins()
        if self.selected_pin:
            self.update_info(self.selected_pin)

    def tab_pressed(self, _ws, ev, _x, _y):
        print('Tab pressed')

    def shift_tab_pressed(self, _ws, ev, _x, _y):
        print('Shift-Tab pressed')

    def mcu_key_pressed(self, _ws, ev, _x, _y):
        if not self.selected_pin:
            return
        if ev.keysym == 'Left':
            self.handle_left()
        elif ev.keysym == 'Right':
            self.handle_right()
        elif ev.keysym == 'Up':
            self.handle_up()
        elif ev.keysym == 'Down':
            self.handle_down()

    def mcu_key_released(self, _ws, ev, _x, _y):
        print('Key Released: %s' % ev.keysym)
