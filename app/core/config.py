from pydantic_settings import BaseSettings
from pydantic import Field
from urllib.parse import quote_plus

class Settings(BaseSettings):
    postgres_host: str = Field(alias="POSTGRES_HOST")
    postgres_port: int = Field(alias="POSTGRES_PORT")
    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")

    @property
    def DATABASE_URL(self) -> str:
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql+psycopg2://"
            f"{self.postgres_user}:{password}@"
            f"{self.postgres_host}:{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    VECTOR_STORE_PATH: str = "./data/chroma_db"

    model_config = {
        "env_file": ".env",
        "extra": "forbid"
    }

settings = Settings()
