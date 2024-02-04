from django.test import TestCase
from .tasks import load_files


class ImportTest(TestCase):
    def test_load_data(self):
        email = "example@gmail.com"
        files = (
            "file_not_founded_error",
            "successed_file.json",
            "format_error_file.jsn",
            "format_error_file_2",
            "json_error_file.json",
            "partially_successed_file.json",
        )

        result = load_files(files, email)

        self.assertIsNone(result)
