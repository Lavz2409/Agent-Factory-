from cli_app.commands import CommandParser
from cli_app.interfaces import OutputFormatter
from cli_app.notes import NoteManager


def main():
    output_formatter = OutputFormatter()
    note_manager = NoteManager()
    command_parser = CommandParser(note_manager, output_formatter)

    while True:
        command = input('> ')
        try:
            action = command_parser.parse(command)
            if action is not None:
                result = action()
                output_formatter.display(result)
        except Exception as e:
            output_formatter.display(f'Error: {e}')


if __name__ == '__main__':
    main()