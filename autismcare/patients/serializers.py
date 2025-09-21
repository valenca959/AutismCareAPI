from rest_framework import serializers
from .models import Parent, Child
from users.serializers import AutenticationUserSerializer

class ChildSerializer(serializers.ModelSerializer):
    parent = AutenticationUserSerializer(source='parent.user', read_only=True)

    class Meta:
        model = Child
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class ParentSerializer(serializers.ModelSerializer):
    user = AutenticationUserSerializer(read_only=True)
    children = ChildSerializer(many=True, read_only=True)

    class Meta:
        model = Parent
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']