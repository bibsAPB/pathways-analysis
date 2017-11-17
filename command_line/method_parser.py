import inspect
import re
from collections import defaultdict

from command_line.parser import Parser, Argument


def analyze_docstring(docstring: str):
    """Analyze docstring and collect arguments with descriptions.

    All arguments have to start with a lowercase letter, be followed
    with a colon (:) and then with the description of the argument.
    """
    help_strings = defaultdict(list)
    collect_help = False
    definition = re.compile(r'(?P<name>.+?):(?P<value>.*)')
    args_sections = ['Arguments:', 'Args:']
    empty_lines = 0
    argument = None

    for line in docstring.split('\n'):
        line = line.strip()

        if not line:
            empty_lines += 1
            collect_help = False
        else:
            empty_lines = 0

        if any(line.startswith(section) for section in args_sections):
            collect_help = True
            continue

        if collect_help:
            match = definition.match(line)
            if match:
                argument = match.group('name')
                if argument[0].isupper():
                    collect_help = False
                    continue
                value = match.group('value').lstrip()
                if value:
                    help_strings[argument].append(value)
            elif argument:
                help_strings[argument].append(line)

    for key, value in help_strings.items():
        help_strings[key] = ' '.join(value)

    return help_strings


def is_set(value):
    return not (value == inspect._empty)


def empty_to_none(value):
    if not is_set(value):
        return None
    return value


class MethodParser(Parser):

    @property
    def help(self):
        if hasattr(self.method, 'help'):
            return self.method.help
        return super().help

    @property
    def description(self):
        return self.help

    def __init__(self, method, **kwargs):
        self.method = method
        restricted_names = ['name']

        # add arguments defined in a Method subclass
        for name, attribute in vars(method).items():
            if isinstance(attribute, Parser) or isinstance(attribute, Argument):
                setattr(self, name, attribute)

        # introspect method.__init__
        signature = inspect.signature(method)
        docstring = method.__init__.__doc__ or ''

        docstring_help = analyze_docstring(docstring)

        for name, parameter in signature.parameters.items():
            # ignore *args and **kwargs
            if parameter.kind in [parameter.VAR_KEYWORD, parameter.VAR_POSITIONAL]:
                continue
            if name in restricted_names:
                raise ValueError(f'"{name}" cannot be used as a name of argument')
            if not hasattr(self, name):
                argument = Argument(
                    default=empty_to_none(parameter.default),
                    type=empty_to_none(parameter.annotation),
                    optional=is_set(parameter.default),
                    help=docstring_help.get(name, None)

                )
                setattr(self, name, argument)
            else:
                argument = getattr(self, name)
                if not hasattr(argument, 'help') or not argument.help:
                    argument.help = docstring_help.get(name, None)

        super().__init__(**kwargs)
