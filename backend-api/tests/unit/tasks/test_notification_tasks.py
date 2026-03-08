"""
Unit tests for Notification Celery Tasks
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timezone


class TestProcessAppointmentStatistics:
    """Tests for process_appointment_statistics task"""

    def test_statistics_returns_expected_keys(self):
        """Test that statistics task returns all expected keys"""
        # Arrange
        from app.tasks.notification_tasks import process_appointment_statistics

        # Act
        result = process_appointment_statistics()

        # Assert
        assert "date" in result
        assert "total_appointments" in result
        assert "scheduled" in result
        assert "completed" in result
        assert "cancelled" in result
        assert "no_show" in result

    def test_statistics_date_is_utc_iso_format(self):
        """Test that statistics date is in UTC ISO format"""
        # Arrange
        from app.tasks.notification_tasks import process_appointment_statistics

        # Act
        result = process_appointment_statistics()

        # Assert - should be parseable as ISO datetime
        parsed = datetime.fromisoformat(result["date"])
        assert parsed.tzinfo is not None  # timezone-aware

    def test_statistics_initial_values_are_zero(self):
        """Test that initial statistics values are zero (no DB connected)"""
        # Arrange
        from app.tasks.notification_tasks import process_appointment_statistics

        # Act
        result = process_appointment_statistics()

        # Assert
        assert result["total_appointments"] == 0
        assert result["scheduled"] == 0
        assert result["completed"] == 0
        assert result["cancelled"] == 0
        assert result["no_show"] == 0


class TestCleanupOldAppointments:
    """Tests for cleanup_old_appointments task"""

    def test_cleanup_returns_cleaned_count(self):
        """Test that cleanup task returns cleaned count"""
        # Arrange
        from app.tasks.notification_tasks import cleanup_old_appointments

        # Act
        result = cleanup_old_appointments()

        # Assert
        assert "cleaned" in result
        assert isinstance(result["cleaned"], int)

    def test_cleanup_initial_count_is_zero(self):
        """Test that initial cleanup count is zero (no DB connected)"""
        # Arrange
        from app.tasks.notification_tasks import cleanup_old_appointments

        # Act
        result = cleanup_old_appointments()

        # Assert
        assert result["cleaned"] == 0

    def test_cleanup_logs_execution(self):
        """Test that cleanup task logs its execution"""
        # Arrange
        from app.tasks.notification_tasks import cleanup_old_appointments

        # Act
        with patch("app.tasks.notification_tasks.logger") as mock_logger:
            cleanup_old_appointments()

            # Assert
            assert mock_logger.info.call_count >= 1
            log_messages = [
                str(call) for call in mock_logger.info.call_args_list
            ]
            assert any("cleanup" in msg.lower() for msg in log_messages)


class TestGenerateDailyReport:
    """Tests for generate_daily_report task"""

    def test_daily_report_returns_expected_keys(self):
        """Test that daily report contains all expected keys"""
        # Arrange
        from app.tasks.notification_tasks import generate_daily_report

        # Act
        result = generate_daily_report()

        # Assert
        assert "date" in result
        assert "new_appointments" in result
        assert "cancelled_appointments" in result
        assert "completed_appointments" in result

    def test_daily_report_date_is_today(self):
        """Test that daily report date matches today"""
        # Arrange
        from app.tasks.notification_tasks import generate_daily_report

        today = datetime.now(timezone.utc).date().isoformat()

        # Act
        result = generate_daily_report()

        # Assert
        assert result["date"] == today

    def test_daily_report_initial_values_are_zero(self):
        """Test that initial report values are zero"""
        # Arrange
        from app.tasks.notification_tasks import generate_daily_report

        # Act
        result = generate_daily_report()

        # Assert
        assert result["new_appointments"] == 0
        assert result["cancelled_appointments"] == 0
        assert result["completed_appointments"] == 0

    def test_daily_report_logs_execution(self):
        """Test that daily report logs its execution"""
        # Arrange
        from app.tasks.notification_tasks import generate_daily_report

        # Act
        with patch("app.tasks.notification_tasks.logger") as mock_logger:
            generate_daily_report()

            # Assert
            assert mock_logger.info.call_count >= 1
