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

    def init_full_sync(self):
        try:
            response = self.client.post("sync-start").raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("nexus init_full_sync error=%s", exc)
            raise NexusAPIException from exc
        return response.json()["started_at"]

    def complete_full_sync(self, start_at):
        try:
            self.client.post("sync-completed", json={"started_at": start_at}).raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("nexus complete_full_sync error=%s", exc)
            raise NexusAPIException from exc

    def send_users(self, users_data):
        try:
            self.client.post("users", json=users_data).raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("nexus send_users error=%s", exc)
            raise NexusAPIException from exc

    def delete_users(self, user_pks):
        try:
            self.client.request(
                "DELETE", "users", json=[{"id": str(user_pk)} for user_pk in user_pks]
            ).raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("nexus delete_users error=%s", exc)
            raise NexusAPIException from exc

    def send_structures(self, structures_data):
        try:
            self.client.post("structures", json=structures_data).raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("nexus send_structures error=%s", exc)
            raise NexusAPIException from exc

    def delete_structures(self, structure_pks):
        try:
            self.client.request(
                "DELETE", "structures", json=[{"id": str(structure_pk)} for structure_pk in structure_pks]
            ).raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("nexus delete_structures error=%s", exc)
            raise NexusAPIException from exc

    def send_memberships(self, memberships_data):
        try:
            self.client.post("memberships", json=memberships_data).raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("nexus send_memberships error=%s", exc)
            raise NexusAPIException from exc

    def delete_memberships(self, membership_pks):
        try:
            self.client.request(
                "DELETE", "memberships", json=[{"id": str(membership_pk)} for membership_pk in membership_pks]
            ).raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("nexus delete_memberships error=%s", exc)
            raise NexusAPIException from exc
