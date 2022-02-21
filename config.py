from typing import Optional
from pydantic import BaseSettings
from functools import lru_cache

class APISettings(BaseSettings):
    server_host: str = "127.0.0.1"
    server_port: int = 8000
    title: str = "FastAPI"
    description: str = ""
    version: str = "0.0.1"
    debug: bool = False
    openapi_url: Optional[str] = "/openapi.json"
    js_driver :str =""
    chorme_driver:str =""
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = APISettings()

@lru_cache(100)
def getFastSetting():
    """
    TODO Next"""
    return APISettings()