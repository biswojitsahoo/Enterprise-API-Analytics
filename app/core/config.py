from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise API Management & Analytics"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    secret_key: str = "unsafe-development-secret-change-me"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./enterprise_api.db"
    seed_admin: bool = True
    admin_email: str = "admin@example.com"
    admin_password: str = "ChangeMe123!"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
