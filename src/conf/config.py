""" Configuration module for the application. """


class Config:
    """Configuration class for the application."""

    DB_URL = "postgresql+asyncpg://postgres:mysecretpassword@localhost:5432/hw8"


config = Config()
