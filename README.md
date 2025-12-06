# NEET PG Tools 🏥

> A data-driven suite of tools for NEET PG aspirants to predict ranks, find colleges, and analyze course eligibility.

![Dark Mode Home Page](https://via.placeholder.com/800x400?text=NEET+PG+Tools+Dark+Mode)

## Features

- **Rank Predictor**: Estimate your All India Rank based on your mock/exam score.
- **Course Predictor**: Find which courses you are eligible for based on previous year closing ranks.
- **Best Colleges**: Filter top medical colleges by state and course popularity.
- **Modern UI**: Fully responsive, Dark Mode enabled interface built with Tailwind CSS.

## Tech Stack

- **Backend**: Python, Flask, SQLite / Pandas
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Data**: Scikit-learn (for rank prediction model)

## Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/neet-pg-tools.git
    cd neet-pg-tools
    ```

2.  **Create a virtual environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Node dependencies (for Tailwind)**
    ```bash
    npm install
    ```

## Usage

1.  **Build CSS (if making changes)**
    ```bash
    npm run build
    ```

2.  **Run the Application**
    ```bash
    python app.py
    ```

3.  **Access in Browser**
    Open `http://127.0.0.1:5000`

## Project Structure

```
├── app.py                 # Main Flask Application
├── database/              # SQLite database files
├── static/
│   ├── src/input.css      # Tailwind source CSS
│   ├── dist/output.css    # Compiled CSS
│   └── main.js           # Frontend Logic
├── templates/             # HTML Templates
└── tailwind.config.js     # Tailwind Configuration
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
