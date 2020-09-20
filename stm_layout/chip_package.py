
BGA_Y_TO_LABEL = 'ABCDEFGHJKLMNPRTUVWY'
BGA_LABEL_TO_Y = {label: i for i, label in enumerate(BGA_Y_TO_LABEL)}


class Package:
    def __init__(self, width, height):
        self.width  = width
        self.height = height
        self.pins   = []
        for _ in range(width):
            self.pins.append([None]*self.height)


class BGA(Package):
    class Cursor:
        def __init__(self, chip):
            self.chip = chip
            self.pos = (-1, 0)
            self.right()

        @property
        def pin(self):
            return self.chip.pins[self.pos[0]][self.pos[1]]

        def move(self, delta):
            new_pos = self.pos
            while True:
                new_pos = (new_pos[0] + delta[0], new_pos[1] + delta[1])
                if new_pos[0] < 0 or new_pos[0] >= self.chip.width:
                    return
                if new_pos[1] < 0 or new_pos[1] >= self.chip.height:
                    return
                if self.chip.pins[new_pos[0]][new_pos[1]] is None:
                    continue

                self.pos = new_pos
                return

        def left(self):
            self.move((-1, 0))

        def right(self):
            self.move((1, 0))

        def up(self):
            self.move((0, -1))

        def down(self):
            self.move((0, 1))

    def __init__(self, width, height):
        super(BGA, self).__init__(width, height)

    def __getitem__(self, key):
        x = int(key[1:], 10) - 1
        y = BGA_LABEL_TO_Y[key[0]]
        return self.pins[x][y]

    def __setitem__(self, key, val):
        x = int(key[1:], 10) - 1
        y = BGA_LABEL_TO_Y[key[0]]
        self.pins[x][y] = val

    def cursor(self):
        return BGA.Cursor(self)


class LQFP(Package):
    class Cursor:
        def __init__(self, chip):
            self.chip = chip
            self.pos  = (0, 1)

        @property
        def pin(self):
            return self.chip.pins[self.pos[0]][self.pos[1]]

        def left(self):
            if self.pos[1] == 0:
                self.counterclockwise()
            elif self.pos[1] == self.chip.height - 1:
                self.clockwise()

        def right(self):
            if self.pos[1] == 0:
                self.clockwise()
            elif self.pos[1] == self.chip.height - 1:
                self.counterclockwise()

        def up(self):
            if self.pos[0] == 0:
                self.clockwise()
            elif self.pos[0] == self.chip.width - 1:
                self.counterclockwise()

        def down(self):
            if self.pos[0] == 0:
                self.counterclockwise()
            elif self.pos[0] == self.chip.width - 1:
                self.clockwise()

        def rotate(self, delta):
            while True:
                if self.pos[0] == 0:
                    self.pos = (0, self.pos[1] - delta)
                if self.pos[1] == 0:
                    self.pos = (self.pos[0] + delta, 0)
                if self.pos[0] == self.chip.width - 1:
                    self.pos = (self.chip.width - 1, self.pos[1] + delta)
                if self.pos[1] == self.chip.height - 1:
                    self.pos = (self.pos[0] - delta, self.chip.height - 1)
                if self.pin is not None:
                    return

        def clockwise(self):
            self.rotate(1)

        def counterclockwise(self):
            self.rotate(-1)

    def __init__(self, width, height):
        super(LQFP, self).__init__(width + 2, height + 2)

    def __getitem__(self, key):
        key = int(key, 10) - 1
        if 0 <= key < self.height - 2:
            return self.pins[0][key]
        key -= self.height - 2
        if 0 <= key < self.width - 2:
            return self.pins[key][self.height - 1]
        key -= self.width - 2
        if 0 <= key < self.height - 2:
            return self.pins[self.width - 1][self.height - 1 - key - 1]
        key -= self.height - 2
        if 0 <= key < self.width - 2:
            return self.pins[self.width - 1 - key - 1][0]
        raise KeyError

    def __setitem__(self, key, val):
        key = int(key, 10) - 1
        if 0 <= key < self.height - 2:
            self.pins[0][key + 1] = val
            return
        key -= self.height - 2
        if 0 <= key < self.width - 2:
            self.pins[key + 1][self.height - 1] = val
            return
        key -= self.width - 2
        if 0 <= key < self.height - 2:
            self.pins[self.width - 1][self.height - 1 - key - 1] = val
            return
        key -= self.height - 2
        if 0 <= key < self.width - 2:
            self.pins[self.width - 1 - key - 1][0] = val
            return
        raise KeyError

    def cursor(self):
        return LQFP.Cursor(self)


class TSSOP(Package):
    class Cursor:
        def __init__(self, chip):
            self.chip = chip
            self.pos = (-1, 0)
            self.right()

        @property
        def pin(self):
            return self.chip.pins[self.pos[0]][self.pos[1]]

        def move(self, delta):
            new_pos = self.pos
            while True:
                new_pos = (new_pos[0] + delta[0], new_pos[1] + delta[1])
                if new_pos[0] < 0 or new_pos[0] >= 2:
                    return
                if new_pos[1] < 0 or new_pos[1] >= self.chip.height:
                    return
                if self.chip.pins[new_pos[0]][new_pos[1]] is None:
                    continue

                self.pos = new_pos
                return

        def left(self):
            self.move((-1, 0))

        def right(self):
            self.move((1, 0))

        def up(self):
            self.move((0, -1))

        def down(self):
            self.move((0, 1))

    def __init__(self, height):
        super(TSSOP, self).__init__(2, height)

    def __getitem__(self, key):
        key = int(key, 10) - 1
        x   = key // self.height
        y   = key % self.height
        return self.pins[x][y]

    def __setitem__(self, key, val):
        key = int(key, 10) - 1
        x   = key // self.height
        y   = key % self.height
        self.pins[x][y] = val

    def cursor(self):
        return TSSOP.Cursor(self)
