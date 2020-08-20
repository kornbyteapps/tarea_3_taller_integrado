from django.http import HttpResponse
from django.shortcuts import render
import spotify
import pandas as pd 
import json

def index(request):
    client_id = '5244f03937d2403d95902683a070a162'
    client_secret = '784bdf33b03d4afdb6320be398b0fa78'
    s = spotify.SpotifyAPI(client_id,client_secret)
    df = pd.read_csv("kornbyte/top_tracks_csv/top.csv")
    dfnew = df.rename(columns={'Unnamed: 0': 'top','Unnamed: 1': 'track','Unnamed: 2':'artist','Note that these figures are generated using a formula that protects against any artificial inflation of chart positions.':'streams','Unnamed: 4':'open_url'})
    dfnew = dfnew.drop(0)
    df_five = dfnew.iloc[:10]
    df_five = df_five.to_json(orient = 'records')
    r = json.loads(df_five)
    get_info = {}
    cont = 0
    for i in r:
        hint_ = r[cont]['artist']
        get_info = s.get_artists_bi_hint(hint_)
        r[cont]['detail_info'] = get_info['artists']['items'][0]
        cont +=1    
    top_artists_details = r

    # agregar al search_full los links a mp3.spotify
    #función para descargar la musica
    #ocupar get   
    return render(request,'index.html',{'top_tracks_week':r, 'top_artists_details':top_artists_details})


def prueba_json(request):
    client_id = '5244f03937d2403d95902683a070a162'
    client_secret = '784bdf33b03d4afdb6320be398b0fa78'
    s = spotify.SpotifyAPI(client_id,client_secret)
    df = pd.read_csv("kornbyte/top_tracks_csv/top.csv")
    dfnew = df.rename(columns={'Unnamed: 0': 'top','Unnamed: 1': 'track','Unnamed: 2':'artist','Note that these figures are generated using a formula that protects against any artificial inflation of chart positions.':'streams','Unnamed: 4':'open_url'})
    dfnew = dfnew.drop(0)
    df_five = dfnew.iloc[:10]
    df_five = df_five.to_json(orient = 'records')
    r = json.loads(df_five)
    get_info = {}
    cont = 0
    for i in r:
        hint_ = r[cont]['artist']
        get_info = s.get_artists_bi_hint(hint_)
        r[cont]['detail_info'] = get_info['artists']['items'][0]
        cont +=1    
    top_artists_details = r

    # agregar al search_full los links a mp3.spotify
    #función para descargar la musica
    #ocupar get   
    return HttpResponse(top_artists_details)

def test(request):
        return render(request,'prueba.html',{})

def search(request):
    query = request.GET['query']
    query = query.replace("+",' ')
    client_id = '5244f03937d2403d95902683a070a162'
    client_secret = '784bdf33b03d4afdb6320be398b0fa78'
    s = spotify.SpotifyAPI(client_id,client_secret)
    track_info,seeds = s.get_songs_full(query)
    return render(request,'blog.html',{'tracks_info':track_info})

def search_art(request):
    query_art = request.GET['query_art']
    query_art = query_art.replace("+",' ')
    client_id = '5244f03937d2403d95902683a070a162'
    client_secret = '784bdf33b03d4afdb6320be398b0fa78'
    s = spotify.SpotifyAPI(client_id,client_secret)
    get_artist = s.search({"artist": query_art}, search_type="artist")#obtener artistas relacionados a un hint
    y = get_artist['artists']['items'][0]['id']#toma el primer atistas del dict
    r_artists = s.related_artists_search(y)#realiza la busqueda de artistas relacionados con la id del primer artista(hint mas preciso)
    get_artist['related_artists'] = r_artists['artists'] #asigna valores para related artists en el dict    
    return render(request,'blog2.html',{'artist_info':get_artist})

def acerca(request):
    return render(request,'acerca.html',{})

def tabla(request):
    client_id = '5244f03937d2403d95902683a070a162'
    client_secret = '784bdf33b03d4afdb6320be398b0fa78'
    s = spotify.SpotifyAPI(client_id,client_secret)
    df = pd.read_csv("kornbyte/top_tracks_csv/top.csv")
    dfnew = df.rename(columns={'Unnamed: 0': 'top','Unnamed: 1': 'track','Unnamed: 2':'artist','Note that these figures are generated using a formula that protects against any artificial inflation of chart positions.':'streams','Unnamed: 4':'open_url'})
    dfnew = dfnew.drop(0)
    df_five = dfnew.iloc[:50]
    df_five = df_five.to_json(orient = 'records')
    r = json.loads(df_five)
    get_info = {}
    cont = 0
    for i in r:
        hint_ = r[cont]['artist']
        get_info = s.get_artists_bi_hint(hint_)
        r[cont]['detail_info'] = get_info['artists']['items'][0]
        cont +=1    
    top_artists_details = r
    return render(request,'tables.html',{'top_tracks':r})
