from __future__ import annotations

import time

import redis


class RedisClient:
    # 面向 UI 自动化场景的 Redis 轻量封装。
    # 当前只暴露验证码读取相关能力，不扩展成通用缓存客户端，保持职责单一。

    # 初始化 Redis 客户端，封装验证码读取所需的连接参数和键名前缀。
    def __init__(
        self,
        *,
        host: str,
        port: int,
        db: int = 0,
        password: str | None = None,
        socket_timeout: int = 5,
        verification_prefix: str = "verification:code:",
    ) -> None:
        self.verification_prefix = verification_prefix
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=socket_timeout,
            decode_responses=True,
        )

    # 验证 Redis 服务是否可连通，供测试启动阶段快速探活。
    def ping(self) -> bool:
        return bool(self.client.ping())

    # 按邮箱读取验证码缓存值，用于验证码登录场景。
    def get_verification_code(self, email: str) -> str | None:
        return self.client.get(f"{self.verification_prefix}{email}")

    # 在限定时间内轮询验证码，兼容验证码异步写入 Redis 的情况。
    # 没有直接把“读不到验证码”视为异常，而是返回 None，让测试层决定跳过还是失败。
    def wait_for_verification_code(
        self,
        email: str,
        timeout: float = 5.0,
        poll_interval: float = 0.5,
    ) -> str | None:
        end_time = time.monotonic() + timeout
        while time.monotonic() <= end_time:
            code = self.get_verification_code(email)
            if code:
                return code
            time.sleep(poll_interval)
        return None

    # 关闭 Redis 连接，避免会话在测试结束后继续占用资源。
    def close(self) -> None:
        self.client.close()




