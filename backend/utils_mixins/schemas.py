from typing import Optional
from ninja import Schema
from ninja.orm import ModelSchema
from django.contrib.auth import get_user_model


User = get_user_model()


class MessageSchema(Schema):
    code: Optional[int] = None
    detail: str


class LightUserDetailOut(ModelSchema):

    class Meta:
        model = User
        fields = '__all__'
        exclude = ['password']
    
