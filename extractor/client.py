import time
import requests
from pathlib import Path
import sys

# Allow imports from the same folder
sys.path.append(str(Path(__file__).resolve().parent))

from config import (
    API_BASE_URL,
    API_KEY,
    DEFAULT_PAGE_SIZE,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    BACKOFF_BASE_SECONDS,
)


class ERPClient:
    def __init__(self):
        if not API_KEY:
            raise ValueError("Missing API key. Check your .env file or environment variables.")

        self.base_url = API_BASE_URL.rstrip("/")
        self.headers = {
            "X-API-Key": API_KEY,
            "Accept": "application/json",
        }

    def _request_with_retry(
        self,
        endpoint: str,
        params: dict | None = None,
        page_label: str | None = None,
    ):
        url = f"{self.base_url}{endpoint}"
        label = page_label or endpoint

        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=REQUEST_TIMEOUT,
                )

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    wait_time = int(retry_after) if retry_after else BACKOFF_BASE_SECONDS * (2 ** attempt)
                    print(f"[429] {label} | attempt {attempt + 1}/{MAX_RETRIES} | waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue

                if response.status_code >= 500:
                    wait_time = BACKOFF_BASE_SECONDS * (2 ** attempt)
                    print(f"[{response.status_code}] {label} | attempt {attempt + 1}/{MAX_RETRIES} | retrying in {wait_time}s")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                wait_time = BACKOFF_BASE_SECONDS * (2 ** attempt)
                print(f"[Timeout] {label} | attempt {attempt + 1}/{MAX_RETRIES} | retrying in {wait_time}s")
                time.sleep(wait_time)

            except requests.exceptions.ConnectionError:
                wait_time = BACKOFF_BASE_SECONDS * (2 ** attempt)
                print(f"[ConnectionError] {label} | attempt {attempt + 1}/{MAX_RETRIES} | retrying in {wait_time}s")
                time.sleep(wait_time)

            except requests.exceptions.SSLError:
                wait_time = BACKOFF_BASE_SECONDS * (2 ** attempt)
                print(f"[SSLError] {label} | attempt {attempt + 1}/{MAX_RETRIES} | retrying in {wait_time}s")
                time.sleep(wait_time)

            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"Request failed for {url}: {e}") from e

        raise RuntimeError(f"Max retries exceeded for {label}")

    def get_page(
        self,
        endpoint: str,
        cursor: str | None = None,
        updated_after: str | None = None,
        page_num: int | None = None,
    ):
        params = {"limit": DEFAULT_PAGE_SIZE}

        if cursor:
            params["cursor"] = cursor

        if updated_after:
            params["updated_after"] = updated_after

        page_label = f"page {page_num}" if page_num else "request"

        return self._request_with_retry(
            endpoint=endpoint,
            params=params,
            page_label=page_label,
        )
