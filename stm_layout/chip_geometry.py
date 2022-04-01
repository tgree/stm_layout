class TSSOP:
    '''
    A TSSOP has pins down the left and right edges only.  Pin keys are text-
    encoded integer strings starting from '1', '2', ... 'N', where N is the
    number of pins.  This is the simplest type of geometry.
    '''
    def __init__(self, name, height, pins):
        assert len(pins) == height*2
        self.name      = name
        self.height    = height
        self.pin_index = [None]*len(pins)
        for k, p in pins.items():
            self.pin_index[int(k) - 1] = p

    def up(self, p):
        i = int(p.key) - 1
        if i < self.height:
            i = max(0, i - 1)
        else:
            i = min(2*self.height - 1, i + 1)
        return self.pin_index[i]

    def down(self, p):
        i = int(p.key) - 1
        if i < self.height:
            i = min(self.height - 1, i + 1)
        else:
            i = max(self.height, i - 1)
        return self.pin_index[i]

    def left(self, p):
        i = int(p.key) - 1
        if i >= self.height:
            i = 2*self.height - i - 1
        return self.pin_index[i]

    def right(self, p):
        i = int(p.key) - 1
        if i < self.height:
            i = 2*self.height - i - 1
        return self.pin_index[i]


class LQFP:
    '''
    An LQFP has pins around the four edges of the chip.  Pin keys are text-
    encoded integer strings starting from '1', '2', ... 'N', where N is the
    number of pins.
    '''
    def __init__(self, name, width, height, pins):
        assert len(pins) == (width + height)*2
        self.name      = name
        self.width     = width
        self.height    = height
        self.pin_index = [None]*len(pins)
        for k, p in pins.items():
            self.pin_index[int(k) - 1] = p

    def up(self, p):
        i = int(p.key) - 1
        if i < self.height:
            # Left side.
            i = (i - 1) % len(self.pin_index)
        elif i < self.height + self.width:
            # Bottom side.
            i = 2*self.width + 3*self.height - i - 1
        elif i < 2*self.height + self.width:
            # Right side.
            i = i + 1
        else:
            # Top side.
            pass
        return self.pin_index[i]

    def down(self, p):
        i = int(p.key) - 1
        if i < self.height:
            # Left side.
            i = i + 1
        elif i < self.height + self.width:
            # Bottom side.
            pass
        elif i < 2*self.height + self.width:
            # Right side.
            i = i - 1
        else:
            # Top side.
            i = 2*self.width + 3*self.height - i - 1
        return self.pin_index[i]

    def left(self, p):
        i = int(p.key) - 1
        if i < self.height:
            # Left side.
            pass
        elif i < self.height + self.width:
            # Bottom side.
            i = i - 1
        elif i < 2*self.height + self.width:
            # Right side.
            i = self.height - (i + 1 - (self.height + self.width))
        else:
            # Top side.
            i = (i + 1) % len(self.pin_index)
        return self.pin_index[i]

    def right(self, p):
        i = int(p.key) - 1
        if i < self.height:
            # Left side.
            i = self.height - (i + 1 - (self.height + self.width))
        elif i < self.height + self.width:
            # Bottom side.
            i = i + 1
        elif i < 2*self.height + self.width:
            # Right side.
            pass
        else:
            # Top side.
            i = i - 1
        return self.pin_index[i]


class BGA:
    '''
    A BGA has pins in a grid pattern, however the grid pattern may have gaps if
    no ball is present at a particular location.  This is common when there is
    a ring of balls encircling a box of VCC/GND pins in the middle of the chip.
    Pin keys are encoded using a letter for the Y position and an integer for
    the X position.  Some letters are skipped because they look similar to
    numbers.  So, we have strings such as 'A1', 'B1', 'C23', etc.
    '''
    Y_TO_LABEL = 'ABCDEFGHJKLMNPRTUVWY'
    LABEL_TO_Y = {label: i for i, label in enumerate(Y_TO_LABEL)}

    def __init__(self, name, width, height, pins):
        assert len(pins) <= width*height
        self.name      = name
        self.width     = width
        self.height    = height
        self.pin_index = [None]*(width*height)
        for k, p in pins.items():
            self.pin_index[self._key_to_index(k)] = p

    def _coord_to_index(self, x, y):
        return y*self.width + x

    def _key_to_coord(self, k):
        x = int(k[1:], 10) - 1
        y = BGA.LABEL_TO_Y[k[0]]
        return x, y

    def _key_to_index(self, k):
        x, y = self._key_to_coord(k)
        return self._coord_to_index(x, y)

    def _delta(self, p, dx, dy):
        x, y = self._key_to_coord(p.key)
        while 0 <= x + dx < self.width and 0 <= y + dy < self.height:
            x += dx
            y += dy
            p2 = self.pin_index[self._coord_to_index(x, y)]
            if p2:
                return p2
        return p

    def get_pin(self, x, y):
        return self.pin_index[self._coord_to_index(x, y)]

    def up(self, p):
        return self._delta(p, 0, -1)

    def down(self, p):
        return self._delta(p, 0, 1)

    def left(self, p):
        return self._delta(p, -1, 0)

    def right(self, p):
        return self._delta(p, 1, 0)
