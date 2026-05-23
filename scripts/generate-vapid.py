#!/usr/bin/env python3
"""
Generate VAPID keys + NOTIFY_AUTH_TOKEN for The Signal push notifications.

One-time setup. Outputs three values to copy into the Cloudflare Pages
project's Functions env vars.

Usage:
  python3 -m pip install cryptography
  python3 scripts/generate-vapid.py
"""

import base64
import json
import secrets

from cryptography.hazmat.primitives.asymmetric import ec


def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def main() -> None:
    key = ec.generate_private_key(ec.SECP256R1())
    priv_value = key.private_numbers().private_value
    pub = key.public_key().public_numbers()

    x = pub.x.to_bytes(32, "big")
    y = pub.y.to_bytes(32, "big")
    d = priv_value.to_bytes(32, "big")

    private_jwk = json.dumps(
        {"kty": "EC", "crv": "P-256", "x": b64url(x), "y": b64url(y), "d": b64url(d)}
    )
    public_b64url = b64url(b"\x04" + x + y)
    auth_token = secrets.token_urlsafe(32)

    bar = "=" * 64
    print(bar)
    print("Cloudflare Pages → Settings → Functions → Production env vars")
    print("Add these three. Leave the first as plaintext; mark the other two as secrets.")
    print(bar)
    print()
    print("VAPID_PUBLIC_KEY:")
    print(f"  {public_b64url}")
    print()
    print("VAPID_PRIVATE_KEY:")
    print(f"  {private_jwk}")
    print()
    print("NOTIFY_AUTH_TOKEN:")
    print(f"  {auth_token}")
    print()
    print(bar)
    print("Then bind a KV namespace:")
    print("  Settings → Functions → KV namespace bindings → Add binding")
    print("  Variable name: SUBSCRIPTIONS")
    print("  KV namespace:  (create one called 'signal-push-subs', then select it)")
    print(bar)


if __name__ == "__main__":
    main()
