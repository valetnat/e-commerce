from django import forms
import os
from django.conf import settings

IMPORT_FOLDER_PATH = settings.IMPORT_FOLDER


class ImportForm(forms.Form):
    files = forms.MultipleChoiceField(
        choices=[
            (file, file)
            for file in os.listdir(os.path.abspath(IMPORT_FOLDER_PATH))
            if os.path.isfile(os.path.join(IMPORT_FOLDER_PATH, file))
        ],
        label="Выбирете файл(ы) для импорта. *Если ни один файл не выбран, "
        "импорт будет инициирован из всех указанных файлов:",
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )

    mail_to = forms.EmailField(
        label="Адрес для отправки отчета:", widget=forms.EmailInput(attrs={"placeholder": "example@gmail.com"})
    )
