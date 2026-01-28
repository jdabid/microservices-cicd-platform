"""
Email Tasks (Celery)
Asynchronous email sending
"""
import logging
from typing import List, Optional
from celery import Task
from app.core.celery.celery_app import celery_app

logger = logging.getLogger(__name__)


class EmailTask(Task):
    """Base task with error handling"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        logger.error(f"Task {task_id} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        logger.info(f"Task {task_id} succeeded")
        super().on_success(retval, task_id, args, kwargs)


@celery_app.task(
    base=EmailTask,
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def send_appointment_confirmation_email(
        self,
        patient_email: str,
        patient_name: str,
        doctor_name: str,
        appointment_date: str,
        appointment_id: int
):
    """
    Send appointment confirmation email

    Args:
        patient_email: Patient's email address
        patient_name: Patient's name
        doctor_name: Doctor's name
        appointment_date: Appointment date (ISO format)
        appointment_id: Appointment ID
    """
    try:
        logger.info(f"Sending confirmation email to {patient_email}")

        # TODO: Integrate with actual email service (SendGrid, AWS SES, etc.)
        # For now, just log the email
        email_content = f"""
        Dear {patient_name},

        Your appointment has been confirmed!

        Details:
        - Doctor: {doctor_name}
        - Date: {appointment_date}
        - Appointment ID: {appointment_id}

        If you need to reschedule, please contact us.

        Best regards,
        Medical Appointments Team
        """

        logger.info(f"Email content:\n{email_content}")

        # Simulate email sending
        import time
        time.sleep(2)  # Simulate delay

        logger.info(f"✅ Email sent successfully to {patient_email}")

        return {
            "status": "success",
            "recipient": patient_email,
            "appointment_id": appointment_id
        }

    except Exception as exc:
        logger.error(f"Failed to send email: {exc}")
        # Retry the task
        raise self.retry(exc=exc)


@celery_app.task(base=EmailTask)
def send_appointment_reminder_email(
        patient_email: str,
        patient_name: str,
        doctor_name: str,
        appointment_date: str,
        hours_before: int = 24
):
    """
    Send appointment reminder email

    Args:
        patient_email: Patient's email
        patient_name: Patient's name
        doctor_name: Doctor's name
        appointment_date: Appointment date
        hours_before: Hours before appointment
    """
    logger.info(f"Sending reminder email to {patient_email} ({hours_before}h before)")

    email_content = f"""
    Dear {patient_name},

    This is a reminder of your upcoming appointment in {hours_before} hours.

    Details:
    - Doctor: {doctor_name}
    - Date: {appointment_date}

    Please arrive 15 minutes early.

    Best regards,
    Medical Appointments Team
    """

    logger.info(f"Reminder email content:\n{email_content}")

    return {
        "status": "success",
        "recipient": patient_email,
        "reminder_type": f"{hours_before}h_before"
    }


@celery_app.task(base=EmailTask)
def send_appointment_cancellation_email(
        patient_email: str,
        patient_name: str,
        appointment_id: int,
        cancellation_reason: Optional[str] = None
):
    """
    Send appointment cancellation email

    Args:
        patient_email: Patient's email
        patient_name: Patient's name
        appointment_id: Cancelled appointment ID
        cancellation_reason: Optional reason for cancellation
    """
    logger.info(f"Sending cancellation email to {patient_email}")

    reason_text = f"\nReason: {cancellation_reason}" if cancellation_reason else ""

    email_content = f"""
    Dear {patient_name},

    Your appointment #{appointment_id} has been cancelled.{reason_text}

    If you would like to reschedule, please contact us.

    Best regards,
    Medical Appointments Team
    """

    logger.info(f"Cancellation email content:\n{email_content}")

    return {
        "status": "success",
        "recipient": patient_email,
        "appointment_id": appointment_id
    }


@celery_app.task
def send_bulk_reminder_emails(appointment_ids: List[int]):
    """
    Send reminder emails to multiple appointments

    Args:
        appointment_ids: List of appointment IDs
    """
    logger.info(f"Sending bulk reminders for {len(appointment_ids)} appointments")

    results = []
    for apt_id in appointment_ids:
        # In production, fetch appointment from database
        # For now, just log
        logger.info(f"Processing reminder for appointment {apt_id}")
        results.append({"appointment_id": apt_id, "status": "queued"})

    return {
        "total": len(appointment_ids),
        "processed": len(results),
        "results": results
    }