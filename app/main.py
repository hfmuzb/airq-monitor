from fastapi import FastAPI, Depends
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.cors import CORSMiddleware

from core.config import settings
from api.dependencies.docs_security import basic_http_credentials
from api import v1


description = """
Air quality monitoring project
"""
version = "v0.0.1"

tags_metadata = [
    {
        "name": "Authentication",
        "description": "Authentication logic is described here. Rate limit is set to max 2 requests per 2 seconds.",
    },
]


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=description,
    version=version,
    contact={
        "name": "Khusniddin Fakhritdinov",
        "url": "https://hfmuzb.t.me",
    },
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    openapi_tags=tags_metadata,
)

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=settings.TRUSTED_HOSTS
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(i).rstrip("/") for i in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=settings.ALLOWED_CORS_METHODS,
    allow_headers=settings.ALLOWED_CORS_HEADERS,
)

# include routes here
app.include_router(v1.api_router)


@app.get("/openapi.json", include_in_schema=False)
async def openapi(_: str = Depends(basic_http_credentials)):
    schema = get_openapi(
        title=app.title,
        description=app.description,
        version=app.version,
        contact=app.contact,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    return schema


@app.get(
    "/docs", include_in_schema=False, dependencies=[Depends(basic_http_credentials)]
)
async def get_redoc_documentation():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="FastAPI | Documentation",
    )
