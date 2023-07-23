class SSHOutput:
    host: str = None
    command: str = None
    output: str = None

    def __init__(self, host=None, command=None, output=None):
        self.host = host
        self.command = command
        self.output = output

    def get_raw_output(self):
        return self.output

    def get_command(self):
        return self.command

    def get_host(self):
        return self.host
