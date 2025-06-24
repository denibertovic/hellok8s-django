import logging
import re


class RequestPathFilter(logging.Filter):
    def __init__(self, *args, path_re, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_filter = re.compile(path_re)

    def filter(self, record):
        req_path = record.args["U"]
        if not self.path_filter.match(req_path):
            return True  # log this entry
        # ... additional conditions can be added here ...
        return False  # do not log this entry


def on_starting(server):
    server.log.access_log.addFilter(RequestPathFilter(path_re=r"^/healthz/$"))
