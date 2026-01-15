"""ADMS API - メインエントリーポイント"""

from fastapi import FastAPI

app = FastAPI(
    title="ADMS API",
    description="Advanced Drone Management System API",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}
