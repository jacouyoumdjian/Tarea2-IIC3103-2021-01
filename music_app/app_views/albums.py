from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from base64 import b64encode
from .. import models


api_url = 'https://t2-iic3103-jacouyoumdjian.herokuapp.com/'


@api_view(["POST", "GET"])
def artists_albums(request, artist_id):  # artists/<str:artist_id>/albums

    album_artist = models.Artist.objects.filter(identificador=artist_id)
    data_album_artist = list(album_artist.values())

    if request.method not in ('GET', 'POST'):
        return HttpResponse(status=405)

    if request.method == 'GET':  # GET all albums from artist artist_id

        if data_album_artist:
            all_albums = models.Album.objects.filter(
                artist_id_id=data_album_artist[0]['id'])
            data_albums = list(all_albums.values())
            for album in data_albums:
                album["self"] = album["myself"]
                del album["myself"]
                del album["id"]
                del album["identificador"]
                del album["artist_id_id"]
            return JsonResponse(data_albums, safe=False, status=200)

        else:
            return JsonResponse({"mesagge": "álbum no encontrado"}, status=404)

    elif request.method == 'POST':  # POST new album from artist artist_id

        if not data_album_artist:  # si es que el artista no existe
            return JsonResponse({"mesagge": "artista no existe"}, status=422)

        valid_inputs = []
        album_data = request.data
        for key in album_data.keys():
            valid_inputs.append(key)

        if valid_inputs != ['name', 'genre']:
            return JsonResponse({"mesagge": "Invalid input"}, safe=False, status=400)

        else:
            request_name = request.data["name"]
            request_genre = request.data["genre"]
            if (type(request_name) != str) or (type(request_genre) != str):
                return JsonResponse({"mesagge": "Invalid input"}, status=400)

        encoded = b64encode(album_data['name'].encode()).decode('utf-8')
        exists_album = models.Album.objects.filter(identificador=encoded)
        data_album = list(exists_album.values())

        if not data_album:
            new_album = models.Album.objects.create(name=album_data['name'],
                                                    identificador=encoded[0:22],
                                                    genre=album_data['genre'],
                                                    artist_id_id=data_album_artist[0]['id'],
                                                    artist=api_url +
                                                    f'artists/{artist_id}',
                                                    tracks=api_url +
                                                    f'albums/{encoded[0:22]}/tracks',
                                                    myself=api_url +
                                                    f'albums/{encoded[0:22]}',
                                                    )
            new_album.save()
            new_album = models.Album.objects.filter(id=new_album.id)
            data_new_album = list(new_album.values())
            data_new_album[0]["self"] = data_new_album[0]["myself"]
            del data_new_album[0]["myself"]
            del data_new_album[0]["id"]
            del data_new_album[0]["identificador"]
            del data_new_album[0]["artist_id_id"]
            return JsonResponse(data_new_album[0], safe=False, status=201)

        else:
            data_album[0]["self"] = data_album[0]["myself"]
            del data_album[0]["myself"]
            del data_album[0]["id"]
            del data_album[0]["identificador"]
            del data_album[0]["artist_id_id"]
            return JsonResponse(data_album[0], safe=False, status=409)


@ api_view(["GET"])  # albums
def albums(request):

    if request.method not in ('GET', 'POST'):
        return HttpResponse(status=405)

    if request.method == 'GET':  # GET all albums
        data_albums = list(models.Album.objects.values())
        for album in data_albums:
            album["self"] = album["myself"]
            del album["myself"]
            del album["id"]
            del album["identificador"]
            del album["artist_id_id"]
        return JsonResponse(data_albums, safe=False, status=200)


@ api_view(["GET", "DELETE"])  # albums/<str:album_id>
def albums_detail(request, album_id):

    album = models.Album.objects.filter(identificador=album_id)
    data_album = list(album.values())

    if request.method == 'GET':  # GET album with album_id
        if data_album:
            data_album[0]["self"] = data_album[0]["myself"]
            del data_album[0]["myself"]
            del data_album[0]["id"]
            del data_album[0]["identificador"]
            del data_album[0]["artist_id_id"]
            return JsonResponse(data_album[0], safe=False, status=200)
        else:
            return JsonResponse({"mesagge": "álbum no encontrado"}, status=404)

    elif request.method == 'DELETE':  # DELETE artist with artist_id
        if data_album:
            album.delete()
            return JsonResponse({"mesagge": "álbum eliminado"}, status=204)
        else:
            return JsonResponse({"mesagge": "álbum no encontrado"}, status=404)
