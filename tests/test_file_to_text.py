import pytest
from werkzeug.datastructures import FileStorage

from src.file_to_text import UnsupportedFiletypeError, file_to_text

@pytest.mark.parametrize("filename, routed_function", [
    ('test.pdf', 'src.file_to_text.pdf_to_text'),
    ('test.png', 'src.file_to_text.img_to_text'),
    ('test.jpg', 'src.file_to_text.img_to_text'),
    ('test.jpeg', 'src.file_to_text.img_to_text'),
])
def test_success(mocker, filename, routed_function):
    mocker.patch(routed_function, return_value='test content')

    file = FileStorage(filename=filename)
    assert file_to_text(file) == 'test content'

@pytest.mark.parametrize("filename", [
    'song.mp3',
    'doc.pdf.gz',
    'sample.png.zip'
])
def test_unsupported_filetype(filename):
    file = FileStorage(filename=filename)
    with pytest.raises(UnsupportedFiletypeError):
        file_to_text(file)
