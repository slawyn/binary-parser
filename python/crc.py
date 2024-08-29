class Crc32:
    ''' Corresponds to address:4,crc32:Li,0xFFFFFFFFF;start_address-end_address
    '''

    def __init__(self, size=4, unit_size=4, start_value=0xFFFFFFFF):
        self.size = size
        self.unit_size = unit_size
        self.start_value = start_value
        self.table = []
        self._create_lookup_table()

    def _mirror(self, orig, size):
        one = 1
        d = 0
        r = 0
        for d in range(8 * size):

            if (orig & (one << d)):
                r |= ((one << (8 * size - 1)) >> d)

        return r

    def _create_lookup_table(self):
        rem = 0
        mask = 1
        left = (self.size - 1) * 8
        mask <<= (self.size * 8 - 1)
        for i in range(256):
            rem = i << left
            for j in range(8):
                if (rem & mask):
                    rem = (rem << 1) ^ 0x4C11DB7
                else:
                    rem <<= 1

            self.table.append(rem)

    def calculate(self, buf):
        mSum = self.start_value
        stack = []
        for byte in buf:
            stack.append(byte)
            if len(stack) == self.unit_size:
                while len(stack) > 0:
                    index = ((mSum >> 24) ^ stack.pop()) & 0xFF
                    t = self.table[index]
                    mSum = (t ^ (mSum << 8)) & 0xFFFFFFFF

        return mSum


