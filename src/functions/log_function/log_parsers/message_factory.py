from .default_parser import DefaultParser
from .regex_parser import RegexParser
from .model_distributor_parser import ModelDistributorParser


class MessageFactory:
    def build_message(self, log_string: str, blob_name: str, source: str):

        default_parser = DefaultParser()
        regex_parser = RegexParser()
        model_distributor_parser = ModelDistributorParser()

        parsers = [regex_parser, model_distributor_parser]

        for p in parsers:
            if p.can_parse(log_string):
                return p.parse(log_string, blob_name, source)

        return default_parser.parse(log_string, blob_name, source)
