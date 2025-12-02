# NEET PG Helper Web Application

An AI-powered web application to assist NEET PG 2025 candidates in predicting eligible courses, finding the best medical colleges, and estimating their rank based on scored marks. The app leverages real counselling and allotment data with advanced statistical models for accurate and practical guidance.

---

## Features

- **Course Predictor:** Enter your rank, quota, and category to see eligible medical courses with closing ranks.
- **Best Colleges Finder:** Find top medical colleges filtered by state and rank thresholds with a custom scoring system.
- **Rank Predictor:** Input your total score (out of 800) to get an estimated NEET PG rank prediction using polynomial regression.

---

## Technology Stack

- **Backend:** Python, Flask web framework
- **Database:** SQLite for fast and lightweight data management
- **Frontend:** Bootstrap 5 for responsive and modern UI
- **Data Processing:** Pandas, scikit-learn for data analysis and rank prediction modeling

---

## Setup and Installation

1. **Clone the repository**

2. **Create a virtual environment and install dependencies**

3. **Prepare SQLite databases**
 - Run the provided Python scripts to create and populate the databases from Excel files:
   - `create_medical_allotment_db.py` for the allotment data
   - `create_rank_predictor_db.py` for rank prediction data

4. **Run the Flask app**
Or alternatively:

5. **Open the app**
Visit `http://localhost:5000` in your browser.

---

## Usage

- Navigate to the homepage to access all tools.
- Use **Course Predictor** to find eligible medical courses.
- Use **Best Colleges** to explore top-ranked colleges.
- Use **Rank Predictor** to estimate your rank based on score input.

---

## Version Control

This project uses Git for version control and is hosted on GitHub. It maintains a clear commit history to track changes, improvements, and bug fixes. Contributions are managed via branches and pull requests to ensure code quality and stability.

You can clone the repository using gitclone

Before contributing, please create a new branch and submit a pull request with your changes. This helps in reviewing and integrating your contributions safely.

---

## Disclaimer

The predictions and recommendations provided by this tool are based on historical data and statistical models. They are estimates and may not reflect actual seat allotments or results, which depend on many factors such as exam difficulty, counselling rounds, and reservation policies. Use this tool for informational purposes only.

---

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements and bug fixes.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contact

For questions or support, please reach out to [your email or GitHub profile].

---

*Built with ❤️ for NEET PG aspirants.*



