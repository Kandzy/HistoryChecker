import os
from Config.config import Config


class SSHConfig(Config):
    file_name = "config.ini"
    host: str = None
    port: int = None
    username: str = None
    password: str = None
    section = 'SSH'

    def read(self):
        self.create_config_if_doesnt_exist()
        self.set_config_file(self.file_name)
        self.host = self.get_data(self.section, "host")
        self.port = self.get_data(self.section, "port")
        self.username = self.get_data(self.section, "username")

    def update_option(self, option, value):
        if option not in ['host', 'port', 'username']:
            raise ValueError("Incorrect option value set")

        setattr(self, option, value)

    def update(self, host=None, port=None, username=None):
        if host:
            self.host = host

        if username:
            self.username = username

        if port:
            self.port = port

        return self

    def save(self):
        if self.host:
            self._set_data(section=self.section, option='host', value=self.host)

        if self.username:
            self._set_data(section=self.section, option='username', value=self.username)

        if self.port:
            self._set_data(section=self.section, option='port', value=str(self.port))

        return self._save_changes()

    def create_config_if_doesnt_exist(self):
        if not os.path.exists(self.config_dir + self.file_name):
            if not os.path.exists(self.config_dir) and not os.path.isdir(self.config_dir):
                os.mkdir(self.config_dir)

            self._add_section('SSH').update(host='', port=22, username='').save()
