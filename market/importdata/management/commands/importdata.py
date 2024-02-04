from django.core.management import BaseCommand
from importdata.tasks import load_files
from django.conf import settings


class Command(BaseCommand):
    help = (
        "Import products data into the database from json"
        "file(s) located at '%s' folder. *If no files are selected,"
        "the import will be initiated from all files in the directory."
        "**WARNING For task works properly Celery should be running" % settings.IMPORT_FOLDER
    )
    # missing_args_message = 'No files'

    def add_arguments(self, parser):
        parser.add_argument(
            "args",
            metavar="file",
            nargs="*",
            help="File(s) label(s).",
        )

        parser.add_argument(
            "-e",
            "--email",
            default=None,
            help="Address to mail a report to.",
        )

    def handle(self, *files, **options):
        load_files.delay(files, options["email"])
        if options["email"]:
            self.stdout.write(
                "Команда 'Importdata' поставлена в очередь задач на выполнение. "
                "По завершению будет отправлен отчет на почту: %s" % options["email"]
            )
        else:
            self.stdout.write("Команда 'Importdata' поставлена в очередь задач на выполнение. ")
