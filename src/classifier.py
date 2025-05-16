from werkzeug.datastructures import FileStorage
import yaml

from src.file_to_text import UnsupportedFiletypeError, file_to_text


with open('classifier_rules.yaml') as rules_file:
    classifier_rules = yaml.safe_load(rules_file)

class UnsupportedIndustryError(ValueError):
    pass

def classify_file(file: FileStorage, industry) -> str:
    """
    Classify a document based on its content and the specified industry,
    using rules defined in `classifier_rules`.

    Parameters:
        file: The file to classify
        industry: The industry context for classification

    Returns:
        str: The document type if matched, otherwise "unknown file"
    
    Raises:
        UnsupportedIndustryError: If the specified industry is not present
                                  in `classifier_rules`
    """
    if industry not in classifier_rules:
        raise UnsupportedIndustryError(industry)
    industry_rules = classifier_rules[industry]

    try:
        file_contents = file_to_text(file)
    except UnsupportedFiletypeError:
        return "unknown file"
    
    # Return first match based on presence of any keyword in document text.
    # Order matters: later documents are not considered once a match is found.
    # We ignore case.
    for document, keywords in industry_rules.items():
        if any((keyword.lower() in file_contents.lower()) for keyword in keywords):
            return document

    return "unknown file"

