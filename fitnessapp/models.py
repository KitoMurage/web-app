from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    workout_plans = db.relationship('WorkoutPlan', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    exercise_entries = db.relationship('WorkoutPlanExercises', back_populates='exercise')

    def __repr__(self):
        return f'<Exercise {self.name}>'

class WorkoutPlan(db.Model):
    __tablename__ = 'workout_plans'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_default = db.Column(db.Boolean, default=False) 
    group_label = db.Column(db.String(50), nullable=True)

    

    workout_plan_exercises = db.relationship('WorkoutPlanExercises', back_populates='workout_plan', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<WorkoutPlan {self.name} - Group: {self.group_label}>'


class WorkoutPlanExercises(db.Model):
    __tablename__ = 'workout_plan_exercises'

    id = db.Column(db.Integer, primary_key=True)
    workout_plan_id = db.Column(db.Integer, db.ForeignKey('workout_plans.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)

    workout_plan = db.relationship('WorkoutPlan', back_populates='workout_plan_exercises')
    exercise = db.relationship('Exercise', back_populates='exercise_entries')

    def __repr__(self):
        return f'<WorkoutPlanExercise {self.exercise.name} - {self.sets} sets x {self.reps} reps>'
    
class HealthMetrics(db.Model):
    __tablename__ = 'health_metrics'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    height = db.Column(db.Float)  
    current_weight = db.Column(db.Float, nullable=False)  
    weight_goal = db.Column(db.Float, nullable=True)  
    weight_history = db.relationship('WeightHistory', backref='health_metrics', lazy=True)

    user = db.relationship('User', backref='health_metrics')

class WeightHistory(db.Model):
    __tablename__ = 'weight_history'

    id = db.Column(db.Integer, primary_key=True)
    health_metrics_id = db.Column(db.Integer, db.ForeignKey('health_metrics.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)  
    weight = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<WeightHistory date={self.date} weight={self.weight}>"
