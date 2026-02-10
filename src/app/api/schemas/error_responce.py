from pydantic import BaseModel

class ErrorResponce(BaseModel):
    er_message: str
    er_details: str
    status_code: int