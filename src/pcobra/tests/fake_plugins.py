from cobra.cli.plugin import PluginCommand


class GoodPlugin(PluginCommand):
    name = "good"
    version = "1.0"
    description = "good plugin"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.description)
        parser.set_defaults(cmd=self)

    def run(self, args):
        pass


class NotPlugin:
    """Class that does not implement PluginInterface"""
    pass


class BadInitPlugin(PluginCommand):
    name = "badinit"

    def __init__(self):
        raise RuntimeError("boom")

    def register_subparser(self, subparsers):
        pass

    def run(self, args):
        pass
