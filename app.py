from flask import Flask, render_template, jsonify, request
from models import connect_db
import workout
import apiworkout
import requests
import constants

app = Flask(__name__)

#for building the first database
app.add_url_rule('/api/exercises', view_func=workout.show_exercises)
app.add_url_rule('/api/videos', view_func=workout.show_videos)
app.add_url_rule('/api/exercises/videos', view_func=workout.number_of_videos)
app.add_url_rule('/api/exercises/<name>', view_func=workout.show_exercise)
app.add_url_rule('/api/videos/<videoid>/<exercise_name>', view_func=workout.show_video)
#app.add_url_rule('/api/exercises', methods=['POST'], view_func=workout.create_exercises)
#app.add_url_rule('/api/videos', methods=['POST'], view_func=workout.create_videos)
#app.add_url_rule('/api/exercises/<name>', methods=['DELETE'], view_func=workout.delete_exercise)
#app.add_url_rule('/api/videos/<videoid>/<exercise_name>', methods=['DELETE'], view_func=workout.delete_video)
#app.add_url_rule('/api/videos/<int:id>', methods=['PATCH'], view_func=workout.change_video_rating)

#API endpoints
app.add_url_rule('/api/workout/exercises', methods=['GET'], view_func=apiworkout.get_exercises)
app.add_url_rule('/api/workout/videos', methods=['GET'], view_func=apiworkout.get_videos)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///workout"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 10
app.config["SECRET_KEY"] = "Capstone projects are challenging."

connect_db(app)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/youtube/<searchterm>')
def show_youtube(searchterm):
    limit = 2
    order = "relevance"
    searchterm += " exercise"
    res = requests.get(f"{constants.BASE_URL_YT}{searchterm}&maxResults={limit}&order={order}&key={constants.API_KEY_YT1}", headers={'Content-Type': 'application/json'}).json()
    if "items" not in res:
        print("First YT Quota exceeded")
        res = requests.get(f"{constants.BASE_URL_YT}{searchterm}&maxResults={limit}&order={order}&key={constants.API_KEY_YT2}", headers={'Content-Type': 'application/json'}).json()
        if "items" not in res:
            print("Second YT Quota exceeded")
            res = requests.get(f"{constants.BASE_URL_YT}{searchterm}&maxResults={limit}&order={order}&key={constants.API_KEY_YT3}", headers={'Content-Type': 'application/json'}).json()
            if "items" not in res:
                print("Third YT Quota exceeded")
                return jsonify({"error": "Quota exceeded"}) 

    video_ids = [res["items"][i]["id"]["videoId"] for i in range(len(res["items"]))]
    return render_template('youtube.html', video_ids=video_ids)


@app.route('/exercisestart')
def exercise():
    muscle = 'abdominals'
    offset = 0
    res = requests.get(f"{constants.BASE_URL_EXERCISE}{muscle}&offset={offset}", headers={'X-Api-Key': constants.API_KEY_NINJAS}).json()
    names = [res[i]['name'] for i in range(len(res))]
    return render_template('exercise.html', names=names, muscle=muscle)

#try without POST
@app.route('/exercise', methods=['GET', 'POST'])
def exercise_offset():
    muscle = request.form['muscle']
    if not muscle:
        print("no muscle group")
        muscle = 'traps'
    res = requests.get(f"{constants.BASE_URL_EXERCISE}{muscle}", headers={'X-Api-Key': constants.API_KEY_NINJAS}).json()
    names = []
    for i in range(len(res)):
        if "/" in res[i]['name']:
            names.append(res[i]['name'].replace("/", " "))
        else:        
            names.append(res[i]['name'])
    return render_template('exercise.html', names=names, muscle=muscle)