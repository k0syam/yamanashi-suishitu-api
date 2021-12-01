import datetime
from pydantic import BaseModel

__all__ = ['DataItem']

class DataItem(BaseModel):
    source_name: str
    measurement_point: str
    measurement_date: datetime.date
    weather: str
    category: str
    value: str
