from ingestion_tester.attachments import generate_attachments
from ingestion_tester.scenarios import AttachmentSpec, AttachmentType


def test_generate_attachments():
    specs = (
        AttachmentSpec(type=AttachmentType.PDF, filename="test.pdf", size_kb=50),
        AttachmentSpec(type=AttachmentType.PNG, filename="test.png", size_kb=20),
        AttachmentSpec(type=AttachmentType.CSV, filename="test.csv", size_kb=5),
    )
    items = generate_attachments(specs, title="Titre", ref="REF123")
    assert len(items) == 3
    for item in items:
        assert item.data
        assert item.filename
