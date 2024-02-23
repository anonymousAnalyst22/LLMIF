class ZbeeCommand:
    def __init__(self) -> None:
        self.cmd_id = -1
        self.description = ''
        self.mandatory = False
        self.payload = [] # A list of ZbeeParam objects
