import requests
import json

n = "noah kahan, watchhouse, Del Water Gap, rainbow kitten surprise, the backseat lovers"

def get_token():
    data = {
        'grant_type': 'client_credentials',
        'client_id': 'f1e80a84357747ad8b165a0d1088824d',
        'client_secret': '9048f5b3256640289d480e3e357a7bd0',
    }
    response = requests.post('https://accounts.spotify.com/api/token', data=data)
    # print(response.text)
    return json.loads(response.text)

headers = {
    'Authorization': 'Bearer  '+get_token()['access_token'],
}
def artist_name_to_id(name: str):
    parsed_name = 'artist'+str(name.replace(' ', '%20'))

    params = {
        'q': parsed_name,
        'type': 'artist',
    }

    response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)

    results = json.loads(response.text)['artists']['items']
    most_pop = {'popularity': 0}
    for artist in results:
        if artist['popularity'] > most_pop['popularity']:
            most_pop = artist
    print(most_pop)
    if most_pop == {'popularity': 0}:
        return 'no results'
    name = most_pop['name']
    id = most_pop['id']
    return [name, id]

def rec_new_five(nas: str):
    ids = []
    names = nas.split(', ')
    # formatted_names = []
    # for nam in names:
    #     na = nam[0].upper() + nam[1:]
    #     formatted_names.append(na)
    spotify_names = []
    for name in names:
        try:
            spot_result = artist_name_to_id(name)
            print(spot_result)
            spotify_names.append(spot_result[0])
            ids.append(spot_result[1])
        except Exception as e:
            print(e)
            return "Could not find anything for artist"
    params = {
        'seed_artists': ids,
    }
    response = requests.get('https://api.spotify.com/v1/recommendations', params=params, headers=headers)
    jsonr = json.loads(response.text)
    if jsonr == {'error': {'message': 'invalid request', 'status': 400}}:
        return 'Could not find any recs for artist'
    topthirty = jsonr['tracks'][0:100]
    uniqueartists = []
    alreadyrecommended = []
    with open('recommended.txt', 'r') as f:
        read = f.read()
    f.close()
    for line in read.split('\n'):
        alreadyrecommended.append(line)
    for item in topthirty:
        #print(item)
        artname = item['artists'][0]['name']
        if artname not in uniqueartists and artname not in spotify_names and artname not in alreadyrecommended:
            uniqueartists.append(item['artists'][0]['name'])
    pretspotnames = ""
    if len(spotify_names) > 1:
        spotify_names[-1] = 'and ' + spotify_names[-1]
    for spot in spotify_names:
        pretspotnames += spot + ', '
    pretspotnames = pretspotnames[:-2]
    pretty = "Your artist deep dive based on "+pretspotnames+":\n"
    count = 1
    for artist in uniqueartists[0:5]:
        pretty += str(count) + ". " + artist + "\n"
        count += 1
    with open('recommended.txt', 'a') as f:
        for artist in uniqueartists[0:5]:
            f.write(artist+'\n')
    f.close()
    "https://open.spotify.com/embed/artist/5uEeqYFuIChoWKy34jp8xE?utm_source=generator"
    print(pretty.strip('\n'))
    return pretty.strip('\n')

# rec_new_five()

from flask import Flask, render_template, request, url_for, flash, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e67876b81dfe567b787e6cb324d6683e8a7cf70e406dfff1'

messages = []

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        # title = request.form['title']
        content = request.form['content']

        if not content:
            flash('At least one artist is required!')
        else:
            messages.append({'content': str(rec_new_five(content))})
            return redirect(url_for('index'))

    return render_template('create.html')
