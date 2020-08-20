import ytkey
import base64
import requests
import datetime
from urllib.parse import urlencode
client_id = ytkey.client_id #archivo que contiene las claves
client_secret = ytkey.client_secret
#para realizar la conexión a la api es necesario obtener 2 tokens de acceso de cliente
#uno de estoss tokens se debe codificar en 64b para ser enviado en la petición a la api
#clase principal de scripts para hacer consultas con spotify api
class SpotifyAPI(object):
    access_token = None #asigna un valor inicial al token de acceso
    access_token_expires = datetime.datetime.now() #setea la hora actual para hacer verificacion de caducidad
    access_token_did_expire = True #verifica si el token expiro
    client_id = None #id cliente none
    client_secret = None #clave secreta cliente none
    token_url = "https://accounts.spotify.com/api/token"#url para obtener el token
    
    def __init__(self, client_id, client_secret, *args, **kwargs): #función inicial
        super().__init__(*args, **kwargs)
        self.client_id = client_id #asigna los valores para la autenticacion
        self.client_secret = client_secret

    def get_client_credentials(self): #obtiene las credenciales del cliente
        """
        retorna un token encodeado en base 64byts
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None: #si los valores estan vacios
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"#client credentials = id:secret
        client_creds_b64 = base64.b64encode(client_creds.encode())#encode en base 64
        return client_creds_b64.decode()#retorna el valor de la cerendcial de acceso
    
    def get_token_headers(self):#define el header para obtener el token
        client_creds_b64 = self.get_client_credentials()#obtiene el valor de get_client_credentials
        return {
            "Authorization": f"Basic {client_creds_b64}" #devuelve un dict con el header del token de usuario
        }
    
    def get_token_data(self): #header 2 para acreditar las credenciales del cliente
        return {
            "grant_type": "client_credentials"
        } 
    
    def perform_auth(self): #realiza la autenticación del token
        token_url = self.token_url #url del token
        token_data = self.get_token_data() #data del token
        token_headers = self.get_token_headers()#headers del token
        r = requests.post(token_url, data=token_data, headers=token_headers) #request con los datos del token de acceso
        if r.status_code not in range(200, 299): #verifica que la request sea correcta (esta en rango 200-299)
            raise Exception("Could not authenticate client.")#sino entrega error
        data = r.json() #asigna a data el valor de la respuesta
        now = datetime.datetime.now() #fecha de ahora
        access_token = data['access_token'] #token de acceso
        expires_in = data['expires_in'] # en cuanto tiempo en segundos expira el token
        expires = now + datetime.timedelta(seconds=expires_in) #cuando expira el token
        self.access_token = access_token 
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now #toma los datos del token y verifica que no esté vencido
        return True
    
    def get_access_token(self): #usa las funciones anteriores para obtener el token de acecso (incluyendo la autenticación de este)
        token = self.access_token #obtiene el token de la funcion access_token
        expires = self.access_token_expires #obtiene el valor de expiracion
        now = datetime.datetime.now()#valor actual
        if expires < now: #verifica si expiro
            self.perform_auth()
            return self.get_access_token()
        elif token == None: #si no hay token
            self.perform_auth()
            return self.get_access_token() 
        return token #devuelve el token
    
    def get_resource_header(self): #obtener el header del recurso para /search,get_album,_get_artist
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    def get_resource(self, lookup_id, resource_type='albums', version='v1'): #variable url a buscar, y tipo de busqueda
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}" #endpoint
        headers = self.get_resource_header() #obtiene el header para la consulta
        r = requests.get(endpoint, headers=headers) #consulta
        if r.status_code not in range(200, 299): #si la respuesta es correcta (rango 200 -299)
            return {}
        return r.json() #retorna la respuesta
    
    def get_album(self, _id): #información de un album con un id
        return self.get_resource(_id, resource_type='albums')
    
    def get_artist(self, _id):#información de un artista con un id
        return self.get_resource(_id, resource_type='artists')

    def get_seeds(self, _dic): #obtener seeds/semillas de un diccionario de datos con varios artistas y ttracks
        i = 0 
        s_tracks = []
        s_artists = []
        for i in range(2):#busca 2 artistas y tracks por cada dict ya que la query solo soporta 4 claves para la busqueda
            s_tracks.append(_dic['hits']['tracks'][int(i)]['cancion_id'])#crea una lista con tracks ids
            s_artists.append(_dic['hits']['tracks'][int(i)]['art'][0]['id'])#crea una lista con artistas id
        seeds = {'seed_artists':s_artists,'seed_tracks':s_tracks} #asigna a un diccionario las listas de ids
        return seeds#retorna las semillas o seeds

    def get_related_header(self): #obtener el header para las busquedas relacionadas a artistas/tracks
        access_token = self.get_access_token()
        headers = { #definición del header
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            "Authorization": f"Bearer {access_token}"
        }
        return(headers)

    def get_artist_albums(self, _id, limit = '3'):#obtiene los albumes de un artista por defecto 3
        endpoint = 'https://api.spotify.com/v1/artists/'+_id+'/albums?limit='+limit #url de busqueda /endpoing+query
        headers = self.get_resource_header() #headers para la busqueda
        r = requests.get(endpoint, headers=headers) #request
        return r.json()

    def get_artist_top_tracks(self, _id):#obtener top tracks de un artista
        endpoint = 'https://api.spotify.com/v1/artists/'+_id+'/top-tracks?country=cl'#endpoint +query
        headers = self.get_related_header()#get headers
        r = requests.get(endpoint, headers=headers)#request
        print(r.status_code)
        return r.json()

    def base_related__tracks_search(self,query_params): #base de busqueda para tracks relacionados
        headers = self.get_related_header()
        endpoint = 'https://api.spotify.com/v1/recommendations?'
        lookup_url = f"{endpoint}{query_params}" #necesito una url con la forma endpoint?search_artists='id_artista'&sarch_tracks='_idtracks' separados por coma o %2C
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299):  #si la respuesta es incorrecta
            return {}
        return r.json()

    def related_tracks_search(self, seeds = {}, limit = '5'):#busqueda de tracks relacionados
        if seeds == None: #si no hay seeds
            raise Exception('necesitas seeds para la busqueda') #generar expeción
        if isinstance(seeds, dict): #si las seeds son un diccionario manipular
            #Esta sección manipula el dict seeds para realizar una query de busqueda
            query = " ".join([f"{k}:{v}" for k,v in seeds.items()])
            a = query.replace('[', '')
            a = a.replace(']', '')
            a = a.replace("'",'')
            a = a.replace(' ','')
            a = a.replace(',','%2C')
            num = a.find("seed_tracks")
            a = a[:num] + '&' + a[num:]
            a = a.replace(':','=')
            a = a+'&limit='+limit
            #finalmente a =endpoint?seed_artists=id1%2Cid2&seed_tracks=id1%2Cid2
        related = self.base_related__tracks_search(a) #usa la busqueda base
        cont = 0
        for i in related['tracks']: #eliminación de datos no deseados
            related['tracks'][cont].pop('available_markets')
            related['tracks'][cont].pop('external_ids')
            cont += 1
        return related #devuelve las canciones relacionadas a un cancion
    
    def base_related__artists_search(self, _id =''): #busqueda base que devuelve aritstas relacionados a otro artista
        headers = self.get_related_header()#obtiene l header
        endpoint = 'https://api.spotify.com/v1/artists/'+_id+'/related-artists?limit=5' #endping + query
        r = requests.get(endpoint, headers=headers) #request
        if r.status_code not in range(200, 299):  #si no es correcto
            return {}
        return r.json() #devuelve la respuesta

    def related_artists_search(self, _id = ''): #busqueda que devuelve artistas relacionados a otro artista
        if _id == ' ': #si la id esta vacia
            raise Exception('necesitas una id para la busqueda') #raise error
        related = self.base_related__artists_search(_id)#llama a la función base
        return related #imprime el resultado de la request

    def base_search(self, query_params): # busqueda base para canciones
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}" #url de busqueda
        r = requests.get(lookup_url, headers=headers) #consulta
        if r.status_code not in range(200, 299):  
            return {}
        return r.json()

    def search(self, query=None, operator=None, operator_query=None, search_type='artist',limit='5' ):#busqueda para canciones
        if query == None:
            raise Exception("A query is required") #exepcion si no hay query/consulta
        if isinstance(query, dict): #si la query es un diccionario
            query = " ".join([f"{k}:{v}" for k,v in query.items()]) #une valores para darle formato
        if operator != None and operator_query != None: #manejador de operadores
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({"q": query, "type": search_type.lower(),'limit':limit}) #junta y codifica la query + el tipo de busqueda
        return self.base_search(query_params)

    def get_songs_full(self, _hint = ' '):
        '''Esta función devuelve un dict refinado de datos con la información relacionada a la busqueda
        de una canción, el dict contiene información de: canciones relacionadas, artistas relacionados, 
        hints de canciones de la busqueda, album de la canción, información del track, información del artista'''
        s = SpotifyAPI(client_id, client_secret)#llamada a la función principal
        get_track = s.search({"track": _hint}, search_type="track")#usar función search
        cont = 0 #contador
        tracks_info = {'hits':{'tracks':{cont:{'art':{},'album':{},'art_detail':{}}},'related':{'tracks':{},'artists':{}}}}
        #creación de la estructura del diccionario refinado
        for i in range (len(get_track['tracks']['items'])):#para cada item encontrado en la busqueda rellena el dict refinado
              #asignación de valores al diccionario creado
            tracks_info['hits']['tracks'][int(i)] = {'cancion_id':get_track['tracks']['items'][int(i)]['id'],'nombre_song':get_track['tracks']['items'][int(i)]['name'],
                                    'img_song':get_track['tracks']['items'][int(i)]['album']['images'][0]['url'],'open_track_link':get_track['tracks']['items'][int(i)]['external_urls']['spotify'],'popularidad':get_track['tracks']['items'][int(i)]['popularity']}
            tracks_info['hits']['tracks'][int(i)]['art'] = get_track['tracks']['items'][int(i)]['artists']
            tracks_info['hits']['tracks'][int(i)]['album'] = get_track['tracks']['items'][int(i)]['album']
            tracks_info['hits']['tracks'][int(i)]['album'].pop('available_markets')
            tracks_info['hits']['tracks'][int(i)]['album'].pop('external_urls')    
        seeds = self.get_seeds(tracks_info) #obtiene las semillas de la busqueda
        for i  in tracks_info['hits']['tracks']:#para cada uno de los datos encontrados en tracks_info
            detail = self.get_artist(tracks_info['hits']['tracks'][cont]['art'][0]['id'])#asignar detalles del artista
            tracks_info['hits']['tracks'][cont]['art_detail'] = detail #ingresar detalles del artista al dict refinado
            cont += 1
        y = tracks_info['hits']['tracks'][0]['art'][0]['id']#toma el primer atistas del dict
        r_tracks = self.related_tracks_search(seeds)#realiza la busqueda de tracks relacionados
        r_artists = self.related_artists_search(y)#realiza la busqueda de artistas relacionados con la id del primer artista(hint mas preciso)
        tracks_info['hits']['related']['artists'] = r_artists['artists'] #asigna valores para related artists en el dict
        tracks_info['hits']['related']['tracks'] = r_tracks['tracks']#asigna valores para related tracks en el dict
        return(tracks_info, seeds) #devuelve el dict refinado y las seeds por si se quieren usar nuevamente

    def get_artist__tracks_full(self, _hint = ' '): #pbtener tracks de un artista
        s = SpotifyAPI(client_id, client_secret)
        get_track = s.search({"artist": _hint}, search_type="track")
        return(get_track)

    
    def get_artists_bi_hint(self,_hint = ' '):
        s = SpotifyAPI(client_id, client_secret)
        get_track = s.search({"artist": _hint}, search_type="artist")#obtener artistas relacionados a un hint
        y = get_track['artists']['items'][0]['id']#toma el primer atistas del dict
        r_artists = self.related_artists_search(y)#realiza la busqueda de artistas relacionados con la id del primer artista(hint mas preciso)
        get_track['related_artists'] = r_artists['artists'] #asigna valores para related artists en el dict
        return(get_track)
    
    