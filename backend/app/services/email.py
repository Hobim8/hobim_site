"""Email delivery helpers using the Resend API.

All outbound emails go through this module so that:
- The Resend API key is configured in exactly one place.
- HTML templates are kept close to their send functions.
- Swapping Resend for another provider later only touches this file.
"""

import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.environ["RESEND_API_KEY"]

# The verified sender address configured in your Resend dashboard.
# Change this once you have a custom domain set up.
FROM_ADDRESS = "Hobim Trades <noreply@hobimtrades.com>"


def send_verification_email(to_email: str, first_name: str, token: str) -> None:
    """Send an account-activation email containing a signed verification link.

    Args:
        to_email:   The recipient's email address.
        first_name: Used to personalise the greeting.
        token:      The signed JWT produced by create_email_verification_token().
    """
    # TODO: Replace with your actual frontend domain once deployed.
    base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    verify_link = f"{base_url}/verify-email?token={token}"

    resend.Emails.send({
        "from": FROM_ADDRESS,
        "to": [to_email],
        "subject": "Verify your Hobim Trades account",
        "html": f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
            <h2>Welcome to Hobim Trades, {first_name}!</h2>
            <p>Click the button below to verify your email address and activate your account.</p>
            <p>
                <a href="{verify_link}"
                   style="display:inline-block;padding:12px 24px;background:#1a1a1a;
                          color:#fff;border-radius:6px;text-decoration:none;font-weight:bold;">
                    Verify my email
                </a>
            </p>
            <p>This link expires in <strong>24 hours</strong>.</p>
            <p>If you did not create an account, you can safely ignore this email.</p>
            <hr/>
            <small>Hobim Trades &mdash; hobimtrades.com</small>
        </div>
        """,
    })


def send_password_reset_email(to_email: str, first_name: str, token: str) -> None:
    """Send a password-reset email containing a signed reset link.

    Args:
        to_email:   The recipient's email address.
        first_name: Used to personalise the greeting.
        token:      The signed JWT produced by create_password_reset_token().
    """
    base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    reset_link = f"{base_url}/reset-password?token={token}"

    resend.Emails.send({
        "from": FROM_ADDRESS,
        "to": [to_email],
        "subject": "Reset your Hobim Trades password",
        "html": f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
            <h2>Password Reset Request</h2>
            <p>Hi {first_name},</p>
            <p>We received a request to reset the password for your Hobim Trades account.</p>
            <p>
                <a href="{reset_link}"
                   style="display:inline-block;padding:12px 24px;background:#1a1a1a;
                          color:#fff;border-radius:6px;text-decoration:none;font-weight:bold;">
                    Reset my password
                </a>
            </p>
            <p>This link expires in <strong>1 hour</strong>. If you did not request a password
               reset, you can safely ignore this email — your password will not change.</p>
            <hr/>
            <small>Hobim Trades &mdash; hobimtrades.com</small>
        </div>
        """,
    })

