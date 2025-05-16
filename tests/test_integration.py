import pytest

from src.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.mark.parametrize("filename, industry, classification", [
    ('drivers_license_1.jpg', 'government', 'drivers_licence'),
    ('drivers_licence_2.jpg', 'government', 'drivers_licence'),
    ('drivers_license_3.jpg', 'government', 'drivers_licence'),
    ('bank_statement_1.pdf', 'accounting', 'bank_statement'),
    ('bank_statement_2.pdf', 'accounting', 'bank_statement'),
    ('bank_statement_3.pdf', 'accounting', 'bank_statement'),
    ('invoice_1.pdf', 'accounting', 'invoice'),
    ('invoice_2.pdf', 'accounting', 'invoice'),
    ('invoice_3.pdf', 'accounting', 'invoice'),
])
def test_integration(client, filename, industry, classification):
    with open(f'files/{filename}', 'rb') as f:
        data = {
            'file': (f, filename),
            'industry': industry
        }
        response = client.post('/classify_file', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert response.get_json() == {"file_class": classification}
