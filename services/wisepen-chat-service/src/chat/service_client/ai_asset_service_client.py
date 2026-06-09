from __future__ import annotations

from typing import Optional

from common.core.exceptions import RpcError
from common.http.rpc_client import RpcClient


_DEFAULT_SERVICE_NAME = "wisepen-ai-asset-service"
_GET_PUBLISHED_SKILL_PATH = "/internal/skill/getPublishedSkillByResourceId"


class AIAssetClient:
    def __init__(
        self,
        rpc: RpcClient,
        *,
        service_name: str = _DEFAULT_SERVICE_NAME,
    ) -> None:
        self._rpc = rpc
        self._service_name = service_name

    async def get_published_skill_by_resource_id(self, resource_id: str) -> Optional[dict]:
        resource_id = (resource_id or "").strip()
        if not resource_id:
            return None
        try:
            data = await self._rpc.get(
                self._service_name,
                _GET_PUBLISHED_SKILL_PATH,
                params={"resourceId": resource_id},
            )
        except RpcError as e:
            raise e
        if not isinstance(data, dict):
            raise RpcError(
                service_name=self._service_name, path=_GET_PUBLISHED_SKILL_PATH,
                msg=f"unexpected data payload: {data!r}",
            )
        return data
