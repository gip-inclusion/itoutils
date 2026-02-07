import logging

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


class NexusAPIException(Exception):
    pass


class NexusAPIClient:
    def __init__(self):
        self.client = httpx.Client(
            base_url=settings.NEXUS_API_BASE_URL,
            headers={"Authorization": f"Token {settings.NEXUS_API_TOKEN}"},
        )

    def call(self, method, url, **kwargs):
        try:
            response = self.client.request(method, url, **kwargs).raise_for_status()
        except httpx.HTTPError as exc:
            try:
                error = exc.response.json()
                logger.exception(f"nexus {method}:{url} error=%s", error)
            except Exception:
                logger.exception(f"nexus {method}:{url} error=%s", exc)
            raise NexusAPIException from exc
        if errors := response.json().get("errors"):
            logger.error(f"nexus {method}:{url} error=%s", errors)
        return response

    def init_full_sync(self):
        return self.call("POST", "sync-start").json()["started_at"]

    def complete_full_sync(self, start_at):
        self.call("POST", "sync-completed", json={"started_at": start_at})

    def send_users(self, users_data):
        self.call("POST", "users", json=users_data)

    def delete_users(self, user_pks):
        self.call("DELETE", "users", json=[{"id": str(user_pk)} for user_pk in user_pks])

    def send_structures(self, structures_data):
        self.call("POST", "structures", json=structures_data)

    def delete_structures(self, structure_pks):
        self.call("DELETE", "structures", json=[{"id": str(structure_pk)} for structure_pk in structure_pks])

    def send_memberships(self, memberships_data):
        self.call("POST", "memberships", json=memberships_data)

    def delete_memberships(self, membership_pks):
        self.call("DELETE", "memberships", json=[{"id": str(membership_pk)} for membership_pk in membership_pks])

    def dropdown_status(self, email):
        return self.call("POST", "dropdown-status", json={"email": email}).json()
