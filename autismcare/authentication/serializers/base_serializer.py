from rest_framework import serializers
from authentication.models.base import AutenticationUser, Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id',
            'city',
            'state',
            'zip_code',
            'country',
            'street',
            'number',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

class AutenticationUserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    user_type = serializers.SerializerMethodField()

    class Meta:
        model = AutenticationUser
        fields = [
            'id',
            'email',
            'username',
            'address',
            'telephone',
            'telephone2',
            'birthdate',
            'cpf',
            'first_name',
            'last_name',
            'user_type',
            'date_joined',
            'is_active',
            'is_staff',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['date_joined', 'is_active', 'is_staff', 'created_at', 'updated_at']

    def get_user_type(self, obj):
        return obj.get_user_type()