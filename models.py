from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)

class Exercise(db.Model):
    __tablename__ = "exercises"

    name = db.Column(db.String(50), primary_key=True, nullable=False,  unique=True)
    exercise_type = db.Column(db.Text, nullable=True)
    muscle = db.Column(db.String(20), nullable=False, default="abdominals")
    equipment = db.Column(db.Text, nullable=False, default="body_only")
    difficulty = db.Column(db.Text, nullable=False, default="beginner")
    instructions = db.Column(db.Text, nullable=True)

    videos = db.relationship("Video", backref="exercise", cascade="all,delete")

    def serialize(self):
        """Returns a dict representation of exercise which we can turn into JSON"""
        return {
            'name': self.name,
            'exercise_type': self.exercise_type,
            'muscle': self.muscle,
            'equipment': self.equipment,
            'difficulty': self.difficulty,
            'instructions': self.instructions
        }
    
    def __repr__(self):
        return f"<Exercise name={self.name} exercise_type={self.exercise_type} muscle={self.muscle} equipment={self.equipment} difficulty={self.difficulty}>"


class Video(db.Model):
    __tablename__ = "videos"

    #id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    videoid = db.Column(db.String(20), nullable=False, default="onLTHQ1KE50", primary_key=True)
    title = db.Column(db.Text, nullable=False, default="YouTube video")
    rating = db.Column(db.Float, nullable=False, default=5.0)
    exercise_name = db.Column(db.Text, db.ForeignKey('exercises.name'), nullable=False, primary_key=True)
    
    '''user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )'''

    def serialize(self):
        """Returns a dict representation of video which we can turn into JSON"""
        return {
            'videoid': self.videoid,
            'title': self.title,
            'rating': self.rating,
            'exercise_name': self.exercise_name
        }

    def __repr__(self):
        return f"<Video videoid={self.videoid} title={self.title} rating={self.rating} exercise_name={self.exercise_name}>"
