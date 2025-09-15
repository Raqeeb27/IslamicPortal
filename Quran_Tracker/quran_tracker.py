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


def update_streak(juz_list):
    data = load_data()
    today = datetime.now().date()
    today_str = today.strftime("%d-%m-%Y")

    if data["last_date"]:
        last_date = datetime.strptime(data["last_date"], "%d-%m-%Y").date()

        if today == last_date:
            # Add juz to today's entry if not already added
            for entry in data["history"]:
                if entry["date"] == today_str:
                    for juz_number in juz_list:
                        if juz_number not in entry["juz"]:
                            entry["juz"].append(juz_number)
                        else:
                            print(f"\n\"Juz {juz_number}\" already marked for {today_str}")
                    entry["juz"].sort(
                        key=lambda x: float(
                            x.replace("¼", ".25").replace("½", ".5").replace("¾", ".75")
                        )
                    )
                    todays_juz = entry["juz"]
                    break
        elif today - last_date == timedelta(days=1):
            data["streak"] += 1
            data["history"].append({"date": today_str, "juz": juz_list})
            todays_juz = juz_list
        else:
            data["streak"] = 1  # reset streak
            data["history"].append({"date": today_str, "juz": juz_list})
            todays_juz = juz_list
    else:
        data["streak"] = 1
        data["history"].append({"date": today_str, "juz": juz_list})
        todays_juz = juz_list

    data["last_date"] = today_str
    save_data(data)
    return data, todays_juz


def get_valid_juz():
    ALLOWED_FRACTIONS = {"1/4": "¼", "1/2": "½", "3/4": "¾"}
    results = []

    while True:
        try:
            raw = input(
                "\nWhich Juz did you recite today (partial or complete)\n"
                "[Example: 1-30 or 2½ or 153/4]\n\n --> "
            ).strip()

            if raw in ["x", "q"]:
                print("\n\nExiting...\n")
                sys.exit(0)

            if not raw:
                input("\n❌ Please enter at least one Juz.\n\nPress Enter to continue..")
                print()
                continue

            parts = raw.split()
            results = []

            for juz in parts:
                # Direct integer juz (1–30)
                try:
                    if juz.isdigit() and 1 <= int(juz) <= 30:
                        results.append(juz)
                        continue
                except ValueError as e:
                    pass
                except Exception as e:
                    print(f"\n❌ Invalid Input: {e}")
                    sys.exit(1)

                # Juz with fraction symbols (like 5½, 13¾, etc.)
                for frac_symbol in ALLOWED_FRACTIONS.values():
                    if juz.endswith(frac_symbol):
                        base = juz[:-1]
                        if base.isdigit() and 1 <= int(base) <= 30:
                            results.append(juz)
                            break
                else:
                    # Juz with slash format (like 11/2 = 1½, 133/4 = 13¾)
                    for frac_str, frac_symbol in ALLOWED_FRACTIONS.items():
                        if juz.endswith(frac_str):
                            base = juz[: -len(frac_str)]
                            if base.isdigit() and 1 <= int(base) <= 30:
                                results.append(base + frac_symbol)
                                break
                    else:
                        input(f"\n❌ Invalid Juz input: {juz}\n\nPress Enter to continue...")
                        print()
                        break
            else:
                # only runs if no invalid input was found
                return results

        except (KeyboardInterrupt, EOFError):
            print("\n\nKeyboard Interrupt!!!\n\nExiting...\n")
            sys.exit(1)


def main():
    juz_list = get_valid_juz()
    data, todays_juz = update_streak(juz_list)
    print(f"\n✅ Logged Juz {', '.join(juz_list)} for {data['last_date']}.")
    print(f"🔥 Current Streak: {data['streak']} days")
    print(f"📖 Today's Juz: [ {', '.join(todays_juz)} ]\n")


if __name__ == "__main__":
    main()

