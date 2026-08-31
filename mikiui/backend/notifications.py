"""Push notification support for MikiUI backends.

Provides functions to send push notifications via FCM (Android) and APNs (iOS).
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def send_push_notification(
    token: str,
    title: str,
    body: str,
    data: dict[str, Any] | None = None,
    *,
    fcm_server_key: str | None = None,
    apns_key_path: str | None = None,
    apns_key_id: str | None = None,
    apns_team_id: str | None = None,
    bundle_id: str | None = None,
    platform: str | None = None,
) -> dict[str, Any]:
    """Send a push notification to a device.

    Supports both FCM (Android) and APNs (iOS). The platform is auto-detected
    from the token format if not specified.

    Parameters
    ----------
    token:
        The device registration token.
    title:
        Notification title.
    body:
        Notification body text.
    data:
        Additional data payload (optional).
    fcm_server_key:
        FCM server key for Android notifications.
    apns_key_path:
        Path to the APNs .p8 key file for iOS notifications.
    apns_key_id:
        APNs key ID (from Apple Developer Portal).
    apns_team_id:
        Apple Developer Team ID.
    bundle_id:
        iOS bundle ID (required for APNs).
    platform:
        Force platform: ``"android"`` or ``"ios"``. Auto-detected if None.

    Returns
    -------
    Dict with ``status`` and ``message`` keys.

    Examples
    --------
    Send via FCM (Android):

    >>> send_push_notification(
    ...     token="device_token_here",
    ...     title="Hello!",
    ...     body="You have a new message",
    ...     fcm_server_key="your_fcm_server_key",
    ... )

    Send via APNs (iOS):

    >>> send_push_notification(
    ...     token="device_token_here",
    ...     title="Hello!",
    ...     body="You have a new message",
    ...     apns_key_path="/path/to/AuthKey_XXXXX.p8",
    ...     apns_key_id="YOUR_KEY_ID",
    ...     apns_team_id="YOUR_TEAM_ID",
    ...     bundle_id="com.example.app",
    ... )
    """
    # Auto-detect platform from token if not specified
    if platform is None:
        # FCM tokens are typically longer and contain colons
        # APNs tokens are 64-character hex strings
        if len(token) == 64 and all(c in "0123456789abcdef" for c in token.lower()):
            platform = "ios"
        else:
            platform = "android"

    if platform == "android":
        return _send_fcm_notification(token, title, body, data, fcm_server_key)
    elif platform == "ios":
        return _send_apns_notification(
            token, title, body, data,
            apns_key_path, apns_key_id, apns_team_id, bundle_id,
        )
    else:
        return {"status": "error", "message": f"Unknown platform: {platform!r}"}


def _send_fcm_notification(
    token: str,
    title: str,
    body: str,
    data: dict[str, Any] | None,
    fcm_server_key: str | None,
) -> dict[str, Any]:
    """Send a push notification via Firebase Cloud Messaging."""
    if not fcm_server_key:
        return {"status": "error", "message": "FCM server key is required for Android notifications"}

    try:
        import requests

        headers = {
            "Authorization": f"key={fcm_server_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "to": token,
            "notification": {
                "title": title,
                "body": body,
                "sound": "default",
            },
            "data": data or {},
            "priority": "high",
        }

        response = requests.post(
            "https://fcm.googleapis.com/fcm/send",
            headers=headers,
            json=payload,
            timeout=10,
        )

        result = response.json()

        if result.get("success", 0) > 0:
            return {"status": "ok", "message": "Notification sent", "platform": "android"}
        else:
            error = result.get("results", [{}])[0].get("error", "Unknown error")
            return {"status": "error", "message": f"FCM error: {error}"}

    except ImportError:
        return {"status": "error", "message": "requests library required. Install with: pip install requests"}
    except Exception as exc:
        logger.exception("FCM notification failed")
        return {"status": "error", "message": str(exc)}


def _send_apns_notification(
    token: str,
    title: str,
    body: str,
    data: dict[str, Any] | None,
    apns_key_path: str | None,
    apns_key_id: str | None,
    apns_team_id: str | None,
    bundle_id: str | None,
) -> dict[str, Any]:
    """Send a push notification via Apple Push Notification service."""
    if not apns_key_path or not apns_key_id or not apns_team_id or not bundle_id:
        return {
            "status": "error",
            "message": "APNs requires: apns_key_path, apns_key_id, apns_team_id, bundle_id",
        }

    # Narrow types for mypy (we've verified they're not None above)
    key_path: str = apns_key_path
    key_id: str = apns_key_id
    team_id: str = apns_team_id
    bundle: str = bundle_id

    try:
        # Try to use the httpx library for HTTP/2 support
        import httpx

        # Read the .p8 key file
        with open(key_path) as f:
            private_key = f.read()

        # Generate JWT token for APNs authentication
        import time

        import jwt

        now = int(time.time())
        token_payload = {
            "iss": team_id,
            "iat": now,
            "exp": now + 3600,  # 1 hour expiry
        }

        auth_token = jwt.encode(token_payload, private_key, algorithm="ES256", headers={"kid": key_id})

        # Determine APNs server (development or production)
        apns_server = "https://api.push.apple.com"  # Production

        headers: dict[str, str] = {
            "authorization": f"bearer {auth_token}",
            "apns-topic": bundle,
            "apns-priority": "10",
            "apns-push-type": "alert",
        }

        payload = {
            "aps": {
                "alert": {
                    "title": title,
                    "body": body,
                },
                "sound": "default",
                "badge": 1,
            },
            **(data or {}),
        }

        url = f"{apns_server}/3/device/{token}"
        response = httpx.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            return {"status": "ok", "message": "Notification sent", "platform": "ios"}
        else:
            error = response.json().get("reason", "Unknown error")
            return {"status": "error", "message": f"APNs error: {error}"}

    except ImportError as exc:
        return {
            "status": "error",
            "message": f"Missing library: {exc.name}. Install with: pip install httpx pyjwt cryptography",
        }
    except Exception as exc:
        logger.exception("APNs notification failed")
        return {"status": "error", "message": str(exc)}


def send_bulk_push_notifications(
    tokens: list[str],
    title: str,
    body: str,
    data: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Send push notifications to multiple devices.

    Parameters
    ----------
    tokens:
        List of device registration tokens.
    title:
        Notification title.
    body:
        Notification body text.
    data:
        Additional data payload (optional).
    **kwargs:
        Additional arguments passed to :func:`send_push_notification`.

    Returns
    -------
    Dict with ``sent``, ``failed``, and ``results`` keys.
    """
    results = []
    sent = 0
    failed = 0

    for token in tokens:
        result = send_push_notification(token, title, body, data, **kwargs)
        results.append({"token": token, **result})
        if result.get("status") == "ok":
            sent += 1
        else:
            failed += 1

    return {
        "status": "ok" if failed == 0 else "partial",
        "sent": sent,
        "failed": failed,
        "total": len(tokens),
        "results": results,
    }


__all__ = [
    "send_push_notification",
    "send_bulk_push_notifications",
]
