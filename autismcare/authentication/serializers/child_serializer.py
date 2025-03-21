from rest_framework import serializers
from authentication.models.child import Child
from .parent_serializer import ParentSerializer

class ChildSerializer(serializers.ModelSerializer):
    parent = ParentSerializer(read_only=True)

    class Meta:
        model = Child
        fields = [
            'id',
            'parent',
            'first_name',
            'last_name',
            'birthdate',
            'gender',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']