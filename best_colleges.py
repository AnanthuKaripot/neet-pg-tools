import sqlite3
import pandas as pd

DB_PATH = "medical_allotment.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_states():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT state
        FROM college_ranker
        WHERE state IS NOT NULL
        ORDER BY state
    """)
    states = [row[0] for row in cur.fetchall()]
    conn.close()
    return states

def get_courses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT course
        FROM college_ranker
        ORDER BY course
    """)
    courses = [row[0] for row in cur.fetchall()]
    conn.close()
    return courses

def get_best_colleges_by_course(course, state_filter=None, top_n=1000):
    """
    Gets the best colleges filtered by course and optionally state,
    ranked by average rank stored in college_ranker.
    """
    conn = get_connection()

    query = """
    SELECT
        college_name,
        course,
        address,
        state,
        avg_rank
    FROM college_ranker
    WHERE course = ?
      AND avg_rank IS NOT NULL
    """
    params = [course]

    if state_filter:
        query += " AND state = ?"
        params.append(state_filter)

    # Display full list by default, limit by very high number top_n (default 1000)
    query += " ORDER BY avg_rank ASC LIMIT ?"
    params.append(top_n)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if df.empty:
        return df

    conn = get_connection()

    seats_query = """
    SELECT
        college_name,
        course,
        COUNT(*) AS total_seats
    FROM allotted_seats
    WHERE course = ?
    """
    seats_params = [course]

    if state_filter:
        seats_query += " AND state = ?"
        seats_params.append(state_filter)

    seats_query += " GROUP BY college_name, course"

    seats_df = pd.read_sql_query(seats_query, conn, params=seats_params)
    conn.close()

    df = df.merge(seats_df, how='left', on=['college_name', 'course'])
    df['total_seats'] = df['total_seats'].fillna(0).astype(int)

    max_rank = df['avg_rank'].max()
    min_rank = df['avg_rank'].min()
    def norm_rank(r):
        return 1.0 if max_rank == min_rank else (max_rank - r) / (max_rank - min_rank)
    df['norm_avg_rank'] = df['avg_rank'].apply(norm_rank)

    max_seats = df['total_seats'].max()
    min_seats = df['total_seats'].min()
    def norm_seats(s):
        return 1.0 if max_seats == min_seats else (s - min_seats) / (max_seats - min_seats)
    df['norm_seats'] = df['total_seats'].apply(norm_seats)

    df['college_score'] = df['norm_avg_rank'] * 0.7 + df['norm_seats'] * 0.3

    df = df.sort_values('college_score', ascending=False).head(top_n).reset_index(drop=True)

    df['avg_rank'] = df['avg_rank'].round(0).astype(int)
    df['college_score'] = df['college_score'].round(3)

    # Add serial number starting from 1
    df.insert(0, 'S.No', range(1, len(df) + 1))

    # Rename columns nicely for display
    df = df.rename(columns={
        'college_name': 'College Name',
        'state': 'State',
        'course': 'Course',
        'address': 'Address',
        'avg_rank': 'Average Rank',
        'total_seats': 'Total Seats',
        'college_score': 'College Score'
    })

    return df[['S.No', 'College Name', 'State', 'Course', 'Address', 'Average Rank', 'Total Seats', 'College Score']]
