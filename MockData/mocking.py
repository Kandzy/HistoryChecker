class Mock:
    _file: str = None

    def __init__(self, file=None):
        self._file = file

    def get_content(self):
        # Open the file in read mode
        file_path = self.get_file_path()

        if not file_path:
            raise MockException("File is not set.")

        file = open(file_path, "r")
        # Read the entire contents of the file
        file_contents = file.read()
        # Close the file
        file.close()
        # Print the file contents
        return file_contents

    def change_mock_file(self, file):
        self._file = file

    def get_file_path(self):
        if not self._file:
            return ''

        return "./MockData/data/" + self._file


class MockException(Exception):
    pass
