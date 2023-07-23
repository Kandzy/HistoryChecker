from configparser import ConfigParser
from configparser import NoOptionError
from configparser import NoSectionError


class Config:
    config_dir = "./Config/data/"
    config: ConfigParser = None
    config_file: str = None

    def __init__(self):
        self.config = ConfigParser()

    def set_config_file(self, config):
        self.config_file = config
        full_path = self.config_dir + config
        self.config.read(full_path)
        return self

    def get_data(self, section, option):
        try:
            return self.config.get(section, option)
        except (ValueError, NoOptionError) as e:
            print(f"Caught an error: {type(e).__name__}: {e}")

    def _add_section(self, section):
        self.config.add_section(section)

        return self

    def _set_data(self, section, option, value):
        try:
            self.config.set(section, option, value)
        except (NoSectionError, NoOptionError) as e:
            print(f"Caught an error during writing config: {type(e).__name__}: {e}")

        return self

    def _save_changes(self):
        try:
            with open(f'{self.config_dir}{self.config_file}', 'w') as configfile:
                self.config.write(configfile)
        except (NoSectionError, NoOptionError) as e:
            print(f"Caught an error during writing config: {type(e).__name__}: {e}")
