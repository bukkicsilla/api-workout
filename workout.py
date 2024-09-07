from flask import jsonify
from models import db, Exercise, Video
#from sqlalchemy.exc import IntegrityError
import constants
import requests
limit = 25
order = "relevance"

def remove_duplicate_by_name(exercise_list):
    # Create an empty list to store unique exercises
    unique_exercises = []
    # Create a set to keep track of the names we've already seen
    seen_names = set()

    for exercise in exercise_list:
        name = exercise['name']
        if name not in seen_names:
            unique_exercises.append(exercise)
            seen_names.add(name)

    return unique_exercises

def get_res_few_times(searchterm):
    res = requests.get(f"{constants.BASE_URL_YT}{searchterm}&maxResults={limit}&order={order}&key={constants.API_KEY_YT1}", headers={'Content-Type': 'application/json'}).json()
    if "items" not in res:
        print("First YT Quota exceeded")
        res = requests.get(f"{constants.BASE_URL_YT}{searchterm}&maxResults={limit}&order={order}&key={constants.API_KEY_YT2}", headers={'Content-Type': 'application/json'}).json()
        if "items" not in res:
            print("Second YT Quota exceeded")
            res = requests.get(f"{constants.BASE_URL_YT}{searchterm}&maxResults={limit}&order={order}&key={constants.API_KEY_YT3}", headers={'Content-Type': 'application/json'}).json()
            if "items" not in res:
                print("Third YT Quota exceeded")
                #return jsonify({"error": "Quota exceeded"})
                return False
    return res

def remove_videos(exercise_name):
    videos =  Video.query.filter(Video.exercise_name == exercise_name).all()
    if videos:
        for video in videos:
            video.query.delete()
            db.session.commit()

def show_exercises():
    """List of all exercises."""
    exercises = [exercise.serialize() for exercise in Exercise.query.all()]
    return jsonify(exercises=exercises)

def show_videos():
    """List of all videos."""
    videos = [video.serialize() for video in Video.query.all()]
    print("all videos", len(videos))
    return jsonify(videos=videos)

def show_exercise(name):
    """Show a single exercise with videos."""
    exercise = Exercise.query.get_or_404(name)
    videos = [video.serialize() for video in exercise.videos]
    if len(videos) > 0 and len(videos) < 10:
    #if len(videos) == 0:
        print("exercise name", exercise.name)
        print("number of videos", len(videos))
        print("*********************************")
    return jsonify(exercise=exercise.serialize(), videos=videos)

def number_of_videos():
    """Only for testing purposes during development."""
    exercises = Exercise.query.all()
    for exercise in exercises:
        show_exercise(exercise.name)
    return jsonify({"message":"Cool"})

def show_video(videoid, exercise_name):
    """Show a single video."""
    #video = Video.query.get_or_404(videoid, exercise_name)
    video = Video.query.filter_by(videoid=videoid, exercise_name=exercise_name).first_or_404()
    return jsonify(video=video.serialize())

def create_exercises():
    """Create exercises with Ninja API and save in the database."""
    muscles = ['abdominals', 'abductors', 'adductors', 'biceps', 'calves', 'chest', 'forearms', 'glutes', 'hamstrings', 'lats', 'lower_back', 'middle_back', 'neck', 'quadriceps', 'traps', 'triceps']
    for i in range(len(muscles)):
        res = requests.get(f"{constants.BASE_URL_EXERCISE}{muscles[i]}", headers={'X-Api-Key': constants.API_KEY_NINJAS}).json()
        res_no_dup = remove_duplicate_by_name(res)
        #print(len(res_no_dup))
        for j in range(len(res_no_dup)):
            new_exercise = Exercise(name=res_no_dup[j]['name'], 
                                    exercise_type=res_no_dup[j]['type'], 
                                    muscle=res_no_dup[j]['muscle'], 
                                    equipment=res_no_dup[j]['equipment'], 
                                    difficulty=res_no_dup[j]['difficulty'],
                                    instructions=res_no_dup[j]['instructions'])
            db.session.add(new_exercise)
            db.session.commit()
        
    return (jsonify({"message":"creation of exercises done"}), 201)

def create_videos():
    """Create videos with YouTube API and save in the database."""
    exercises = Exercise.query.filter(Exercise.muscle == 'chest').all()
    for exercise in exercises:
        #remove_videos(exercise.name)
        searchterm = exercise.name + " exercise"
        res =  get_res_few_times(searchterm)
        if not res:
            return jsonify({"error": "Quota exceeded"}) 
        results = []
        for i in range(len(res['items'])):
            videoId = res['items'][i]['id'].get("videoId", "")
            result = {'exercise_name': exercise.name,  'videoid': videoId,  'title': res['items'][i]['snippet']['title'] } 
            results.append(result)
        for result in results:
            if result['videoid']:
                new_video = Video(exercise_name=result['exercise_name'], videoid=result['videoid'], title=result['title'])
                #video = Video.query.filter(Video.videoid == new_video.videoid).first()
                video = Video.query.filter(Video.videoid ==  new_video.videoid and Video.exercise.name == exercise.name).first()
                if video:
                    print("video exists", video.videoid)
                else:
                    db.session.add(new_video)
                    db.session.commit()
    return (jsonify({"message":"creation of videos done"}), 201)

def change_video_rating(id):
    """Change the rating of the video. Between 1 and 10"""
    return jsonify({"message": "rating changed"})

def delete_exercise(name):
    """Delete a single exercise."""
    exercise_to_delete = Exercise.query.get_or_404(name)
    db.session.delete(exercise_to_delete)
    db.session.commit()
    return jsonify({"message":"deleted exercise"})

def delete_video(videoid, exercise_name):
    """Delete a single video."""
    #video_to_delete = Video.query.get_or_404(id)
    video_to_delete = Video.query.filter_by(videoid=videoid, exercise_name=exercise_name).first_or_404()
    db.session.delete(video_to_delete)
    db.session.commit()
    return jsonify({"message":"deleted video"})