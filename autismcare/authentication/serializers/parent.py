from rest_framework import serializers
from ..models.parent import Parent, Child, MedicalRecord, MedicalHistory

class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = '__all__'
        extra_kwargs = {
            'child': {'required': False}  # Remove a obrigatoriedade do campo child
        }


class MedicalRecordSerializer(serializers.ModelSerializer):
    medical_history = MedicalHistorySerializer(many=True, required=False)

    class Meta:
        model = MedicalRecord
        fields = '__all__'
        extra_kwargs = {
            'child': {'required': False}  # Remove a obrigatoriedade do campo child
        }

    def create(self, validated_data):
        # Remove os dados do histórico médico
        medical_history_data = validated_data.pop('medical_history', [])
        
        # Cria o MedicalRecord
        medical_record = MedicalRecord.objects.create(**validated_data)

        # Cria os MedicalHistory associados
        for history_data in medical_history_data:
            MedicalHistory.objects.create(child=medical_record.child, **history_data)

        return medical_record


class ChildSerializer(serializers.ModelSerializer):
    medical_record = MedicalRecordSerializer(required=False)

    class Meta:
        model = Child
        fields = '__all__'
        extra_kwargs = {
            'parent': {'required': False}  # Remove a obrigatoriedade do campo parent
        }

    def create(self, validated_data):
        # Remove os dados do prontuário médico
        medical_record_data = validated_data.pop('medical_record', None)
        
        # Cria o Child
        child = Child.objects.create(**validated_data)

        # Cria o MedicalRecord associado, se houver dados
        if medical_record_data:
            medical_history_data = medical_record_data.pop('medical_history', [])
            medical_record = MedicalRecord.objects.create(child=child, **medical_record_data)

            # Cria os MedicalHistory associados
            for history_data in medical_history_data:
                MedicalHistory.objects.create(child=child, **history_data)

        return child


class ParentSerializer(serializers.ModelSerializer):
    children = ChildSerializer(many=True, required=False)

    class Meta:
        model = Parent
        fields = [
            'id', 'username', 'password', 'email', 'city', 'state', 'zip_code', 'country', 'street', 'number',
            'telephone', 'telephone2', 'birthdate', 'cpf', 'spouse', 'children'
        ]
        extra_kwargs = {
            'password': {'write_only': True}  # A senha não será retornada na resposta
        }

    def create(self, validated_data):
        # Remove os dados dos filhos
        children_data = validated_data.pop('children', [])
        
        # Cria o Parent
        parent = Parent.objects.create_user(**validated_data)

        # Cria os filhos e seus objetos relacionados
        for child_data in children_data:
            # Adiciona o parent ao child_data
            child_data['parent'] = parent
            
            # Remove os dados do prontuário médico
            medical_record_data = child_data.pop('medical_record', None)
            
            # Cria o Child
            child = Child.objects.create(**child_data)

            # Cria o MedicalRecord associado, se houver dados
            if medical_record_data:
                medical_history_data = medical_record_data.pop('medical_history', [])
                medical_record = MedicalRecord.objects.create(child=child, **medical_record_data)

                # Cria os MedicalHistory associados
                for history_data in medical_history_data:
                    MedicalHistory.objects.create(child=child, **history_data)

        return parent

    def update(self, instance, validated_data):
        # Remove os dados dos filhos
        children_data = validated_data.pop('children', [])
        
        # Atualiza os campos do Parent
        instance = super().update(instance, validated_data)

        # Atualiza ou cria os filhos e seus objetos relacionados
        for child_data in children_data:
            child_id = child_data.get('id', None)
            if child_id:
                # Atualiza o Child existente
                child = Child.objects.get(id=child_id, parent=instance)
                for attr, value in child_data.items():
                    setattr(child, attr, value)
                child.save()
            else:
                # Cria um novo Child
                child_data['parent'] = instance
                medical_record_data = child_data.pop('medical_record', None)
                child = Child.objects.create(**child_data)

                # Cria o MedicalRecord associado, se houver dados
                if medical_record_data:
                    medical_history_data = medical_record_data.pop('medical_history', [])
                    medical_record = MedicalRecord.objects.create(child=child, **medical_record_data)

                    # Cria os MedicalHistory associados
                    for history_data in medical_history_data:
                        MedicalHistory.objects.create(child=child, **history_data)

        return instance