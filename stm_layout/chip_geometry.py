
BGA_Y_TO_LABEL = 'ABCDEFGHJKLMNPRTUVWY'
BGA_LABEL_TO_Y = {label: i for i, label in enumerate(BGA_Y_TO_LABEL)}


class TSSOP:
    def __init__(self, height, pins):
        self.height    = height
        self.pin_index = [None]*len(pins)
        for k, p in pins.items():
            self.pin_index[int(k)] = p

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
        if i < self.chip.height:
            i = 2*self.chip.height - i - 1
        return self.pin_index[i]
