from rest_framework import serializers


class IBANSerializer(serializers.Serializer):
    iban = serializers.CharField(max_length=34)
    country = serializers.CharField(max_length=100)

    class Meta:
        fields = ("iban", "country")
