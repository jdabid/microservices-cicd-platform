"""
Unit tests for Email Celery Tasks
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def celery_config():
    """Override Celery config for testing (eager mode)"""
    return {
        "task_always_eager": True,
        "task_eager_propagates": True,
    }


@pytest.fixture
def mock_celery_app():
    """Mock the Celery app to avoid Redis connection"""
    with patch("app.core.celery.celery_app.celery_app") as mock_app:
        mock_app.conf = MagicMock()
        yield mock_app


@pytest.fixture
def confirmation_email_data():
    """Sample data for appointment confirmation email"""
    return {
        "patient_email": "patient@example.com",
        "patient_name": "John Doe",
        "doctor_name": "Dr. Smith",
        "appointment_date": "2026-03-15T10:00:00",
        "appointment_id": 42,
    }


@pytest.fixture
def reminder_email_data():
    """Sample data for appointment reminder email"""
    return {
        "patient_email": "patient@example.com",
        "patient_name": "John Doe",
        "doctor_name": "Dr. Smith",
        "appointment_date": "2026-03-15T10:00:00",
    }


@pytest.fixture
def cancellation_email_data():
    """Sample data for appointment cancellation email"""
    return {
        "patient_email": "patient@example.com",
        "patient_name": "John Doe",
        "appointment_id": 42,
    }


class TestSendAppointmentConfirmationEmail:
    """Tests for send_appointment_confirmation_email task"""

    def test_confirmation_email_returns_success(self, confirmation_email_data):
        """Test that confirmation email task returns success status"""
        # Arrange
        with patch("app.tasks.email_tasks.celery_app") as mock_app:
            mock_app.task = lambda *args, **kwargs: lambda fn: fn

            # Re-import to get the undecorated function logic
            from app.tasks.email_tasks import send_appointment_confirmation_email

            mock_self = MagicMock()

            # Act
            result = send_appointment_confirmation_email(
                mock_self,
                **confirmation_email_data,
            )

            # Assert
            assert result["status"] == "success"
            assert result["recipient"] == confirmation_email_data["patient_email"]
            assert result["appointment_id"] == confirmation_email_data["appointment_id"]

    def test_confirmation_email_retry_on_exception(self):
        """Test that confirmation email retries on failure"""
        # Arrange
        from app.tasks.email_tasks import send_appointment_confirmation_email

        mock_self = MagicMock()
        mock_self.retry = MagicMock(side_effect=Exception("Retry triggered"))

        # Act & Assert - simulate an exception in the task body
        with patch("app.tasks.email_tasks.logger") as mock_logger:
            mock_logger.info = MagicMock(side_effect=Exception("SMTP error"))

            with pytest.raises(Exception):
                send_appointment_confirmation_email(
                    mock_self,
                    patient_email="test@example.com",
                    patient_name="Test",
                    doctor_name="Dr. Test",
                    appointment_date="2026-03-15T10:00:00",
                    appointment_id=1,
                )

            # Assert retry was called
            mock_self.retry.assert_called_once()

    def test_confirmation_email_logs_content(self, confirmation_email_data):
        """Test that confirmation email logs the email content"""
        # Arrange
        from app.tasks.email_tasks import send_appointment_confirmation_email

        mock_self = MagicMock()

        # Act
        with patch("app.tasks.email_tasks.logger") as mock_logger:
            send_appointment_confirmation_email(
                mock_self,
                **confirmation_email_data,
            )

            # Assert - verify logging was called with email content
            log_calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any(
                confirmation_email_data["patient_name"] in call
                for call in log_calls
            )


class TestSendAppointmentReminderEmail:
    """Tests for send_appointment_reminder_email task"""

    def test_reminder_email_returns_success(self, reminder_email_data):
        """Test that reminder email task returns success status"""
        # Arrange
        from app.tasks.email_tasks import send_appointment_reminder_email

        # Act
        result = send_appointment_reminder_email(**reminder_email_data)

        # Assert
        assert result["status"] == "success"
        assert result["recipient"] == reminder_email_data["patient_email"]
        assert result["reminder_type"] == "24h_before"

    def test_reminder_email_custom_hours(self, reminder_email_data):
        """Test reminder email with custom hours_before parameter"""
        # Arrange
        from app.tasks.email_tasks import send_appointment_reminder_email

        # Act
        result = send_appointment_reminder_email(
            **reminder_email_data,
            hours_before=48,
        )

        # Assert
        assert result["reminder_type"] == "48h_before"


class TestSendAppointmentCancellationEmail:
    """Tests for send_appointment_cancellation_email task"""

    def test_cancellation_email_returns_success(self, cancellation_email_data):
        """Test that cancellation email returns success status"""
        # Arrange
        from app.tasks.email_tasks import send_appointment_cancellation_email

        # Act
        result = send_appointment_cancellation_email(**cancellation_email_data)

        # Assert
        assert result["status"] == "success"
        assert result["recipient"] == cancellation_email_data["patient_email"]
        assert result["appointment_id"] == cancellation_email_data["appointment_id"]

    def test_cancellation_email_with_reason(self, cancellation_email_data):
        """Test cancellation email includes reason when provided"""
        # Arrange
        from app.tasks.email_tasks import send_appointment_cancellation_email

        # Act
        with patch("app.tasks.email_tasks.logger") as mock_logger:
            result = send_appointment_cancellation_email(
                **cancellation_email_data,
                cancellation_reason="Doctor unavailable",
            )

            # Assert
            assert result["status"] == "success"
            log_calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any("Doctor unavailable" in call for call in log_calls)

    def test_cancellation_email_without_reason(self, cancellation_email_data):
        """Test cancellation email works without a reason"""
        # Arrange
        from app.tasks.email_tasks import send_appointment_cancellation_email

        # Act
        result = send_appointment_cancellation_email(**cancellation_email_data)

        # Assert
        assert result["status"] == "success"


class TestSendBulkReminderEmails:
    """Tests for send_bulk_reminder_emails task"""

    def test_bulk_reminders_processes_all_ids(self):
        """Test bulk reminder processes all appointment IDs"""
        # Arrange
        from app.tasks.email_tasks import send_bulk_reminder_emails

        appointment_ids = [1, 2, 3, 4, 5]

        # Act
        result = send_bulk_reminder_emails(appointment_ids)

        # Assert
        assert result["total"] == 5
        assert result["processed"] == 5
        assert len(result["results"]) == 5

    def test_bulk_reminders_empty_list(self):
        """Test bulk reminder with empty list"""
        # Arrange
        from app.tasks.email_tasks import send_bulk_reminder_emails

        # Act
        result = send_bulk_reminder_emails([])

        # Assert
        assert result["total"] == 0
        assert result["processed"] == 0
        assert result["results"] == []

    def test_bulk_reminders_result_structure(self):
        """Test that each result in bulk reminders has correct structure"""
        # Arrange
        from app.tasks.email_tasks import send_bulk_reminder_emails

        appointment_ids = [10, 20]

        # Act
        result = send_bulk_reminder_emails(appointment_ids)

        # Assert
        for item in result["results"]:
            assert "appointment_id" in item
            assert "status" in item
            assert item["status"] == "queued"
