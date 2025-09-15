import os
import sys
import json
from datetime import datetime, timedelta


script_dir = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = os.path.join(script_dir, "quran_streak.json")


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"last_date": None, "streak": 0, "history": []}


def save_data(data):
    def custom_dump(obj, level=0):
        indent = " " * 4 * level
        if isinstance(obj, dict):
            items = []
            for k, v in obj.items():
                items.append(f'{indent}    "{k}": {custom_dump(v, level + 1)}')
            return indent + "{\n" + ",\n".join(items) + f"\n{indent}}}"
        elif isinstance(obj, list):
            # Inline short lists (like juz)
            if all(isinstance(x, str) for x in obj) and len(obj) <= 10:
                return "[ " + ", ".join(f'"{x}"' for x in obj) + " ]"
            else:
                return "[\n" + ",\n".join(custom_dump(x, level + 1) for x in obj) + f"\n{indent}]"
        elif isinstance(obj, str):
            return f'"{obj}"'
        else:
            return str(obj)

    with open(DATA_FILE, "w") as f:
        f.write(custom_dump(data, 0))


def update_streak(juz_number: str):
    data = load_data()
    today = datetime.now().date()
    today_str = today.strftime("%d-%m-%Y")

    if data["last_date"]:
        last_date = datetime.strptime(data["last_date"], "%d-%m-%Y").date()

        if today == last_date:
            # Add juz to today's entry if not already added
            for entry in data["history"]:
                if entry["date"] == today_str:
                    if juz_number not in entry["juz"]:
                        entry["juz"].append(juz_number)
                        entry["juz"].sort(key=lambda x: int(x))  # keep sorted
                    else:
                        print(f"\n\"Juz {juz_number}\" already marked for {today}")
                    todays_juz = entry["juz"]
                    break
        elif today - last_date == timedelta(days=1):
            data["streak"] += 1
            data["history"].append({"date": today_str, "juz": [juz_number]})
            todays_juz = [juz_number]
        else:
            data["streak"] = 1  # reset streak
            data["history"].append({"date": today_str, "juz": [juz_number]})
            todays_juz = [juz_number]
    else:
        data["streak"] = 1
        data["history"].append({"date": today_str, "juz": [juz_number]})
        todays_juz = [juz_number]

    data["last_date"] = today_str
    save_data(data)
    return data, todays_juz


def get_valid_juz():
    while True:
        try:
            juz = input("\nWhich Juz did you recite today (1–30): ").strip()
            if juz.isdigit() and 1 <= int(juz) <= 30:
                return juz
            else:
                print("\n❌ Invalid input. Please enter a juz number between 1 and 30.\n")
        except (KeyboardInterrupt, EOFError):
            print("\n\nKeyboard Interrupt!!!\n\nExiting...\n")
            sys.exit(1)


def main():
    juz = get_valid_juz()
    data, todays_juz = update_streak(juz)
    print(f"\n✅ Logged \"Juz {juz}\" for {data['last_date']}.")
    print(f"🔥 Current Streak: {data['streak']} days")
    print(f"📖 Today's Juz: [ {', '.join(todays_juz)} ]\n")


if __name__ == "__main__":
    main()
