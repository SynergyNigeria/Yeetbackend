"""
Email utility functions for YEET Bank notifications.

Handles:
  - Welcome / registration emails
  - Password reset emails
  - Money received emails
"""

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def _send(subject: str, html_content: str, recipient_email: str):
    """Low-level helper that sends a single HTML email."""
    import logging
    logger = logging.getLogger(__name__)

    from_email = settings.DEFAULT_FROM_EMAIL
    host = getattr(settings, 'EMAIL_HOST', '?')
    port = getattr(settings, 'EMAIL_PORT', '?')
    backend = getattr(settings, 'EMAIL_BACKEND', '?')
    host_user = getattr(settings, 'EMAIL_HOST_USER', '?')

    print(f"\n{'='*60}")
    print(f"[EMAIL] Attempting to send email")
    print(f"  Backend  : {backend}")
    print(f"  SMTP     : {host}:{port}")
    print(f"  Auth user: {host_user}")
    print(f"  From     : {from_email}")
    print(f"  To       : {recipient_email}")
    print(f"  Subject  : {subject}")
    print(f"{'='*60}")

    plain_text = strip_tags(html_content)
    try:
        send_mail(
            subject=subject,
            message=plain_text,
            from_email=from_email,
            recipient_list=[recipient_email],
            html_message=html_content,
            fail_silently=False,
        )
        print(f"[EMAIL] ✅ Sent successfully to {recipient_email}")
        logger.info("Email sent successfully to %s | subject: %s", recipient_email, subject)
        return True
    except Exception as exc:
        print(f"[EMAIL] ❌ FAILED to send to {recipient_email}")
        print(f"[EMAIL]    Error: {exc}")
        logger.error("Email send failed to %s | subject: %s | error: %s", recipient_email, subject, exc)
        return False


# ─── Welcome Email ───────────────────────────────────────────────────────────

def send_welcome_email(user) -> bool:
    """
    Send a welcome email to a newly registered user.

    Parameters
    ----------
    user : accounts.User instance
    """
    subject = "Welcome to YEET Bank!"
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Welcome to YEET Bank</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }}
    .container {{ max-width: 560px; margin: 40px auto; background: #ffffff;
                  border-radius: 12px; overflow: hidden;
                  box-shadow: 0 4px 12px rgba(0,0,0,.08); }}
    .header {{ background: linear-gradient(135deg, #6C63FF, #3B82F6);
               padding: 40px 24px; text-align: center; }}
    .header h1 {{ color: #fff; margin: 0 0 8px; font-size: 26px; }}
    .header p  {{ color: rgba(255,255,255,.85); margin: 0; font-size: 15px; }}
    .body {{ padding: 32px 24px; color: #374151; }}
    .body p {{ line-height: 1.6; margin: 0 0 16px; }}
    .account-box {{ background: #EEF2FF; border: 2px solid #6C63FF;
                    border-radius: 10px; padding: 18px 20px; margin: 20px 0; }}
    .account-box .label {{ font-size: 12px; color: #6B7280; text-transform: uppercase;
                           letter-spacing: .6px; margin-bottom: 6px; }}
    .account-box .value {{ font-size: 22px; font-weight: bold; color: #6C63FF;
                           letter-spacing: 2px; }}
    .steps {{ margin: 0 0 24px; padding: 0; list-style: none; }}
    .steps li {{ padding: 10px 0; border-bottom: 1px solid #E5E7EB;
                 font-size: 14px; color: #374151; }}
    .steps li:last-child {{ border-bottom: none; }}
    .steps li span {{ margin-right: 10px; font-size: 18px; }}
    .btn {{ display: inline-block; padding: 14px 32px;
            background: linear-gradient(135deg, #6C63FF, #3B82F6);
            color: #ffffff; text-decoration: none;
            border-radius: 8px; font-weight: bold; font-size: 16px; }}
    .footer {{ background: #f9fafb; padding: 20px 24px;
               text-align: center; font-size: 12px; color: #9CA3AF; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Welcome to YEET Bank!</h1>
      <p>Your account is live and ready to use.</p>
    </div>
    <div class="body">
      <p>Hi <strong>{user.first_name or user.username}</strong>,</p>
      <p>You're officially a YEET Bank member! Here's your account number — keep it safe,
         you'll share it with people who want to send you money.</p>

      <div class="account-box">
        <div class="label">Your Account Number</div>
        <div class="value">{user.account_number}</div>
      </div>

      <p><strong>Get started in 3 easy steps:</strong></p>
      <ul class="steps">
        <li><span></span> Set up a 4-digit <strong>Transfer PIN</strong> in Settings</li>
        <li><span></span> <strong>Add money</strong> to your account from the Dashboard</li>
        <li><span></span> <strong>Send &amp; receive</strong> money instantly with YEET transfers</li>
      </ul>

      <p style="text-align:center;">
        <a href="{frontend_url}/dashboard" class="btn">Go to My Dashboard</a>
      </p>
    </div>
    <div class="footer">
      &copy; 2026 YEET Bank &bull; This is an automated message, please do not reply.
    </div>
  </div>
</body>
</html>
"""
    return _send(subject, html_content, user.email)


# ─── Password Reset ────────────────────────────────────────────────────────────

def send_password_reset_email(user, reset_link: str) -> bool:
    """
    Send a password-reset email.

    Parameters
    ----------
    user        : accounts.User instance
    reset_link  : full URL pointing to the frontend reset-password page
                  e.g. https://app.yeetbank.com/reset-password?uid=…&token=…
    """
    subject = "Reset your YEET Bank password"

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Reset Your Password</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }}
    .container {{ max-width: 560px; margin: 40px auto; background: #ffffff;
                  border-radius: 12px; overflow: hidden;
                  box-shadow: 0 4px 12px rgba(0,0,0,.08); }}
    .header {{ background: linear-gradient(135deg, #6C63FF, #3B82F6);
               padding: 32px 24px; text-align: center; }}
    .header h1 {{ color: #fff; margin: 0; font-size: 24px; letter-spacing: .5px; }}
    .body {{ padding: 32px 24px; color: #374151; }}
    .body p {{ line-height: 1.6; margin: 0 0 16px; }}
    .btn {{ display: inline-block; padding: 14px 32px;
            background: linear-gradient(135deg, #6C63FF, #3B82F6);
            color: #ffffff; text-decoration: none;
            border-radius: 8px; font-weight: bold; font-size: 16px;
            margin: 8px 0 24px; }}
    .note {{ font-size: 13px; color: #6B7280; }}
    .footer {{ background: #f9fafb; padding: 20px 24px;
               text-align: center; font-size: 12px; color: #9CA3AF; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>YEET Bank</h1>
    </div>
    <div class="body">
      <p>Hi <strong>{user.first_name or user.username}</strong>,</p>
      <p>We received a request to reset the password for your YEET Bank account
         (<em>{user.email}</em>).</p>
      <p>Click the button below to choose a new password. This link is valid for
         <strong>1 hour</strong>.</p>
      <p style="text-align:center;">
        <a href="{reset_link}" class="btn">Reset My Password</a>
      </p>
      <p class="note">
        If the button doesn't work, copy and paste this link into your browser:<br/>
        <a href="{reset_link}">{reset_link}</a>
      </p>
      <p class="note">
        If you didn't request a password reset, please ignore this email —
        your password will remain unchanged.
      </p>
    </div>
    <div class="footer">
      &copy; 2026 YEET Bank &bull; This is an automated message, please do not reply.
    </div>
  </div>
</body>
</html>
"""
    return _send(subject, html_content, user.email)


# ─── Money Received ────────────────────────────────────────────────────────────

def send_money_received_email(recipient, sender, amount, transaction) -> bool:
    """
    Send an email to the recipient when money arrives in their account.

    Parameters
    ----------
    recipient   : accounts.User — person who received money
    sender      : accounts.User — person who sent money
    amount      : Decimal / float / str — transfer amount
    transaction : transactions.Transaction instance
    """
    subject = f"You received ${amount} on YEET Bank"

    # Format completed_at nicely
    completed_at = ""
    if transaction.completed_at:
        completed_at = transaction.completed_at.strftime("%B %d, %Y at %I:%M %p UTC")

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Money Received</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }}
    .container {{ max-width: 560px; margin: 40px auto; background: #ffffff;
                  border-radius: 12px; overflow: hidden;
                  box-shadow: 0 4px 12px rgba(0,0,0,.08); }}
    .header {{ background: linear-gradient(135deg, #10B981, #3B82F6);
               padding: 32px 24px; text-align: center; }}
    .header h1 {{ color: #fff; margin: 0; font-size: 24px; }}
    .amount-box {{ background: #F0FDF4; border: 2px solid #10B981;
                   border-radius: 10px; padding: 20px; text-align: center;
                   margin: 24px 0; }}
    .amount-box .amount {{ font-size: 40px; font-weight: bold;
                           color: #10B981; margin: 0; }}
    .amount-box .label {{ color: #6B7280; font-size: 14px; margin-top: 4px; }}
    .body {{ padding: 32px 24px; color: #374151; }}
    .body p {{ line-height: 1.6; margin: 0 0 12px; }}
    .detail-row {{ display: flex; justify-content: space-between;
                   padding: 10px 0; border-bottom: 1px solid #E5E7EB;
                   font-size: 14px; }}
    .detail-row:last-child {{ border-bottom: none; }}
    .detail-label {{ color: #6B7280; }}
    .detail-value {{ font-weight: bold; color: #111827; }}
    .footer {{ background: #f9fafb; padding: 20px 24px;
               text-align: center; font-size: 12px; color: #9CA3AF; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Money Received!</h1>
    </div>
    <div class="body">
      <p>Hi <strong>{recipient.first_name or recipient.username}</strong>,</p>
      <p>Great news — money has landed in your YEET Bank account!</p>

      <div class="amount-box">
        <div class="amount">${amount}</div>
        <div class="label">has been credited to your account</div>
      </div>

      <div>
        <div class="detail-row">
          <span class="detail-label">From</span>
          <span class="detail-value">{sender.get_full_name()} ({sender.account_number})</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">To</span>
          <span class="detail-value">{recipient.get_full_name()} ({recipient.account_number})</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Transaction ID</span>
          <span class="detail-value">#{transaction.id}</span>
        </div>
        {"" if not completed_at else f'''
        <div class="detail-row">
          <span class="detail-label">Date</span>
          <span class="detail-value">{completed_at}</span>
        </div>'''}
        {"" if not transaction.description else f'''
        <div class="detail-row">
          <span class="detail-label">Note</span>
          <span class="detail-value">{transaction.description}</span>
        </div>'''}
      </div>

      <p style="margin-top:24px; font-size:13px; color:#6B7280;">
        Log in to YEET Bank to view your full transaction history and updated balance.
      </p>
    </div>
    <div class="footer">
      &copy; 2026 YEET Bank &bull; This is an automated message, please do not reply.
    </div>
  </div>
</body>
</html>
"""
    return _send(subject, html_content, recipient.email)
