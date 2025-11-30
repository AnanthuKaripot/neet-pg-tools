from flask import Flask, render_template, request, jsonify
import sqlite3
from best_colleges import get_best_colleges_by_course, get_states, get_courses

app = Flask(__name__)

def get_connection():
    return sqlite3.connect("medical_allotment.db")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/coursepredict", methods=["GET", "POST"])
def coursepredict():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT course FROM allotted_seats ORDER BY course")
    courses = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT allotted_category FROM allotted_seats ORDER BY allotted_category")
    categories = [r[0] for r in cur.fetchall()]

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
            cur.execute("""
                        SELECT MAX(rank)
                        FROM allotted_seats
                        WHERE course = ? AND allotted_quota = ? AND allotted_category = ?;
                        """, (selected_course, selected_quota, selected_category))
            row = cur.fetchone()
            if row and row[0] is not None:
                last_rank = int(row[0])

        if my_rank_str and selected_category and selected_quota:
            my_rank = int(my_rank_str)
            cur.execute("""
                        SELECT course, allotted_quota, allotted_category, MAX(rank) AS last_rank
                        FROM allotted_seats
                        WHERE allotted_category = ? AND allotted_quota = ?
                        GROUP BY course, allotted_category
                        HAVING last_rank >= ?
                        ORDER BY last_rank;
                        """, (selected_category, selected_quota, my_rank))
            eligible_courses = cur.fetchall()
    conn.close()
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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT allotted_quota
        FROM allotted_seats
        WHERE course = ?
        ORDER BY allotted_quota;
    """, (course,))
    quotas = [row[0] for row in cur.fetchall()]
    conn.close()
    return jsonify({"quotas": quotas})

@app.route("/best-colleges", methods=["GET", "POST"])
def best_colleges():
    courses = get_courses()
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
            table_html = df.to_html(classes="table table-striped table-hover text-center", 
                                   index=False, escape=False, table_id="best-colleges-table")

    return render_template("best_colleges.html",
                           table_html=table_html,
                           error=error,
                           courses=courses,
                           states=states,
                           selected_course=course,
                           selected_state=state_filter,
                           top_n=top_n)

if __name__ == "__main__":
    app.run()
