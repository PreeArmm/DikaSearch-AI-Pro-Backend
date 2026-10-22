
import os
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

app = FastAPI(
    title="DikaSearch AI Pro Backend",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://preearmm.github.io",
    ],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

TIMEOUT = httpx.Timeout(60.0, connect=10.0)


def get_upstream():
    base = os.getenv("COLAB_API_BASE", "").strip().rstrip("/")
    return base


@app.get("/")
def root():
    return {
        "service": "DikaSearch AI Pro Backend",
        "status": "running",
        "proxy_configured": bool(get_upstream()),
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "dikasearch-ai-pro-backend",
        "status": "awake",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "proxy_configured": bool(get_upstream()),
    }


async def forward_request(path: str, request: Request):
    base = get_upstream()

    if not base:
        return Response(
            content='{"ok":false,"error":"COLAB_API_BASE is not configured"}',
            status_code=503,
            media_type="application/json",
        )

    url = f"{base}/{path.lstrip('/')}"

    try:
        async with httpx.AsyncClient(
            timeout=TIMEOUT,
            follow_redirects=False,
        ) as client:
            upstream = await client.get(
                url,
                params=request.query_params,
                headers={"Accept": "application/json"},
            )

        content_type = upstream.headers.get(
            "content-type",
            "application/json",
        )

        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            media_type=(
                content_type.split(";")[0]
                if content_type.startswith("application/json")
                else content_type
            ),
        )

    except httpx.TimeoutException:
        return Response(
            content='{"ok":false,"error":"Upstream request timed out"}',
            status_code=504,
            media_type="application/json",
        )

    except httpx.RequestError:
        return Response(
            content='{"ok":false,"error":"Could not reach Colab API"}',
            status_code=502,
            media_type="application/json",
        )


@app.get("/upstream-health")
async def upstream_health(request: Request):
    return await forward_request("/health", request)


@app.get("/filters")
async def filters(request: Request):
    return await forward_request("/filters", request)


@app.get("/search-page")
async def search_page(request: Request):
    return await forward_request("/search-page", request)


@app.get("/document/{document_id}")
async def document(document_id: str, request: Request):
    return await forward_request(
        f"/document/{document_id}",
        request,
    )
