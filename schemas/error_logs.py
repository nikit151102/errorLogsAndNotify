from pydantic import BaseModel

class ErrorResponseDto(BaseModel):
    httpStatus: int
    userMessage: str
    details: str
    exception: str
    timestamp: str
    stackTrace: str

class FrontendErrorLogDto(BaseModel):
    errorMessage: str
    details: str
    url: str
    username: str
    timestamp: str
