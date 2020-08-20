import spotify
import json
import requests
import csv
import pandas as pd
client_id = '5244f03937d2403d95902683a070a162'
client_secret = '784bdf33b03d4afdb6320be398b0fa78'
s = spotify.SpotifyAPI(client_id,client_secret)
get_track = s.search({"artist": 'gojira'}, search_type="artist")#obtener artistas relacionados a un hint
y = get_track['artists']['items'][0]['id']#toma el primer atistas del dict
r_artists = s.related_artists_search(y)#realiza la busqueda de artistas relacionados con la id del primer artista(hint mas preciso)
get_track['related_artists'] = r_artists['artists'] #asigna valores para related artists en el dict
g= (json.dumps(get_track))
print(g)
#print(json.dumps(tracks_info))
#print(type(tracks_info[0]))
#url = 'https://p.scdn.co/mp3-preview/af237206f611b722f48620ece049aff3b8650e77?cid=5244f03937d2403d95902683a070a162'
#r = requests.get(url, allow_redirects=True)
#open('static/music-files/idtrack_preview.mp3', 'wb').write(r.content)
'''reader = csv.DictReader(open('kornbyte/top_tracks_csv/top.csv','rb',encoding="UTF-8"))
dict_ = {'hits':{}}
cont = 1
for line in reader:
    dict_ = {cont:line}
print(reader)'''
'''df = pd.read_csv("kornbyte/top_tracks_csv/top.csv")
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
    cont +=1'''
    #if get_info:
        #print ('se encontró la info y se guardo en get_info')    
#top_artists_aditionnal_info = r
#print((tracks_info))
'''dict_ = {'weaita':'weaitawena'}
r[0]['nuevo'] ={'diccionario_nuevo':dict_} 
print(r[0]['nuevo']['diccionario_nuevo']['weaita'])
for i in dfnew:
    lista.appen#d'''