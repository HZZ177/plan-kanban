import httpx
from typing import Optional

from common.core.logger import logger


class HttpClient:
    """异步 HTTP 客户端，基于 httpx 连接池单例"""

    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None:
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(max_connections=200, max_keepalive_connections=50),
            )
            logger.debug("HttpClient 已初始化")
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client is not None:
            await cls._client.aclose()
            cls._client = None
            logger.debug("HttpClient 已关闭")

    @classmethod
    def _truncate(cls, text: str, max_length: int = 500) -> str:
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text

    @classmethod
    async def request(cls, method: str, url: str, **kwargs) -> httpx.Response:
        body = kwargs.get("json") or kwargs.get("data") or kwargs.get("params")
        logger.debug(f"HTTP请求 | {method} {url} | 入参: {body}")

        response = await cls.get_client().request(method, url, **kwargs)

        try:
            import json
            response_data = response.json()
            response_text = cls._truncate(json.dumps(response_data, ensure_ascii=False))
        except Exception:
            response_text = cls._truncate(response.text)

        if response.is_success:
            logger.debug(f"HTTP响应 | {method} {url} | 状态码: {response.status_code} | 返回: {response_text}")
        else:
            logger.error(f"HTTP异常 | {method} {url} | 状态码: {response.status_code} | 返回: {response_text}")
            raise Exception(f"HTTP异常 | {method} {url} | 状态码: {response.status_code} | 返回: {response_text}")

        return response

    @classmethod
    async def get(cls, url: str, **kwargs) -> httpx.Response:
        return await cls.request("GET", url, **kwargs)

    @classmethod
    async def post(cls, url: str, **kwargs) -> httpx.Response:
        return await cls.request("POST", url, **kwargs)

    @classmethod
    async def put(cls, url: str, **kwargs) -> httpx.Response:
        return await cls.request("PUT", url, **kwargs)

    @classmethod
    async def delete(cls, url: str, **kwargs) -> httpx.Response:
        return await cls.request("DELETE", url, **kwargs)

    @classmethod
    async def patch(cls, url: str, **kwargs) -> httpx.Response:
        return await cls.request("PATCH", url, **kwargs)
