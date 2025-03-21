from rest_framework import serializers
from authentication.models.role import Role

class RoleSerializer(serializers.ModelSerializer):
    parent_role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), allow_null=True)

    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'description',
            'permissions',
            'parent_role',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']