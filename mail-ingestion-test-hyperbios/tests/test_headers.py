from ingestion_tester.mailer import build_message
from ingestion_tester.scenarios import Scenario, SenderType, AttachmentSpec, AttachmentType, RenderedScenario


def test_headers_generation():
    scenario = Scenario(
        id="TEST_SCENARIO",
        sender_type=SenderType.BANK,
        entity_display_name="Banque Test",
        from_email="banque@test.local",
        reply_to="reply@test.local",
        subject_template="Sujet {ref}",
        body_template="Body {ref}",
        attachments=tuple(),
        tags=tuple(),
    )
    rendered = RenderedScenario(
        scenario=scenario,
        subject="Sujet ABC",
        body="Body ABC",
        reference="ABC",
        date_str="2026-02-09",
    )
    msg = build_message(
        rendered,
        to_addr="dest@test.local",
        simulated_from="banque@test.local",
        reply_to="reply@test.local",
        attachments=[],
        simulated_sender_type="BANK",
        simulated_entity="Banque Test",
        scenario_id="TEST_SCENARIO",
    )
    assert msg["X-Simulated-Sender-Type"] == "BANK"
    assert msg["X-Simulated-Entity"] == "Banque Test"
    assert msg["X-Test-Scenario-Id"] == "TEST_SCENARIO"
