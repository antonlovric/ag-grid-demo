from typing import Any

from pydantic import BaseModel


class SSRMResponse(BaseModel):
    rowData: list[dict[str, Any]]
    rowCount: int | None = None
