from __future__ import annotations

from typing import Optional

from sqlite3 import IntegrityError
import bcrypt

from .base import BaseService


class AuthService(BaseService):
    table_name = "users"

    def authenticate(self, username: str, password: str) -> Optional[dict]:
        user = self._fetch_one(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username.strip(),),
        )
        if not user:
            return None
        stored_hash: str = user.get("password_hash", "")
        if not stored_hash:
            return None
        if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            return user
        return None

    def verify_credentials(self, username: str, password: str) -> bool:
        user = self.authenticate(username, password)
        return user is not None

    def update_password(self, user_id: int, new_password: str) -> None:
        hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt(rounds=12))
        self._execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hashed.decode("utf-8"), user_id),
        )

    def update_profile(
        self,
        user_id: int,
        username: str,
        display_name: str,
        new_password: Optional[str] = None,
    ) -> dict:
        username_clean = username.strip()
        display_clean = display_name.strip() or username_clean
        update_fields = {"username": username_clean, "display_name": display_clean}
        if new_password:
            hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt(rounds=12))
            update_fields["password_hash"] = hashed.decode("utf-8")

        assignments = ", ".join(f"{key} = ?" for key in update_fields.keys())
        params = tuple(update_fields.values()) + (user_id,)
        try:
            self._execute(
                f"UPDATE {self.table_name} SET {assignments} WHERE id = ?",
                params,
            )
        except IntegrityError as exc:
            raise ValueError("Nome de usuario indisponivel. Escolha outro.") from exc
        return self.get_by_id(user_id) or {}


auth_service = AuthService()
