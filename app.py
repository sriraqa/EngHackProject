from flask import Flask, request, render_template
import requests, json, os

app = Flask(__name__)

url = "https://language.googleapis.com/v1beta2/documents:analyzeSentiment"
access_url = "https://accounts.spotify.com/api/token"
key = "?key=" + str(os.environ["CLOUD_KEY"])

@app.route('/')
def search():
    return render_template('form.html')

@app.route('/', methods = ['POST', 'GET'])
def get_recommendations():
    seed_genres = 'pop/'
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
        #return str(rd['documentSentiment']['score'])
    a = 0.5
    b = -0.5

    if rd['documentSentiment']['score'] > a:
        seed_tracks = '60nZcImufyMA1MKQY3dcCH'
        seed_artists = '6veTV9sF06FBf2KN0xAdvo'
    elif rd['documentSentiment']['score'] > b:
        seed_tracks = '4CxmynXhw78QefruycvxG8'
        seed_artists = '3ApUX1o6oSz321MMECyIYd'
    else:
        seed_tracks = '1TQXIltqoZ5XXyfCbAeSQQ'
        seed_artists = '4xnihxcoXWK3UqryOSnbw5'

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

    # recommendation_endpoint = 'recommendations/' #+ seed_artists +'&' + seed_genres + '&' + seed_tracks
    # recommendation_req = requests.get(BASE_URL + recommendation_endpoint, headers = headers)
    # recommendation_json = recommendation_req.json()

    return audio_json

@app.route('/homepage')
def home():
    return render_template('index.html')
