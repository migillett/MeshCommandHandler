from pydantic import BaseModel, Field


class ResponseBase(BaseModel):
    message: str


class UserResponse(ResponseBase):
    """Designates when we need to send a DM to a specific user"""

    user_id: str


class ChannelResponse(ResponseBase):
    """Designates when we need to send a response to a specific channel"""

    channel_id: str


class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, allow_inf_nan=False)
    longitude: float = Field(..., ge=-180.0, le=180.0, allow_inf_nan=False)

    def to_message(self) -> str:
        return f"{round(self.latitude, 6)},{round(self.longitude, 6)}"
