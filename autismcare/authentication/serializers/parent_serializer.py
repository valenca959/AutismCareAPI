from rest_framework import serializers
from authentication.models.parent import Parent
from .base_serializer import AutenticationUserSerializer
from .child_serializer import ChildSerializer

class ParentSerializer(serializers.ModelSerializer):
    user = AutenticationUserSerializer(read_only=True)
    children = ChildSerializer(many=True, read_only=True)

    class Meta:
        model = Parent
        fields = [
            'id',
            'user',
            'spouse',
            'spouse_phone',
            'children',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']