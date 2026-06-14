import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)


class MoodleWSException(Exception):
    def __init__(self, message: str, status_code: int = 502) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class MoodleClient:
    def __init__(
        self,
        moodle_url: str,
        ws_token: str,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self._base_url = moodle_url.rstrip("/")
        self._ws_token = ws_token
        self._timeout = timeout
        self._max_retries = max_retries

    async def sync_users(self, course_id: int) -> list[dict]:
        params: dict = {
            "wsfunction": "core_enrol_get_enrolled_users",
            "courseid": course_id,
        }
        return await self._call(params)

    async def _call(self, params: dict) -> list[dict]:
        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.post(
                        f"{self._base_url}/webservice/rest/server.php",
                        params={
                            "wstoken": self._ws_token,
                            "moodlewsrestformat": "json",
                            **params,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    if isinstance(data, dict) and "exception" in data:
                        raise MoodleWSException(
                            f"Moodle WS error: {data.get('message', 'Unknown error')}"
                        )
                    return data
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                last_error = exc
                logger.warning(
                    "Moodle WS call failed (attempt %d/%d): %s",
                    attempt + 1,
                    self._max_retries,
                    exc,
                )
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(2**attempt)
            except MoodleWSException:
                raise

        raise MoodleWSException(
            f"Moodle WS no disponible después de {self._max_retries} intentos: {last_error}"
        )
