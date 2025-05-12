import os
import datetime
import numpy as np
import random
import subprocess

# --- CONFIGURATION --- #
repo_path = "."  # Change this to your repo path
branch = "main"  # Change if necessary

# Define the date range
start_date = datetime.date(2023, 1, 15)
end_date = datetime.date(2023, 1, 30)

# Gaussian distribution parameters
mean_commits = 3  # Average commits per day
std_dev_commits = 2  # Variation in commits per day

# Weekly commit trends (likelihood of commits per day)
commit_weights = {
    0: 0.6,  # Monday
    1: 1.0,  # Tuesday
    2: 1.2,  # Wednesday
    3: 1.2,  # Thursday
    4: 1.1,  # Friday
    5: 0.8,  # Saturday
    6: 0.5,  # Sunday
}

# Late-night coding probability (Friday & Saturday)
late_night_prob = {4: 0.3, 5: 0.4}  # 30% on Fridays, 40% on Saturdays

# List of no-commit days (YYYY-MM-DD format)
no_commit_days = {
    "2019-12-25",  # Christmas
    "2020-01-01",  # New Year's Day
    "2021-07-04",  # Example: Independence Day
    # Add more as needed
}

# Simulate "burnout weeks" where fewer commits happen
burnout_prob = 0.1  # 10% chance that a week has significantly fewer commits

# --- FUNCTION TO CREATE COMMITS --- #
def make_commit(commit_date, num_commits, is_late_night=False):
    for _ in range(num_commits):
        if is_late_night:
            hour = random.randint(23, 2)  # Between 11 PM and 2 AM
        else:
            hour = np.random.choice([random.randint(8, 12), random.randint(13, 19)], p=[0.4, 0.6])  
        
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        timestamp = f"{commit_date} {hour}:{minute}:{second}"
        os.environ["GIT_COMMITTER_DATE"] = timestamp
        os.environ["GIT_AUTHOR_DATE"] = timestamp

        # Write commit file
        file_path = os.path.join(repo_path, "dummy.txt")
        with open(file_path, "a") as f:
            f.write(f"Commit on {timestamp}\n")

        # Run Git commands
        subprocess.run(["git", "add", file_path], cwd=repo_path)
        subprocess.run(["git", "commit", "-m", f"Automated commit on {timestamp}"], cwd=repo_path)

# --- MAIN SCRIPT --- #
def main():
    os.chdir(repo_path)
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        weekday = current_date.weekday()

        # Skip no-commit days
        if date_str in no_commit_days:
            print(f"Skipping {date_str} (No-commit day)")
        else:
            # Apply weekly trends
            weight = commit_weights.get(weekday, 1.0)
            num_commits = max(0, round(np.random.normal(mean_commits * weight, std_dev_commits)))

            # Occasionally simulate burnout weeks
            if random.random() < burnout_prob:
                num_commits = max(0, num_commits // 2)

            # Late-night commits on Fridays & Saturdays
            is_late_night = weekday in late_night_prob and random.random() < late_night_prob[weekday]

            if num_commits > 0:
                print(f"Committing {num_commits} times on {date_str} {'(Late night)' if is_late_night else ''}")
                make_commit(date_str, num_commits, is_late_night)

        current_date += datetime.timedelta(days=1)

    # Push all commits at once
    subprocess.run(["git", "push", "origin", branch], cwd=repo_path)

if __name__ == "__main__":
    main()
