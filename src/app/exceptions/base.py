class AppException(Exception):
    status_code: int = 500
    message: str = "Internal server error"
    details: str | None = None

    def __init__(self, message: str | None = None, details: str | None = None):
        super().__init__(message)
        if message:
            self.message = message
        self.details = details