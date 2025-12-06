from flask import Flask, render_template, request, jsonify
from best_colleges import get_best_colleges_by_course, get_states, get_courses as get_best_courses
from rank_predictor import predict_rank
import course_predictor


app = Flask(__name__)

#           ------   index page    ------   

@app.route("/")
def home():
    return render_template("index.html")

#           ------   course predictor page    ------   

@app.route("/coursepredict", methods=["GET", "POST"])
def coursepredict():
    courses = course_predictor.get_courses()
    categories = course_predictor.get_categories()
    selected_course = None
    selected_quota = None
    selected_category = None
    last_rank = None
    my_rank = None
    eligible_courses = []

    if request.method == "POST":
        selected_course = request.form.get("course")
        selected_quota = request.form.get("quota")
        selected_category = request.form.get("category")
        my_rank_str = request.form.get("my_rank")

        if selected_course and selected_category and selected_quota:
            last_rank = course_predictor.get_last_rank(selected_course, selected_quota, selected_category)

        if my_rank_str and selected_category and selected_quota:
            try:
                my_rank = int(my_rank_str)
            except ValueError:
                my_rank = None
            if my_rank is not None:
                eligible_courses = course_predictor.get_eligible_courses(my_rank, selected_quota, selected_category)

    return render_template("coursepredict.html",
                           courses=courses,
                           categories=categories,
                           selected_course=selected_course,
                           selected_quota=selected_quota,
                           selected_category=selected_category,
                           my_rank=my_rank,
                           last_rank=last_rank,
                           eligible_courses=eligible_courses)


@app.route("/get_quotas", methods=["GET"])
def get_quotas():
    course = request.args.get("course")
    quotas = course_predictor.get_quotas(course) if course else []
    return jsonify({"quotas": quotas})

#               ------   best colleges page   ------ 

@app.route("/best-colleges", methods=["GET", "POST"])
def best_colleges():
    courses = get_best_courses()
    states = get_states()

    if request.method == "POST":
        course = request.form.get("course")
        state_filter = request.form.get("state_filter", '')
        top_n = 1000  # Display full list by default
    else:
        course = request.args.get("course", None)
        state_filter = request.args.get("state_filter", '')
        top_n = 1000

    error = None
    table_html = None

    if not course:
        error = "Please select a course to view colleges."
        course = None

    if course:
        df = get_best_colleges_by_course(course, state_filter=state_filter or None, top_n=top_n)
        if not df.empty:
            # Convert dataframe to list of dicts for Jinja iteration
            colleges_data = df.to_dict(orient='records')
            # If the dataframe column names have spaces, we might need to be careful in jinja or rename them here.
            # Assuming keys are 'Allotted Institute', 'Course', 'Allotted Quota', 'Rank', etc. from previous context.

    return render_template("best_colleges.html",
                           colleges=colleges_data if 'colleges_data' in locals() else [],
                           error=error,
                           courses=courses,
                           states=states,
                           selected_course=course,
                           selected_state=state_filter,
                           top_n=top_n)


#                ------   rank predictor page    ------   

@app.route('/predict-rank', methods=['GET', 'POST'])
def predict_rank_route():
    predicted_rank = None
    if request.method == 'POST':
        try:
            score = float(request.form.get('score', -1))
            # Validate score range
            if not (0 <= score <= 800):
                raise ValueError("Score out of valid range")

            # Convert score to percentage
            percentage = (score / 800) * 100
            predicted_rank = predict_rank(percentage)
        except Exception:
            predicted_rank = "Invalid input. Please enter a valid score from 0 to 800."

    return render_template('predict_rank.html', predicted_rank=predicted_rank)


if __name__ == "__main__":
    app.run()
