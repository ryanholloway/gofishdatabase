
# GoFish Web Game

This is a web-based version of the **Go Fish** card game, built using **Flask** for the backend and **MariaDB** for the database. The game allows users to play Go Fish against a computer, track their high scores, and view a leaderboard displaying the top 10 players based on their high scores.

## Features
- **Player vs. Computer**: Play a traditional Go Fish card game against an AI opponent.
- **Leaderboard**: View the top 10 players based on their highest score and the time when it was achieved.
- **Game Tracking**: Keep track of the number of games won and high scores for each player.

## Requirements
- **Python 3.7+**
- **Flask** (Backend framework)
- **MariaDB** (Database for storing player and game data)
- **HTML/CSS** for frontend rendering

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/ryanholloway/gofishdatabase.git
cd gofishdatabase
```

### Step 2: Install Dependencies
You will need to install the required Python dependencies. It's recommended to use a **virtual environment**.

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### Step 3: Setup MariaDB

1. **Create the Database**:
   - Log into MariaDB:
     ```bash
     mysql -u root -p
     ```
   - Create a new database for the Go Fish game:
     ```sql
     CREATE DATABASE gofishDB;
     ```

2. **Setup the Database Tables**:
   - Run the SQL setup commands from `gofish-schema.txt` to create the required tables and views.
     ```bash
     source gofish-schema.txt;
     ```

   This will create the necessary tables for `players` and `games`, as well as the `leaderboard` view.

### Step 4: Configure the Database in the Flask Application

1. Open the `app.py` file.
2. Set your **MariaDB connection details** in the `db_config` dictionary:
   ```python
   db_config = {
       'host': 'localhost',
       'database': 'gofishDB',
       'user': 'gofishuser',
       'password': 'gofishpassword'
   }
   ```

### Step 5: Run the Application

To start the Flask development server, run:

```bash
python app.py
```

By default, Flask will run on **http://localhost:5000**.

### Step 6: Play the Game

- Go to **http://localhost:5000** in your web browser.
- Register a new handle, and start playing the Go Fish game.
- After playing, you can check the **leaderboard** to see your ranking.

## SQL Schema

The SQL schema is included in the file `gofish-schema.txt` and includes the following:
- Creation of `players` and `games` tables.
- Creation of a `leaderboard` view that ranks players based on their highest score and displays the time when the highscore was achieved.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


![alt text](image-1.png)