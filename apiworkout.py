from flask import jsonify, request
from models import db, Exercise, Video
import constants
import requests

def get_exercises():
    """List of all exercises."""
    muscle = request.args.get('muscle')
    if muscle and len(muscle) > 3:
        #exercises = [exercise.serialize() for exercise in Exercise.query.filter(Exercise.muscle == muscle).all()]
        musclelike = f"%{muscle}%"
        exercises = [exercise.serialize() for exercise in Exercise.query.filter(Exercise.muscle.ilike(musclelike)).all()]
        return jsonify(exercises=exercises)
    exercises = [exercise.serialize() for exercise in Exercise.query.all()]
    #return jsonify(exercises=exercises)
    return jsonify(exercises=[])

def get_videos():
    """List of all videos."""
    name = request.args.get('name')
    if name:
        videos = [video.serialize() for video in Video.query.filter(Video.exercise_name == name).all()]
        return jsonify(videos=videos)
    videos = [video.serialize() for video in Video.query.all()]
    return jsonify(videos=videos)