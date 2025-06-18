from pydantic import BaseModel

class Token(BaseModel):
    """用于返回给用户的令牌"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """存储在令牌中的数据"""
    username: str | None = None