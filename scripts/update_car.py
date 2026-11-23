
import os
import json
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from PIL import Image


# ================= SETTINGS =================

USERNAME = "Mano522"

BASE_GIF = Path("assets/innova-crysta.gif")
OUTPUT_GIF = Path("profile/innova-crysta-live.gif")
STATUS_FILE = Path("profile/car-status.json")

GITHUB_API = "https://api.github.com/graphql"


# ================= GET GITHUB ACTIVITY =================

def get_github_activity():
    token = os.getenv("GH_TOKEN")

    if not token:
        raise RuntimeError("GH_TOKEN is missing. Add it to GitHub Actions Secrets.")

    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=400)

    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """

    payload = {
        "query": query,
        "variables": {
            "username": USERNAME,
            "from": start_date.isoformat() + "T00:00:00Z",
            "to": today.isoformat() + "T23:59:59Z"
        }
    }

    request = urllib.request.Request(
        GITHUB_API,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Mano522-GitHub-Car"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))

    if result.get("errors"):
        raise RuntimeError(f"GitHub API error: {result['errors']}")

    user = result.get("data", {}).get("user")

    if not user:
        raise RuntimeError(f"GitHub user '{USERNAME}' was not found.")

    weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]

    contributions = {}

    for week in weeks:
        for day in week["contributionDays"]:
            contributions[date.fromisoformat(day["date"])] = day["contributionCount"]

    today_count = contributions.get(today, 0)

    # Calculate current streak.
    # If there are no contributions today, yesterday may still hold the streak.
    check_day = today if today_count > 0 else today - timedelta(days=1)

    streak = 0

    while contributions.get(check_day, 0) > 0:
        streak += 1
        check_day -= timedelta(days=1)

    return streak, today_count


# ================= CALCULATE CAR SPEED =================

def calculate_speed(streak, today_count):

    score = (streak * 2) + (today_count * 3)

    if streak == 0 and today_count == 0:
        return "Parked", score, 1.0

    if score <= 4:
        return "Slow", score, 1.5

    if score <= 10:
        return "Normal", score, 1.0

    if score <= 20:
        return "Fast", score, 0.65

    return "Turbo", score, 0.35


# ================= GENERATE NEW GIF =================

def generate_car_gif(speed, multiplier):

    if not BASE_GIF.exists():
        raise FileNotFoundError(
            f"Base GIF not found: {BASE_GIF}. Upload assets/innova-crysta.gif first."
        )

    OUTPUT_GIF.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(BASE_GIF) as gif:

        frames = []
        durations = []

        frame_count = getattr(gif, "n_frames", 1)

        for index in range(frame_count):
            gif.seek(index)

            frame = gif.convert("RGBA").copy()
            original_duration = gif.info.get("duration", 100)

            frames.append(frame)
            durations.append(original_duration)

        if not frames:
            raise RuntimeError("The base GIF contains no frames.")

        # Parked = show only the first frame.
        if speed == "Parked":
            frames = [frames[0]]
            durations = [1000]

        else:
            durations = [
                max(20, int(duration * multiplier))
                for duration in durations
            ]

        frames[0].save(
            OUTPUT_GIF,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            disposal=2,
            optimize=True
        )


# ================= SAVE STATUS =================

def save_status(streak, today_count, speed, score):

    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)

    status = {
        "username": USERNAME,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "current_streak": streak,
        "today_contributions": today_count,
        "activity_score": score,
        "car_speed": speed
    }

    STATUS_FILE.write_text(
        json.dumps(status, indent=4),
        encoding="utf-8"
    )


# ================= MAIN PROGRAM =================

def main():

    print("Checking GitHub activity...")

    streak, today_count = get_github_activity()

    speed, score, multiplier = calculate_speed(
        streak,
        today_count
    )

    print(f"Current streak: {streak} days")
    print(f"Today's contributions: {today_count}")
    print(f"Activity score: {score}")
    print(f"Car speed: {speed}")

    generate_car_gif(speed, multiplier)
    save_status(streak, today_count, speed, score)

    print("Innova GIF updated successfully!")


if __name__ == "__main__":
    main()
