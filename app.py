from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from best_colleges import get_best_colleges_by_course, get_states, get_courses as get_best_courses
from rank_predictor import predict_rank
import course_predictor
from logic_main import generate_main_timetable
from logic_revision import generate_revision_timetable
from models import get_db_connection, TIMETABLE_DB, REV_TIMETABLE_DB
import pdf_generator
from datetime import datetime, date, timedelta


from db_init import (
    init_pyq_weightage_db, 
    init_revision_weightage_db, 
    init_created_timetable_db, 
    init_revision_timetable_db
)

# Initialize databases to ensure tables exist
init_pyq_weightage_db()
init_revision_weightage_db()
init_created_timetable_db()
init_revision_timetable_db()

app = Flask(__name__)

# Disable caching for development
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

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


#                ------   timetable generator page    ------   

@app.route('/timetable')
def timetable_form():
    """Display the timetable generation form"""
    return render_template('timetable_form.html')


@app.route('/generate-timetable', methods=['POST'])
def generate_timetable():
    """Generate timetable using old project logic"""
    # 1. Extract Inputs
    from_date_str = request.form['from_date']
    to_date_str = request.form['to_date']
    revision_days = int(request.form.get('revision_days', 0))
    daily_hours = int(request.form['daily_hours'])
    selected_slots = request.form.getlist('time_slots') 
    
    gt_freq = request.form.get('grant_test_frequency', 'once_weekly')
    method = request.form.get('method', 'subject_completion_wise')
    
    # Simple validation
    if not from_date_str or not to_date_str:
        return "Dates required", 400
        
    start_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
    
    total_days = (end_date - start_date).days + 1
    
    main_timetable_id = None
    rev_timetable_id = None
    
    # 2. Logic Dispatch
    if total_days <= 60:
        # ONLY Revision Timetable
        rev_timetable_id = generate_revision_timetable(start_date, end_date, selected_slots, daily_hours)
    else:
        # Both Main and Revision
        main_days_count = total_days - revision_days
        main_end = start_date + timedelta(days=main_days_count - 1)
        rev_start = main_end + timedelta(days=1)
        rev_end_actual = end_date - timedelta(days=1)
        
        # Generate Main
        main_timetable_id = generate_main_timetable(start_date, main_end, selected_slots, gt_freq, method, revision_days)
        
        # Generate Revision
        rev_timetable_id = generate_revision_timetable(rev_start, rev_end_actual, selected_slots, daily_hours)

    # 3. Retrieve Data for Display
    def process_data_matrix(timetable_id, is_revision=False):
        if not timetable_id:
            return {'days': [], 'summary': {}}
            
        table = 'TimetableSlots'
        id_col = 'timetable_id' if not is_revision else 'rev_timetable_id'
        
        with get_db_connection(TIMETABLE_DB if not is_revision else REV_TIMETABLE_DB) as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table} WHERE {id_col} = ? ORDER BY slot_date, start_time", (timetable_id,))
            rows = cur.fetchall()
            
            # Summary
            counts = {}
            for r in rows:
                s = r['subject']
                if s not in counts: counts[s] = 0
                counts[s] += 1
            
            sorted_summary = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
            
            # Matrix Transformation
            matrix_days = []
            current_date = None
            current_day_obj = None
            
            for r in rows:
                r_dict = dict(r)
                d_str = r_dict['slot_date']
                
                if d_str != current_date:
                    if current_day_obj:
                        matrix_days.append(current_day_obj)
                    
                    dt = datetime.strptime(d_str, '%Y-%m-%d')
                    day_name = dt.strftime('%A')
                    friendly_date = f"{d_str} ({day_name})"
                    
                    current_day_obj = {
                        'date_display': friendly_date,
                        'is_special': False,
                        'special_label': '',
                        'slots_map': {}
                    }
                    current_date = d_str
                
                subj = r_dict['subject']
                time_key = f"{r_dict['start_time']}-{r_dict['end_time']}"
                
                if is_revision:
                    if "Grand Test" in subj:
                        current_day_obj['is_special'] = True
                        current_day_obj['special_label'] = "Grand Test"
                    elif "Weekly Revision" in subj:
                        current_day_obj['is_special'] = True
                        current_day_obj['special_label'] = "Weekly Revision"
                
                current_day_obj['slots_map'][time_key] = subj
                
            if current_day_obj:
                matrix_days.append(current_day_obj)
                
            return {'days': matrix_days, 'summary': sorted_summary}

    main_data = process_data_matrix(main_timetable_id, is_revision=False)
    rev_data = process_data_matrix(rev_timetable_id, is_revision=True)
    
    # Calculate Duration Stats
    stats = {}
    total_d = (end_date - start_date).days + 1
    stats['total_days'] = total_d
    
    if total_days <= 60:
         stats['main_days'] = 0
         stats['rev_days'] = total_d
    else:
         stats['main_days'] = (main_end - start_date).days + 1
         stats['rev_days'] = (rev_end_actual - rev_start).days + 1 

    cols = sorted(selected_slots) 

    return render_template('timetable_result.html', 
                         main=main_data, 
                         rev=rev_data, 
                         stats=stats, 
                         time_cols=cols, 
                         quotes=pdf_generator.MOTIVATIONAL_QUOTES,
                         form_data={
                             'from_date': from_date_str,
                             'to_date': to_date_str,
                             'revision_days': revision_days,
                             'daily_hours': daily_hours,
                             'time_slots': selected_slots,
                             'grant_test_frequency': gt_freq,
                             'method': method
                         })


@app.route('/download-timetable-pdf', methods=['POST'])
def download_timetable_pdf():
    """Generate and download enhanced PDF"""
    try:
        # Get form data (same as generate_timetable)
        from_date_str = request.form['from_date']
        to_date_str = request.form['to_date']
        revision_days = int(request.form.get('revision_days', 0))
        daily_hours = int(request.form['daily_hours'])
        selected_slots = request.form.getlist('time_slots')
        gt_freq = request.form.get('grant_test_frequency', 'once_weekly')
        method = request.form.get('method', 'subject_completion_wise')
        
        start_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        total_days = (end_date - start_date).days + 1
        
        main_timetable_id = None
        rev_timetable_id = None
        
        # Generate timetables (same logic)
        if total_days <= 60:
            rev_timetable_id = generate_revision_timetable(start_date, end_date, selected_slots, daily_hours)
        else:
            main_days_count = total_days - revision_days
            main_end = start_date + timedelta(days=main_days_count - 1)
            rev_start = main_end + timedelta(days=1)
            rev_end_actual = end_date - timedelta(days=1)
            
            main_timetable_id = generate_main_timetable(start_date, main_end, selected_slots, gt_freq, method, revision_days)
            rev_timetable_id = generate_revision_timetable(rev_start, rev_end_actual, selected_slots, daily_hours)
        
        # Process data (same helper function)
        def process_data_matrix(timetable_id, is_revision=False):
            if not timetable_id:
                return {'days': [], 'summary': {}}
                
            table = 'TimetableSlots'
            id_col = 'timetable_id' if not is_revision else 'rev_timetable_id'
            
            with get_db_connection(TIMETABLE_DB if not is_revision else REV_TIMETABLE_DB) as conn:
                cur = conn.cursor()
                cur.execute(f"SELECT * FROM {table} WHERE {id_col} = ? ORDER BY slot_date, start_time", (timetable_id,))
                rows = cur.fetchall()
                
                counts = {}
                for r in rows:
                    s = r['subject']
                    if s not in counts: counts[s] = 0
                    counts[s] += 1
                
                sorted_summary = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
                
                matrix_days = []
                current_date = None
                current_day_obj = None
                
                for r in rows:
                    r_dict = dict(r)
                    d_str = r_dict['slot_date']
                    
                    if d_str != current_date:
                        if current_day_obj:
                            matrix_days.append(current_day_obj)
                        
                        dt = datetime.strptime(d_str, '%Y-%m-%d')
                        day_name = dt.strftime('%A')
                        friendly_date = f"{d_str} ({day_name})"
                        
                        current_day_obj = {
                            'date_display': friendly_date,
                            'is_special': False,
                            'special_label': '',
                            'slots_map': {}
                        }
                        current_date = d_str
                    
                    subj = r_dict['subject']
                    time_key = f"{r_dict['start_time']}-{r_dict['end_time']}"
                    
                    if is_revision:
                        if "Grand Test" in subj:
                            current_day_obj['is_special'] = True
                            current_day_obj['special_label'] = "Grand Test"
                        elif "Weekly Revision" in subj:
                            current_day_obj['is_special'] = True
                            current_day_obj['special_label'] = "Weekly Revision"
                    
                    current_day_obj['slots_map'][time_key] = subj
                    
                if current_day_obj:
                    matrix_days.append(current_day_obj)
                    
                return {'days': matrix_days, 'summary': sorted_summary}
        
        main_data = process_data_matrix(main_timetable_id, is_revision=False)
        rev_data = process_data_matrix(rev_timetable_id, is_revision=True)
        
        stats = {}
        total_d = (end_date - start_date).days + 1
        stats['total_days'] = total_d
        
        if total_days <= 60:
             stats['main_days'] = 0
             stats['rev_days'] = total_d
        else:
             stats['main_days'] = (main_end - start_date).days + 1
             stats['rev_days'] = (rev_end_actual - rev_start).days + 1
        
        cols = sorted(selected_slots)
        
        # Generate enhanced PDF
        pdf_buffer = pdf_generator.generate_pdf(main_data, rev_data, stats, cols)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'NEET_PG_Timetable_{from_date_str}_to_{to_date_str}.pdf'
        )
        
    except Exception as e:
        return f"Error generating PDF: {str(e)}", 500



if __name__ == "__main__":
    app.run()
