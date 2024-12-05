from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from forms import RegisterForm, LoginForm, AddExerciseToPlanForm, CreateWorkoutPlanForm, EditExerciseForm, UpdateHealthMetricsForm
from models import db, User, Exercise, WorkoutPlan, WorkoutPlanExercises, HealthMetrics, WeightHistory
from datetime import datetime


bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness_app.db'
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    migrate = Migrate(app, db)

    
    @login_manager.user_loader
    def load_user(user_id):
        '''user loader function for login'''
        return User.query.get(int(user_id))


    @app.route('/')
    @login_required
    def home():
        return render_template('home.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        ''' Function to register a new a user'''
        form = RegisterForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Your account has been created!', 'success')
            login_user(new_user)
            return redirect(url_for('home'))
        else:
            if form.errors:
                flash('Registration unsuccessful. Please correct the errors and try again.', 'danger')
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        ''' Function to log-in a user'''
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('You have been logged in!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Login unsuccessful. Check username and/or password.', 'danger')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        ''' Function to logout a user'''
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))

    @app.route('/exercises')
    @login_required
    def view_exercises():
        ''' Function to view all exercises in the library'''
        exercises = Exercise.query.all()
        return render_template('exercise_library.html', exercises=exercises)

    @app.route("/workout_plan/create", methods=["GET", "POST"])
    @login_required
    def create_workout_plan():
        ''' Function to create a new plan'''
        form = CreateWorkoutPlanForm()
        if form.validate_on_submit():
            new_plan = WorkoutPlan(name=form.name.data, description=form.description.data, group_label=form.group_label.data, user_id=current_user.id)
            db.session.add(new_plan)
            db.session.commit()
            flash('Workout Plan created successfully!', 'success')
            return redirect(url_for('view_workout_plans'))
        return render_template('create_workout_plan.html', form=form)

    @app.route('/workout_plans')
    @login_required
    def view_workout_plans():
        ''' Function to view all plans'''
        workout_plans = WorkoutPlan.query.filter(
        (WorkoutPlan.user_id == current_user.id) | (WorkoutPlan.is_default == True)).all()
        return render_template('workout_plans.html', workout_plans=workout_plans)

    @app.route('/workout_plan/<int:id>')
    def view_workout_plan(id):
        ''' Function to view a particular plan'''
        workout_plan = WorkoutPlan.query.get(id)
        return render_template('view_workout_plan.html', workout_plan=workout_plan)



    @app.route('/workout_plan/<int:workout_plan_id>/add_exercise_to_plan', methods=["GET", "POST"])
    @login_required
    def add_exercise_to_plan(workout_plan_id):
        workout_plan = WorkoutPlan.query.get_or_404(workout_plan_id)
        ''' Function to add an exercise to the plan'''
        if workout_plan.is_default:
            flash('This Workout plan cannot be edited', 'danger')
            return redirect(url_for('view_workout_plans'))
    
        form = AddExerciseToPlanForm()
        form.exercise.choices = [(exercise.id, exercise.name) for exercise in Exercise.query.all()]

        if form.validate_on_submit():
            exercise = Exercise.query.get(form.exercise.data)
            workout_plan_exercise = WorkoutPlanExercises(
                workout_plan_id=workout_plan.id,
                exercise_id=exercise.id,
                sets=form.sets.data,
                reps=form.reps.data
            )
            db.session.add(workout_plan_exercise)
            db.session.commit()
            flash('Exercise added to your workout plan!', 'success')
            return redirect(url_for('view_workout_plan', id=workout_plan.id))

        return render_template('add_exercise_to_plan.html', form=form, workout_plan=workout_plan)


    @app.route('/workout_plan/<int:id>/edit_exercise/<int:entry_id>', methods=['GET', 'POST'])
    @login_required
    def edit_exercise(id, entry_id):
        ''' Function to edit an exercise in the plan'''
        workout_plan = WorkoutPlan.query.get(id)
        exercise_entry = WorkoutPlanExercises.query.get(entry_id)
        form = EditExerciseForm()

        if form.validate_on_submit():
            exercise_entry.sets = form.sets.data
            exercise_entry.reps = form.reps.data
            db.session.commit()
            return redirect(url_for('view_workout_plan', id=id))

        form.sets.data = exercise_entry.sets
        form.reps.data = exercise_entry.reps
        return render_template('edit_exercise.html', form=form, workout_plan=workout_plan, entry=exercise_entry)

    @app.route('/workout_plan/<int:workout_plan_id>/delete_exercise/<int:entry_id>', methods=['GET', 'POST'])
    @login_required
    def delete_exercise(workout_plan_id, entry_id):
        ''' Function to delete an exercise from the workout plan'''
        exercise_entry = WorkoutPlanExercises.query.get_or_404(entry_id)
        db.session.delete(exercise_entry)
        db.session.commit()
        flash('Exercise removed from the workout plan successfully!', 'success')
        return redirect(url_for("view_workout_plan", id=workout_plan_id))

    @app.route('/workout_plan/<int:plan_id>/delete', methods=['POST'])
    @login_required
    def delete_workout_plan(plan_id):
        ''' Function to delete workout plan, default plans cannot be deleted'''
        workout_plan = WorkoutPlan.query.get_or_404(plan_id)
        if workout_plan.is_default:
            flash('This Workout plan cannot be deleted', 'danger')
            return redirect(url_for('view_workout_plans'))
        
        db.session.delete(workout_plan)
        db.session.commit()
        flash('Workout plan deleted successfully!', 'success')
        return redirect(url_for('view_workout_plans'))



    @app.route('/health_metrics', methods=['GET', 'POST'])
    @login_required
    def health_metrics():
        ''' Function to track weight and weight goal of the user'''
        metrics = HealthMetrics.query.filter_by(user_id=current_user.id).first()
        form = UpdateHealthMetricsForm()

        if form.validate_on_submit():
            if not metrics:
                metrics = HealthMetrics(user_id=current_user.id)
                db.session.add(metrics)

            metrics.height = form.height.data
            metrics.current_weight = form.current_weight.data
            metrics.weight_goal = form.weight_goal.data
            db.session.commit()

            new_weight_entry = WeightHistory(
                health_metrics_id=metrics.id,
                date=form.weight_date.data,
                weight=form.current_weight.data
            )
            db.session.add(new_weight_entry)
            db.session.commit()

            flash('Health metrics updated!', 'success')
            return redirect(url_for('health_metrics'))

        if metrics:
            form.height.data = metrics.height
            form.current_weight.data = metrics.current_weight
            form.weight_goal.data = metrics.weight_goal

        weight_trend = metrics.weight_history if metrics else []
        weight_trend_info = []
        for entry in weight_trend:
            difference = metrics.weight_goal - entry.weight
            if difference > 0:
                trend_message = f": You're {difference} kg under your weight goal."
            elif difference < 0:
                trend_message = f": You're {abs(difference)} kg over your weight goal."
            else:
                trend_message = ": You've reached your weight goal!"

            weight_trend_info.append({
                "entry": entry,
                "message": trend_message
            })

        return render_template('health_metrics.html', form=form, weight_trend_info=weight_trend_info)


    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
