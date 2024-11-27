class Segment:
    def __init__(self, start_address, data):
        self.data = data
        self.start_address = start_address

    def get_address(self):
        return self.start_address

    def get_data(self):
        return self.data