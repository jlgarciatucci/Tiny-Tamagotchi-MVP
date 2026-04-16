from __future__ import annotations

import os
from typing import Any

import certifi

try:
    import streamlit as st
except Exception:  # pragma: no cover - streamlit is optional in unit tests
    st = None  # type: ignore[assignment]


class SupabaseConfigError(RuntimeError):
    pass


def get_supabase_client() -> Any:
    _configure_ssl_certificates()

    from supabase import create_client

    url = _read_secret("SUPABASE_URL", "url", "project_url")
    key = _read_secret(
        "SUPABASE_KEY",
        "key",
        "anon_key",
        "service_role_key",
        "supabase_key",
    )

    if not url or not key:
        raise SupabaseConfigError(
            "Supabase is not configured. Add SUPABASE_URL and SUPABASE_KEY to Streamlit secrets."
        )

    return create_client(url, key)


def _configure_ssl_certificates() -> None:
    custom_ca_bundle = _read_secret(
        "SUPABASE_CA_BUNDLE",
        "ca_bundle",
        "ca_bundle_path",
        "ssl_cert_file",
    )
    if custom_ca_bundle:
        os.environ["SSL_CERT_FILE"] = custom_ca_bundle
        os.environ["REQUESTS_CA_BUNDLE"] = custom_ca_bundle
        return

    try:
        import truststore

        truststore.inject_into_ssl()
        return
    except Exception:
        pass

    _try_enable_windows_certifi()
    ca_bundle = certifi.where()
    os.environ["SSL_CERT_FILE"] = ca_bundle
    os.environ["REQUESTS_CA_BUNDLE"] = ca_bundle


def _try_enable_windows_certifi() -> None:
    if os.name != "nt":
        return

    try:
        import certifi_win32  # noqa: F401
    except Exception:
        pass


def _read_secret(env_name: str, *supabase_names: str) -> str | None:
    if st is not None:
        try:
            value = st.secrets.get(env_name)
            if value:
                return str(value)
        except Exception:
            pass

        try:
            section = st.secrets.get("supabase", {})
            for name in supabase_names:
                value = section.get(name)
                if value:
                    return str(value)
        except Exception:
            pass

    return os.getenv(env_name)
