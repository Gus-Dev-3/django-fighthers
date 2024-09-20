from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import traceback
import requests
from django.conf import settings
from .utils import extract_tournament_id, has_passed_and_more_than_3_days
from .models import StarGGTournament, ChallongeTournament,Post,StreamUser
from .serializers import StarGGTournamentSerializer, ChallongeTournamentSerializer, PostSerializer,StreamUserSerializer
from django.core.cache import cache
import challonge

class StarGGTournamentListView(APIView):
    def get(self, request, format=None):
        tournaments = StarGGTournament.objects.all()
        serializer = StarGGTournamentSerializer(tournaments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ChallongeTournamentListView(APIView):
    def get(self, request, format=None):
        tournaments = ChallongeTournament.objects.all()
        serializer = ChallongeTournamentSerializer(tournaments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostListView(APIView):
    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        

class TournamentEventsView(APIView):

    
    def get(self, request, *args, **kwargs):
        # URL de la API de GraphQL
        url = settings.URL_STARTGG_API
        
        # La query de GraphQL
        query = """
        query TournamentEvents($tourneySlug: String!) {
            tournament(slug: $tourneySlug) {
                id
                name
                endAt
                events {
                    id
                    name
                    startAt
                    state
                    rulesMarkdown
                    slug
                    numEntrants
                    videogame {
                        id
                        name
                        images {
                            url
                        }
                    }
                }
            }
        }
        """
        
        # Variables para la query
        variables = {
            "tourneySlug": request.query_params.get("idTournament", "default-slug"),
        }

        # Encabezados de la solicitud
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.TOKEN_STARTGG_API}"
        }

        # Cuerpo de la solicitud
        payload = {
            "query": query,
            "variables": variables
        }

        try:
            # Realizar la solicitud POST a la API de GraphQL
            response = requests.post(url, json=payload, headers=headers)
            response_data = response.json()

            # Obtener el valor endAt del primer evento en la respuesta
            end_at_timestamp = response_data.get('data', {}).get('tournament', {}).get('endAt')
            
            # Verificar si la fecha y hora del torneo han pasado más de 3 días
            if end_at_timestamp and has_passed_and_more_than_3_days(end_at_timestamp):
                # Buscar la instancia del torneo usando un filtro que contenga el idTournament
                tournament_id = request.query_params.get("idTournament", "default-slug")
                try:
                    tournament_instance = StarGGTournament.objects.get(url_tournament__icontains=tournament_id)
                    # Setear is_completed a True
                    tournament_instance.is_completed = True
                    tournament_instance.save()
                    print("El atributo is_completed se ha actualizado a True.")
                except StarGGTournament.DoesNotExist:
                    print("No se encontró el torneo con el id proporcionado.")
            else:
                print("La fecha y hora no han pasado más de 3 días.")
            
            # Retornar la respuesta de la API en formato JSON
            return Response(response_data, status=response.status_code)

        except requests.exceptions.RequestException as e:
            # Manejar errores de la solicitud
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Configura las credenciales de Challonge
challonge.set_credentials(settings.CHALLONGE_USERNAME, settings.CHALLONGE_API_KEY)

class TournamentDetailsChallongeView(APIView):
    
    def get(self, request, tournament_id, *args, **kwargs):
        print(tournament_id)

        try:
            # Recupera la información del torneo desde Challonge
            tournament = challonge.tournaments.show(tournament_id)
            participants = challonge.participants.index(tournament_id)

            # Prepara la respuesta con la información del torneo y los participantes
            data = {
                "tournament": {
                    "id": tournament.get("id"),
                    "name": tournament.get("name"),
                    "state": tournament.get("state"),
                    "tournament_type": tournament.get("tournament_type"),
                    "participants": participants,
                    "start_at": tournament.get("start_at"),
                    "description": tournament.get("description"),
                    "live_image_url": tournament.get("live_image_url"),
                    "private": tournament.get("private"),
                    "sign_up_url": tournament.get("sign_up_url"),
                    "game_name": tournament.get("game_name"),
                    "participants_count": tournament.get("participants_count"),
                },
                "participants_count": len(participants),
            }

            # Intenta obtener la instancia del torneo en la base de datos
            try:
                tournament_instance = ChallongeTournament.objects.get(idTournament=tournament_id)

                # Actualiza el modelo según los datos obtenidos de la API
                if tournament_instance.sign_up_url == "" and "sign_up_url" in data["tournament"] and data["tournament"]["sign_up_url"]:
                    tournament_instance.sign_up_url = data["tournament"]["sign_up_url"]
                    tournament_instance.save()

                if tournament_instance.start_at is None and "start_at" in data["tournament"] and data["tournament"]["start_at"]:
                    tournament_instance.start_at = data["tournament"]["start_at"]
                    tournament_instance.save()

                if tournament_instance.game_name == "" and "game_name" in data["tournament"] and data["tournament"]["game_name"]:
                    tournament_instance.game_name = data["tournament"]["game_name"]
                    tournament_instance.save()

                if tournament_instance.name == "Pendiente" and "name" in data["tournament"] and data["tournament"]["name"]:
                    tournament_instance.name = data["tournament"]["name"]
                    tournament_instance.save()

                if data["tournament"]["state"] == "complete" and not tournament_instance.is_completed:
                    tournament_instance.is_completed = True
                    tournament_instance.save()

            except ChallongeTournament.DoesNotExist:
                # Si el torneo no está en la base de datos, simplemente muestra un mensaje
                print(f"Tournament instance with ID {tournament_id} does not exist in the database.")

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            # Agrega esto para depuración
            print(f"Unexpected error: {e}")
            print(traceback.format_exc())  # Imprime la traza completa del error
            return Response({"error": f"An unexpected error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TwitchUserOnline(APIView):

    def get(self, request, format=None):
        # Obtener todos los usuarios que tienen como plataforma Twitch
        users = StreamUser.objects.filter(platform='TW')
        
        # Verificar si no hay usuarios en la base de datos
        if not users.exists():
            return Response({'error': 'No hay usuarios registrados en la plataforma'}, status=status.HTTP_404_NOT_FOUND)
        
        live_users = []
        headers = {
            'Client-ID': settings.TWITCH_CLIENT_ID,
            'Authorization': 'Bearer ' + settings.TWITCH_JWT_TOKEN
        }
        
        # Primero, obtenemos los streams en vivo
        stream_data = []
        for user in users:
            url = f'https://api.twitch.tv/helix/streams?user_login={user.user_name}'
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data['data']:  # La lista 'data' no está vacía, significa que el usuario está en vivo
                    stream_info = data['data'][0]
                    stream_info['user_login'] = user.user_name  # Guardamos el nombre de usuario para la siguiente solicitud
                    stream_data.append(stream_info)
            else:
                continue
        
        if not stream_data:
            return Response({'error': 'No hay usuarios en vivo'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ahora obtenemos la información de los usuarios para agregar `profile_image_url`
        for stream_info in stream_data:
            user_login = stream_info['user_login']
            url = f'https://api.twitch.tv/helix/users?login={user_login}'
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data['data']:
                    user_info = data['data'][0]
                    # Agregamos `profile_image_url` a la información del stream
                    stream_info['profile_image_url'] = user_info['profile_image_url']
            else:
                stream_info['profile_image_url'] = None  # Si la solicitud falla, podemos agregar un valor por defecto

        # Ahora serializamos los datos y retornamos la respuesta
        response_data = []
        for stream_info in stream_data:
            user_data = next((user for user in users if user.user_name == stream_info['user_login']), None)
            if user_data:
                serialized_user = StreamUserSerializer(user_data).data
                stream_info['channel'] = serialized_user  # Anidar la información del usuario
                response_data.append(stream_info)

        return Response({"streamers": response_data}, status=status.HTTP_200_OK)
    

class YouTubeChannelsView(APIView):
    API_KEY = settings.GOOGLE_API_KEY

    def get(self, request):
        cache_key = 'youtube_live_channels'
        cached_results = cache.get(cache_key)

        if cached_results is not None:
            return Response(cached_results, status=status.HTTP_200_OK)

        results = []
        users = StreamUser.objects.filter(platform='YT')
        
        # Verificar si no hay usuarios en la base de datos
        if not users.exists():
            return Response({'error': 'No hay usuarios registrados en la plataforma'}, status=status.HTTP_404_NOT_FOUND)

        for user in users:
            channel_id = user.user_name  # Usar user_name como channel_id para YouTube
            # 1. Verificar si está en vivo
            live_check_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=live&key={self.API_KEY}'
            live_response = requests.get(live_check_url)

            if live_response.status_code != 200:
                continue  # Si falla la consulta, simplemente salta al siguiente canal

            live_data = live_response.json()

            if live_data['items']:
                video_id = live_data['items'][0]['id']['videoId']
                live_url = f'https://www.youtube.com/watch?v={video_id}'  # URL para redirigir al video en vivo

                # 2. Obtener estadísticas del canal
                channel_stats_url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={self.API_KEY}'
                channel_response = requests.get(channel_stats_url)

                if channel_response.status_code != 200:
                    continue  # Salta si no se puede obtener la información del canal

                channel_data = channel_response.json()

                if channel_data['items']:
                    channel_name = channel_data['items'][0]['snippet']['title']
                    profile_image = channel_data['items'][0]['snippet']['thumbnails']['default']['url']  # URL de la foto de perfil

                    # 3. Obtener detalles del video en vivo
                    live_details_url = f'https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id={video_id}&key={self.API_KEY}'
                    details_response = requests.get(live_details_url)

                    if details_response.status_code != 200:
                        continue  # Salta si no se puede obtener los detalles del video en vivo

                    details_data = details_response.json()
                    viewers = details_data['items'][0]['liveStreamingDetails'].get('concurrentViewers', None)

                    results.append({
                        "channel_name": channel_name,
                        "profile_image": profile_image,
                        "viewers": viewers,
                        "live_url": live_url  # URL para ver el video en vivo
                    })

        # Cachear resultados, incluso si está vacío
        cache.set(cache_key, results, timeout=600)

        # Retorna una lista vacía si no hay resultados
        return Response(results, status=status.HTTP_200_OK if results else status.HTTP_204_NO_CONTENT)