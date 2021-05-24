from django.core.management.commands.dumpdata import Command as DumpDataCommand


class Command(DumpDataCommand):

    def handle(self, *app_labels, **options):
        # override options, app_labels and code method

        # with or without ...
        super(Command, self).handle(*app_labels, **options)
