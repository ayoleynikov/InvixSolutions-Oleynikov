from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://catalog:catalog_secret@localhost:5432/catalog"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "products"
    minio_public_url: str = "http://localhost:9000"
    # When unset, public_url omits the bucket segment only for *.r2.dev bases.
    minio_public_url_omit_bucket: bool | None = None
    minio_secure: bool = False
    cors_origins: str = "http://localhost:3000"


settings = Settings()
