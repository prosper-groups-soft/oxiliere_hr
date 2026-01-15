from typing import Optional
from ninja.orm import ModelSchema
from django.contrib.auth import get_user_model
from ninja import FilterSchema


User = get_user_model()
    

class LightUserOut(ModelSchema):

    class Meta:
        model = User
        fields = '__all__'
        fields_optional ='__all__'


class BaseFilter(FilterSchema):
    search: Optional[str] = None

