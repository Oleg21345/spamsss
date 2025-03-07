from pydantic import BaseModel


class STelegramAdd(BaseModel):
    number_phone: str

class STelegram(STelegramAdd):
    id: int







