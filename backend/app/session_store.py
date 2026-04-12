from __future__ import annotations

import json
from datetime import datetime
from threading import Lock
from uuid import uuid4

from .config import RGB_IMAGE_PATH, THERMAL_IMAGE_PATH, TRAIN_TEST_SPLIT_PATH
from .schemas import (
    ChainOfThoughtStep,
    LatLng,
    Session,
    SessionMessage,
    SessionStatus,
)


class InMemorySessionStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._sessions: dict[str, Session] = {}
        self._contexts: dict[str, dict] = {}
        self._live_chains: dict[str, list[ChainOfThoughtStep]] = {}

    def create_session(self, center: LatLng, radius_m: int) -> Session:
        session_id = f"sess_{uuid4().hex[:8]}"

        # Load image metadata
        image_metadata = {}
        if TRAIN_TEST_SPLIT_PATH.exists():
            with open(TRAIN_TEST_SPLIT_PATH) as f:
                image_metadata = json.load(f)

        context = {
            "center": {"lat": center.lat, "lng": center.lng},
            "radius_m": radius_m,
            "rgb_image_path": str(RGB_IMAGE_PATH),
            "thermal_image_path": str(THERMAL_IMAGE_PATH),
            "image_metadata": {
                "rgb_file": "475.JPG",
                "thermal_file": "475 (1).JPG",
                "source_pair": image_metadata.get("475.JPG", []),
                "total_image_pairs": len(image_metadata),
            },
        }

        session = Session(
            session_id=session_id,
            center=center,
            radius_m=radius_m,
            status=SessionStatus.region_loaded,
        )

        with self._lock:
            self._sessions[session_id] = session
            self._contexts[session_id] = context
            self._live_chains[session_id] = []

        return session

    def get_session(self, session_id: str) -> Session:
        with self._lock:
            return self._sessions[session_id]

    def get_region_context(self, session_id: str) -> dict:
        with self._lock:
            return self._contexts[session_id]

    def set_status(self, session_id: str, status: SessionStatus) -> None:
        with self._lock:
            self._sessions[session_id].status = status

    def append_chain_step(self, session_id: str, step: ChainOfThoughtStep) -> None:
        with self._lock:
            self._live_chains[session_id].append(step)

    def get_live_chain(self, session_id: str) -> list[ChainOfThoughtStep]:
        with self._lock:
            return list(self._live_chains[session_id])

    def finalize_message(
        self,
        session_id: str,
        role: str,
        content: str,
        chain_of_thought: list[ChainOfThoughtStep] | None = None,
    ) -> None:
        with self._lock:
            session = self._sessions[session_id]
            msg_index = len(session.messages)
            session.messages.append(
                SessionMessage(
                    role=role,
                    content=content,
                    message_index=msg_index,
                    chain_of_thought=chain_of_thought or [],
                )
            )
            self._live_chains[session_id] = []

    def get_messages(self, session_id: str) -> list[SessionMessage]:
        with self._lock:
            return list(self._sessions[session_id].messages)


session_store = InMemorySessionStore()
