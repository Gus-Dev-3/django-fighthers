from rest_framework import serializers
from .models import StarGGTournament, ChallongeTournament, Post,StreamUser


class StarGGTournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StarGGTournament
        fields = ['url_tournament', 'is_completed']

    def create(self, validated_data):
        return StarGGTournament.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.url_tournament = validated_data.get('url_tournament', instance.url_tournament)
        instance.is_completed = validated_data.get('is_completed', instance.is_completed)
        instance.save()
        return instance

class ChallongeTournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallongeTournament
        fields = ['name', 'idTournament', 'is_completed','flayer_img','game_name', 'sign_up_url', 'start_at','stream_url']

    def create(self, validated_data):
        return ChallongeTournament.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.idTournament = validated_data.get('idTournament', instance.idTournament)
        instance.is_completed = validated_data.get('is_completed', instance.is_completed)
        instance.save()
        return instance

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"

class StreamUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamUser
        fields = ['user_name', 'platform']  # Los campos que quieres incluir en la respuesta