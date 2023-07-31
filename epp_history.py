from datetime import datetime, timedelta
import getpass
from MockData.mocking import Mock
from Parser.parser import Parser
from SSH.ssh_connect import SSHConnect, SSHConnectionError
from Config.ssh_config import SSHConfig
from SSH.ssh_output import SSHOutput


class Client:
    options: list = []
    password = None
    ssh_config = None
    reset_config: bool = False
    exit = None

    def __init__(self, argv):
        del argv[0]
        self.options = argv

    def start(self):
        self._process_options()
        ssh_config_builder = SSHConfigBuilder()
        self.ssh_config = ssh_config_builder.prepare_config()

        if not ssh_config_builder.is_new_config and self.reset_config:
            self.ssh_config = ssh_config_builder.force_update()

        self._request_password()

        while True:
            self._read_command()

            if self.exit:
                break

    def _read_command(self):
        print("1. Check domain EPP history\n"
              "2. Update Config\n"
              "3. Update Password\n"
              "4. Execute mocked data\n"
              "5. Exit script\n")
        command = int(input("Select action: "))

        if command == 1:
            EPPHistoryChecker().run(self.ssh_config, self.password)
        elif command == 2:
            SSHConfigBuilder().force_update()
        elif command == 3:
            self._request_password()
        elif command == 4:
            filename = input("Mocked Filename: ")
            mock = Mock(filename)
            MockEPPHistoryChecker().run_mock(mock)
        elif command == 5:
            self.exit = True
        else:
            print("\033[31mCommand selection error\033[0m")

    def _process_options(self):
        if '--reset' in self.options:
            self.reset_config = True

    def _request_password(self):
        self.password = getpass.getpass("Enter Your Password: ")


class EPPHistoryChecker:
    domain_name: str = None
    ssh: SSHConnect = None
    check_since_month: str = None
    check_to_month: str = None
    commands: list = []

    # Execution Flags
    change_domain = True
    change_period = True
    execute_command = True

    def run(self, ssh_config, password):
        try:
            self._connect_to_ssh(ssh_config, password)
        except SSHConnectionError as e:
            print(f"\033[31m{e}\033[0m")
            return

        while True:
            if self.change_domain:
                self._get_domain()

            if self.change_period:
                self._get_period()

            if self.execute_command:
                responses = self._run_execution()
                self.parse_responses(responses)

                # parser.print_result()

            print("1. Check again\n"
                  "2. Change domain\n"
                  "3. Change_period\n"
                  "4. Exit script\n")
            action = int(input("Select action for checker: "))

            if action == 1:
                self.execute_command = True
            elif action == 2:
                self.change_domain = True
            elif action == 3:
                self.change_period = True
            elif action == 4:
                break
            else:
                print("\033[31mError during processing EPP check script\033[0m")
                break

        self._close_connection()

    def _run_execution(self):
        self._build_commands()
        responses = self._execute_command()
        return responses

    def parse_responses(self, responses: list[SSHOutput]):
        parser = Parser()

        for response in responses:
            raw_text_response = response.get_raw_output()

            with open(f"{self.domain_name}_result_raw", 'a') as file:
                file.write(raw_text_response)

            occurrences = self.parce_raw_text(parser, raw_text_response)
            self.write_parsed_file(occurrences)

    def parce_raw_text(self, parser: Parser, response):
        parser.parce_response(self.domain_name, response)
        return parser.get_occurrences()

    def write_parsed_file(self, occurrences):
        for occurrence in occurrences:
            with open(f"{self.domain_name}_result_parsed", 'a') as file:
                file.write(occurrence + "\n")

    def _connect_to_ssh(self, ssh_config, password):
        self.ssh = SSHConnect(host=ssh_config.host, login=ssh_config.username, password=password)

    def _build_commands(self):
        self.commands = []
        date_since = datetime.strptime(self.check_since_month, "%Y-%m")
        date_to = datetime.strptime(self.check_to_month, "%Y-%m")
        months = [date_since.strftime("%Y-%m")]
        tld = self.domain_name.split('.')[-1]

        while date_since < date_to:
            date_since += timedelta(days=32)  # Adding 32 days because of varying month lengths
            date_since = date_since.replace(day=1)  # Set the day to 1 to ensure it's the first day of the month
            months.append(date_since.strftime("%Y-%m"))

        for month in months:
            self.commands.append(f'zgrep -A 30 -B 10 \'{self.domain_name}\' /backups/epp/epp_logs/*/internal_req-{tld}'
                                 f'.log.{month}*')

    def _execute_command(self) -> list[SSHOutput]:
        self.ssh.clear_output()

        for command in self.commands:
            self.ssh.execute(command)

        self.execute_command = False
        return self.ssh.get_all_outputs()

    def _close_connection(self):
        self.ssh.close_connection()

    def _get_domain(self):
        self.domain_name = input("Domain to check: ")
        self.change_domain = False

    def _get_period(self):
        self.check_since_month = input("Check since(Y-m): ")
        self.check_to_month = input("Check to(Y-m): ")
        self.change_period = False


class SSHConfigBuilder:
    is_new_config: bool = False
    host: str = None
    port: int = None
    username: str = None
    ssh_config: SSHConfig = None

    def prepare_config(self):
        self._read_config()
        self._check_credentials()

        return self.ssh_config

    def force_update(self):
        self._update_config()
        return self.ssh_config

    def _read_config(self):
        self.ssh_config = SSHConfig()
        self.ssh_config.read()

    def _check_credentials(self):
        if not self.ssh_config.host or not self.ssh_config.port or not self.ssh_config.username:
            self._update_config()

    def _update_config(self):
        self._read_config()
        self._set_host()
        self._set_port()
        self._set_username()
        self.ssh_config.update(
            host=self.host,
            port=self.port,
            username=self.username
        ).save()
        self.is_new_config = True

    def _set_host(self):
        while True:
            self.host = input("Set Hostname:")

            if self.host:
                break
            else:
                print("\033[31mHostname set Incorrectly or empty\033[0m")

    def _set_port(self):
        while True:
            self.port = int(input("Set Port:"))

            if self.port and isinstance(self.port, int):
                break
            else:
                print("\033[31mPort set Incorrectly or empty\033[0m")

    def _set_username(self):
        while True:
            self.username = input("Set Username:")

            if self.username:
                break
            else:
                print("\033[31mUsername set Incorrectly or empty\033[0m")


class MockEPPHistoryChecker(EPPHistoryChecker):
    def run_mock(self, mock: Mock):
        self._get_domain()
        response = mock.get_content()
        occurrences = self.parce_raw_text(Parser(), response)
        self.write_parsed_file(occurrences)
