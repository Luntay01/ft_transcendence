from rest_framework import serializers

class OauthCodeSerializer(serializers.Serializer):
    code = serializers.CharField()
    state = serializers.CharField()