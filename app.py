from flask import Flask, request, render_template, redirect, url_for
import requests, json, os, random

app = Flask(__name__)

url = "https://language.googleapis.com/v1beta2/documents:analyzeSentiment"
access_url = "https://accounts.spotify.com/api/token"
key = "?key=" + str(os.environ["CLOUD_KEY"])

@app.route('/')
def search():
    return render_template('index.html')

@app.route('/', methods = ['POST', 'GET'])
def get_recommendations():

    if request.form.get('action1') == 'LOGO':
        return redirect(url_for("search"))

    seed_genres = 'pop'
    seed_artists = 'null'
    seed_tracks = 'null'

    q = request.form['text-content']
    headers = {'Content-Type':'application/json; charset=utf-8'}
    pload = {
        'document': {
            'type':'PLAIN_TEXT',
            'content':q},
        'encodingType':'UTF8'
        }
    with app.test_request_context():
        r = requests.post(url + key, headers = headers, data = json.dumps(pload))
        rd = r.json()

    score = rd['documentSentiment']['score']
    magnitude = rd['documentSentiment']['magnitude']

    sentences = json.loads(r.text)
    content = ""
    for item in sentences['sentences']:
        content = item['text']['content']
        magnitude += (0.1 * content.count('!'))

    bgimage = ""
    a = 0.5
    b = -0.5

    if score > a and magnitude > 1.0: #very positive (Happy - Pharrell William)
        seed_tracks = '60nZcImufyMA1MKQY3dcCH'
        seed_artists = '6veTV9sF06FBf2KN0xAdvo'
        bgimage = "https://static.vecteezy.com/system/resources/thumbnails/001/820/803/small/dark-green-yellow-gradient-blur-drawing-vector.jpg"
    elif score < b and magnitude > 1.0: #very negative (Dancing With Your Ghost - Sasha Sloan)
        seed_tracks = '1TQXIltqoZ5XXyfCbAeSQQ'
        seed_artists = '4xnihxcoXWK3UqryOSnbw5'
        bgimage = "https://i0.wp.com/twinpixelvideo.com/wp-content/uploads/2015/04/gradient-wallpapers-desktop-gradient-grey-wallpaper-generator-iphone-5-android-maker-wallpapers-hd-ios-7-deviantart-ipad.jpg?fit=1920%2C1200&ssl=1"
    elif magnitude == 0.0: #neutral/chill (Coffee - Quinn XCII)
        seed_tracks = '4CxmynXhw78QefruycvxG8'
        seed_artists = '3ApUX1o6oSz321MMECyIYd'
        bgimage = "https://balochistan.gov.pk/wp-content/uploads/2019/05/beautiful-color-ui-gradients-backgrounds-endless-river-1.png"
    elif score < 0.0: #slightly negative (Born To Die - Lana Del Rey)
        seed_tracks = '487OPlneJNni3NWC8SYqhW'
        seed_artists = '00FQb4jTyendYWaN8pK0wa'
        bgimage = "https://i.stack.imgur.com/7vMmx.jpg"
    else: #slightly positive (Free Love - HONNE)
        seed_tracks = '0GPJSHYaXh8rZSSJoUMgyl'
        seed_artists = '0Vw76uk7P8yVtTClWyOhac'
        bgimage = "https://wallpaperaccess.com/full/340597.jpg"

    CLIENT_ID = str(os.environ["CLIENT_ID"])
    CLIENT_SECRET = str(os.environ["CLIENT_SECRET"])

    AUTH_URL = 'https://accounts.spotify.com/api/token'

    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })

    auth_response_data = auth_response.json()

    access_token = auth_response_data['access_token']

    headers = {
    'Authorization': 'Bearer {token}'.format(token = access_token)
    }

    BASE_URL = 'https://api.spotify.com/v1/'

    audio_req = requests.get(BASE_URL + 'audio-features/' + seed_tracks, headers = headers)
    audio_json = audio_req.json()

    r_danceability = random.uniform(audio_json["danceability"]-0.1, audio_json["danceability"]+0.1)
    r_instrumentalness = random.uniform(audio_json["instrumentalness"]-0.1, audio_json["instrumentalness"]+0.1)
    r_liveness = random.uniform(audio_json["liveness"]-0.1, audio_json["liveness"]+0.1)
    r_speechiness = random.uniform(audio_json["speechiness"]-0.1, audio_json["speechiness"]+0.1)
    r_valence = random.uniform(audio_json["valence"]-0.1, audio_json["valence"]+0.1)
 
    if r_danceability > 1:
        r_danceability = 1
    elif r_danceability < 0:
        r_danceability = 0
 
    if r_instrumentalness > 1:
        r_instrumentalness = 1
    elif r_instrumentalness < 0:
        r_instrumentalness = 0
 
    if r_liveness > 1:
        r_liveness = 1
    elif r_liveness < 0:
        r_liveness = 0
 
    if r_speechiness > 1:
        r_speechiness = 1
    elif r_speechiness < 0:
        r_speechiness = 0
 
    if r_valence > 1:
        r_valence = 1
    elif r_valence < 0:
        r_valence = 0


    recommendation_endpoint = 'recommendations?' + 'seed_artists='+ seed_artists + '&seed_genres=' + seed_genres + '&seed_tracks=' + seed_tracks
    added_features = '&limit=10&danceability=' + str(r_danceability) + '&valence=' + str(r_valence) + '&instrumentalness=' +str(r_instrumentalness) + '&liveness=' + str(r_liveness) + '&speechiness=' + str(r_speechiness)
    
    recommendation_req = requests.get(BASE_URL + recommendation_endpoint + added_features, headers = headers)
    recommendation_json = json.loads(recommendation_req.text)
    recommend_items = recommendation_json['tracks']
    recommend_album = recommend_items[0]['album']

    name_artist = dict() #store the name with artist in each item
    info = []
    image = ""
    for item in recommend_items:
        artists = [] #creates new list for each song
        info.append(item['external_urls']['spotify'])
        for artist in item['artists']: #adds all the artists
            artists.append(artist['name'])
        name_artist[item['name']] = artists #adds artists to each song name (name is key)
    
    image = recommend_album['images'][0]['url']

    print(image)

    base = "https://open.spotify.com/embed/track/"

    for i in range(10):
        info[i] = base + info[i][len("https://open.spotify.com/track/"):]


    return render_template('results.html', spotify_link=info, album_image=image, bgimage = bgimage)

