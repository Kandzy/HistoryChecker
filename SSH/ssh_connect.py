from SSH.ssh_output import SSHOutput
import socket
import paramiko


class SSHConnect:
    _outputs = []
    _last_output: SSHOutput = None
    _client: paramiko.SSHClient = None
    _host: str = None

    def __init__(self, host='', login='', password='', port=22):
        self._host = host

        try:
            # Create an SSH client
            self._client = paramiko.SSHClient()
            # Automatically add the remote server's host key (not recommended for production use)
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # Connect to the remote server
            print(f"\033[33mConnecting {login} to {self._host}:{port}\033[0m")
            self._client.connect(hostname=host, port=port, username=login, password=password)
            print(f"\033[32mConnected to {self._host} \033[0m")
        except (paramiko.ssh_exception.AuthenticationException, paramiko.ssh_exception.SSHException, socket.error) as e:
            raise SSHConnectionError(f"SSH connection to {self._host} failed:{e}")

    def execute(self, command: str = ''):
        if not isinstance(command, str):
            raise TypeError('Command must be a string')

        if not command:
            raise ValueError('Command should not be empty')

        print(f"\033[33m Executing command: {command} \033[0m")
        # Execute a command on the remote server
        stdin, stdout, stderr = self._client.exec_command(command)
        # Print the output of the command
        ssh_output = stdout.read().decode()
        self._add_output(command, ssh_output)
        print(f"\033[32mCommand executed: {command} \033[0m\n")
        return self._last_output

    def get_last_output(self):
        return self._last_output

    def get_all_outputs(self):
        return self._outputs

    def clear_output(self):
        self._outputs = []

    def close_connection(self):
        transport = self._client.get_transport()

        if transport is None or not transport.is_alive():
            return

        try:
            self._client.close()
            print(f"\033[32mSSH connection closed to {self._host}.\033[0m")
        except Exception as e:
            print(f"\033[31mError while closing the SSH connection to host{self._host}:\033[0m", str(e))

    def _add_output(self, command, output):
        output = SSHOutput(command=command, output=output, host=self._host)
        self._outputs.append(output)
        self._last_output = output

    def __del__(self):
        self.close_connection()


class SSHConnectionError(Exception):
    pass
