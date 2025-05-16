from werkzeug.datastructures import FileStorage

import pytest

from src.classifier import UnsupportedIndustryError, classify_file
from src.file_to_text import UnsupportedFiletypeError

# note alternative spellings of licence/license in both document names and keywords
classifier_rules = {
    'legal': {
        'licence_agreement': ['licence', 'license'],
        'statement_of_particulars': ['statement']
    },
    'medical': {
        'license_to_practice': ['licence', 'license'],
        'doctors_statement': ['statement']
    },
    'retail': {}
}

@pytest.mark.parametrize("industry, file_contents, expected", [
    ("legal", "This license is made between...", "licence_agreement"),
    ("legal", "Employee statement of particulars", "statement_of_particulars"),
    ("legal", "This is unrelated content", "unknown file"),
    ("medical", "LICENCE to practice medicine", "license_to_practice"),
    ("medical", "Doctor's statement confirms diagnosis", "doctors_statement"),
    ("medical", "This is something else entirely", "unknown file"),
    # retail industry has no documents defined in classifier_rules
    ("retail", "Receipt for purchase 5/02/12 £29.19", "unknown file"),
    # empty file
    ("legal", "", "unknown file")
])
def test_classification(mocker, industry, file_contents, expected):
    mocker.patch('src.classifier.classifier_rules', classifier_rules)
    mocker.patch('src.classifier.file_to_text', return_value=file_contents)

    file = mocker.Mock(FileStorage)
    assert classify_file(file, industry) == expected

def test_unsupported_industry(mocker):
    mocker.patch('src.classifier.classifier_rules', classifier_rules)
    mocker.patch('src.classifier.file_to_text', return_value="dummy contents")

    file = mocker.Mock(FileStorage)

    with pytest.raises(UnsupportedIndustryError):
        classify_file(file, 'blah')

def test_unsupported_filetype_returns_unknown(mocker):
    mocker.patch('src.classifier.classifier_rules', classifier_rules)
    mocker.patch('src.classifier.file_to_text', side_effect=UnsupportedFiletypeError("mp3"))
    
    file = mocker.Mock(FileStorage)
    
    assert classify_file(file, 'legal') == "unknown file"
