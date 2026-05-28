from typing import Optional

from pydantic import BaseModel


class ProblemDetail(BaseModel):
    type : str = "about:blank"
    title : str
    status : int
    detail : str
    instance : Optional[str] = None
