import sqlite3

DB_PATH = "database/medical_allotment.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def clean_category(cat):
    # Just trim whitespace now that DB is cleaned
    if cat:
        return cat.strip()
    return cat


def get_non_pwd_category(category):
    # Map PwD category to base category (correct spelling "PwD")
    pwd_map = {
        "OBC PwD": "OBC",
        "OPEN PwD": "OPEN",
        "EWS PwD": "EWS",
        "ST PwD": "ST",
        "SC PwD": "SC",
    }
    cat_clean = clean_category(category)
    return pwd_map.get(cat_clean, cat_clean)


def get_courses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT course FROM allotted_seats ORDER BY course")
    courses = [r[0] for r in cur.fetchall()]
    conn.close()
    return courses


def get_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT allotted_category FROM allotted_seats ORDER BY allotted_category"
    )
    categories = [clean_category(r[0]) for r in cur.fetchall()]
    conn.close()
    return categories


def get_quotas(course):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DISTINCT allotted_quota
        FROM allotted_seats
        WHERE course = ?
        ORDER BY allotted_quota
    """,
        (course,),
    )
    quotas = [row[0] for row in cur.fetchall()]
    conn.close()
    return quotas


def get_last_rank(selected_course, selected_quota, selected_category):
    selected_category = clean_category(selected_category)
    conn = get_connection()
    cur = conn.cursor()

    # Try original category
    cur.execute(
        """
        SELECT MAX(rank)
        FROM allotted_seats
        WHERE course = ? AND allotted_quota = ? AND allotted_category = ?;
    """,
        (selected_course, selected_quota, selected_category),
    )
    row = cur.fetchone()
    if row and row[0] is not None:
        conn.close()
        return int(row[0])

    # Fallback to base category if PwD
    base_category = get_non_pwd_category(selected_category)
    if base_category != selected_category:
        cur.execute(
            """
            SELECT MAX(rank)
            FROM allotted_seats
            WHERE course = ? AND allotted_quota = ? AND allotted_category = ?;
        """,
            (selected_course, selected_quota, base_category),
        )
        row = cur.fetchone()
        if row and row[0] is not None:
            conn.close()
            return int(row[0])

    conn.close()
    return None


def get_eligible_courses(my_rank, selected_quota, selected_category):
    selected_category = clean_category(selected_category)
    conn = get_connection()
    cur = conn.cursor()

    categories_to_check = [selected_category]
    base_category = get_non_pwd_category(selected_category)
    if base_category != selected_category:
        categories_to_check.append(base_category)

    placeholders = ",".join("?" for _ in categories_to_check)

    query = f"""
        SELECT course, allotted_quota, allotted_category, MAX(rank) AS last_rank
        FROM allotted_seats
        WHERE allotted_category IN ({placeholders})
          AND allotted_quota = ?
        GROUP BY course, allotted_category
        HAVING last_rank >= ?
        ORDER BY last_rank;
    """
    params = categories_to_check + [selected_quota, my_rank]
    cur.execute(query, params)
    eligible_courses = cur.fetchall()
    conn.close()
    return eligible_courses
