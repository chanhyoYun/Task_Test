from rest_framework import serializers
from team.models import User, Team


class TeamSerializer(serializers.ModelSerializer):
    """팀 시리얼라이저

    팀을 저장
    """

    class Meta:
        model = Team
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """유저 시리얼라이저

    유저 정보 시리얼라이저
    """

    class Meta:
        model = User
        fields = ["id", "email", "password", "username", "team"]

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.save()
        return instance
