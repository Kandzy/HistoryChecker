import re


class Parser:

    def __init__(self):
        self.domain_occurrences: list = []
        self.domain_name = None
        self._response = None

    def print_result(self):
        # # Print the occurrences
        for occurrence in self.domain_occurrences:
            print(occurrence)

    def get_occurrences(self):
        return self.domain_occurrences

    def parce_response(self, domain_name=None, response=None):
        self.domain_name = domain_name
        self._response = response

        print("Parsing ...")
        clear_response = self._clear_raw_response()
        occurrences = self._get_occurrences(clear_response)
        self._parce_occurrences(occurrences)

    def _parce_occurrences(self, occurrences: list):
        append_next_occurrence = False

        for occurrence in occurrences:

            domain_match = False

            if not append_next_occurrence:
                domain_match = re.search(r'(' + self.domain_name + ')', occurrence)
            else:
                match_trId = re.search(r"(<trId>" + trId + "</trId>)", occurrence)

                if match_trId:
                    self.domain_occurrences.append(occurrence)

                append_next_occurrence = False
                trId = ''

            if domain_match:
                domain = domain_match.group(1)
                self.domain_occurrences.append(occurrence)
                command_match = re.search(r'(?:CheckDomain|UpdateDomain|DeleteDomain)>', occurrence)

                if command_match:
                    trId_match = re.search(r"<trId>(.*?)</trId>", occurrence)

                    if trId_match:
                        trId = trId_match.group(1)

                    append_next_occurrence = True

    def _clear_raw_response(self):
        # Remove text between "/backups/epp/epp_logs" and "gz-"
        return re.sub(r'/backups/epp/epp_logs.*?gz', '', self._response)

    def _get_occurrences(self, text):
        # Find all occurrences of the text between "<?xml version="1.0" and </EPP>"
        return re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}.*?<\?xml version="1\.0".*?</EPP>',
                          text, re.DOTALL)
