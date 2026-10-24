import json
import os

TASKS_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")


def load_tasks():
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_tasks():
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)


tasks = load_tasks()

def add_task():
    name = input("Task name: ")
    while True:
        deadline_time = input("Deadline time (HH:MM, 24-hour format): ")

        try:
            time_parts = deadline_time.split(":")

            if len(time_parts) == 2:
                hour = int(time_parts[0])
                minute = int(time_parts[1])

                if 0 <= hour < 24 and 0 <= minute < 60:
                    break

            print("Enter a valid time, for example 18:30.")

        except ValueError:
            print("Enter a valid time, for example 18:30.")

    while True:
        try:
            days_left = int(input("Days until the deadline? Enter 0 if due today: "))
            if days_left >= 0:
                break
            print("Enter 0 or a positive number.")
        except ValueError:
            print("Enter a whole number.")

    while True:
        try:
            difficulty = int(input("Difficulty (1 to 5): "))
            if 1 <= difficulty <= 5:
                break
            print("Difficulty must be from 1 to 5.")
        except ValueError:
            print("Enter a whole number.")

    while True:
        try:
            hours = float(input("Estimated study hours: "))
            if hours > 0:
                break
            print("Study hours must be greater than 0.")
        except ValueError:
            print("Enter a number, for example 2 or 1.5.")
    while True:
        try:
            energy_need = int(
                input("Focus needed (1 = low, 5 = high): ")
            )
            if 1 <= energy_need <= 5:
                break
            print("Enter a number from 1 to 5.")
        except ValueError:
            print("Enter a whole number from 1 to 5.")
    task = {
        "name": name,
        "days_left": days_left,
        "deadline_time": deadline_time,
        "difficulty": difficulty,
        "hours": hours,
        "energy_need": energy_need
    }

    tasks.append(task)
    save_tasks()
    print("Task added!\n")
def view_tasks():
    if len(tasks) == 0:
        print("No tasks added yet.\n")
        return

    for number, task in enumerate(tasks, start=1):
        print(f"\n{number}. {task['name']}")
        print(
            f"   Deadline: in {task['days_left']} day(s), "
            f"at {task.get('deadline_time', '23:59')}"
        )
        print(f"   Difficulty: {task['difficulty']}/5")
        print(f"   Study hours: {task['hours']}")
        print(f"   Focus needed: {task.get('energy_need', 3)}/5")

def delete_task():
    if len(tasks) == 0:
        print("There are no tasks to delete.\n")
        return

    view_tasks()

    try:
        task_number = int(input("Enter the number of the task to delete: "))
    except ValueError:
        print("Please enter a task number.\n")
        return

    if task_number < 1 or task_number > len(tasks):
        print("That task number does not exist.\n")
        return

    task = tasks[task_number - 1]
    confirmation = input(
        f"Delete '{task['name']}'? Type yes to confirm: "
    )

    if confirmation.lower() == "yes":
        deleted_task = tasks.pop(task_number - 1)
        save_tasks()
        print(f"'{deleted_task['name']}' was deleted.\n")
    else:
        print("Task was not deleted.\n")

STUDY_SESSION_MINUTES = 50
BREAK_MINUTES = 10


def time_to_minutes(time_text):
    hour_text, minute_text = time_text.split(":")
    hours = int(hour_text)
    minutes = int(minute_text)
    return hours * 60 + minutes


def minutes_to_time(total_minutes):
    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"

def priority_score(task, current_energy):
    days = task["days_left"]

    if days <= 1:
        urgency = 5
    elif days <= 3:
        urgency = 4
    elif days <= 7:
        urgency = 3
    else:
        urgency = 2

    task_energy = task.get("energy_need", 3)
    energy_match = 5 - abs(task_energy - current_energy)

    return (urgency, energy_match, task["difficulty"])

def make_study_plan():
    if len(tasks) == 0:
        print("Add some tasks first.\n")
        return

    while True:
        time_text = input("Enter current time (HH:MM, 24-hour format): ")

        try:
            time_parts = time_text.split(":")

            if len(time_parts) == 2:
                hour = int(time_parts[0])
                minute = int(time_parts[1])

                if 0 <= hour < 24 and 0 <= minute < 60:
                    start_minutes = time_to_minutes(time_text)
                    break

            print("Enter a valid time, for example 21:30.")

        except ValueError:
            print("Enter a valid time, for example 21:30.")
    while True:
        try:
            current_energy = int(
                input("Your current focus level (1 = low, 5 = high): ")
            )
            if 1 <= current_energy <= 5:
                break
            print("Enter a number from 1 to 5.")
        except ValueError:
            print("Enter a whole number from 1 to 5.")
    while True:
        bedtime_text = input("Planned bedtime (HH:MM, 24-hour format): ")

        try:
            parts = bedtime_text.split(":")
            if len(parts) == 2:
                hour = int(parts[0])
                minute = int(parts[1])

                if 0 <= hour < 24 and 0 <= minute < 60:
                    bedtime_minutes = time_to_minutes(bedtime_text)

                    if bedtime_minutes <= start_minutes:
                        bedtime_minutes += 24 * 60

                    break

            print("Enter a valid bedtime, for example 23:00.")

        except ValueError:
            print("Enter a valid bedtime, for example 23:00.")

    current_minutes = start_minutes
    minutes_available = bedtime_minutes - start_minutes
    while True:
        try:
            max_study_hours = float(
                input("Maximum focused study hours before bedtime: ")
            )
            if max_study_hours > 0:
                break
            print("Enter a number greater than 0.")
        except ValueError:
            print("Enter a number, for example 2 or 2.5.")

    study_minutes_left = round(max_study_hours * 60)
    ordered_tasks = sorted(
        tasks,
        key=lambda task: priority_score(task, current_energy),
        reverse=True
    )

    schedule = [] 
    study_sessions = 0
    unfinished_tasks = []

    for task_number, task in enumerate(ordered_tasks):
        task_minutes = round(task["hours"] * 60)

        while task_minutes > 0 and minutes_available > 0 and study_minutes_left > 0:
            if current_energy <= 2 and study_sessions < 2:
                session_length = 20
                break_length = 15
            elif current_energy <= 2:
                session_length = 25
                break_length = 15
            elif current_energy == 3:
                session_length = 30
                break_length = 15
            else:
                session_length = 40
                break_length = 15
            study_block = min(
                session_length,
                task_minutes,
                minutes_available,
                study_minutes_left
            )

            start_time = minutes_to_time(current_minutes)
            end_time = minutes_to_time(current_minutes + study_block)

            schedule.append(
                (start_time, end_time, "STUDY", task["name"], task["days_left"])
            )

            current_minutes += study_block
            minutes_available -= study_block
            study_minutes_left -= study_block
            study_sessions += 1
            task_minutes -= study_block
            if study_sessions == 4 or study_sessions == 8:
                break_length = 60
            more_work = task_minutes > 0 or len(ordered_tasks) > task_number + 1

            if (
                study_block == session_length
                and more_work
                and minutes_available >= break_length
                and study_minutes_left > 0
            ):
                break_start = minutes_to_time(current_minutes)
                break_end = minutes_to_time(current_minutes + break_length)
                if break_length == 60:
                    break_name = "Take a long break"
                else:
                    break_name = "Take a short break"

                schedule.append(
                    (break_start, break_end, "BREAK", break_name, None)
                )

                current_minutes += break_length
                minutes_available -= break_length

        if task_minutes > 0:
            unfinished_tasks.append(
                (task["name"], task["days_left"], task_minutes)
            )
    print(f"\nYour current focus level: {current_energy}/5")

    print("\nTONIGHT'S SUGGESTED SCHEDULE")

    for session in schedule:
        start_time, end_time, kind, name, days_left = session

        if kind == "STUDY":
            if days_left == 0:
                deadline_text = "due today"
            else:
                deadline_text = f"due in {days_left} day(s)"

            print(f"{start_time}-{end_time} | Study | {name} ({deadline_text})")
        else:
            print(f"{start_time}-{end_time} | Break | {name}")

    if len(unfinished_tasks) > 0:
        print("\nDISCLAIMER: Some study work will remain after midnight.")

        for name, days_left, remaining_minutes in unfinished_tasks:
            remaining_hours = remaining_minutes / 60
            print(
                f"- {name}: {remaining_hours:.1f} hour(s) left; "
                f"deadline in {days_left} day(s)"
            )

        print("Consider starting earlier or adjusting your workload.")
    else:
        print("\nAll task estimates fit before midnight.")

if __name__ == "__main__":
    while True:
        print("\nSTUDENT ENERGY PLANNER")
        print("1. Add a task")
        print("2. View tasks")
        print("3. Make a study plan")
        print("4. Delete a task")
        print("5. Exit")

        try:
            choice = input("Choose 1, 2, 3, 4 or 5: ")
        except EOFError:
            print("\nGoodbye!")
            break

        if choice == "1":
            add_task()
        elif choice == "2":
            view_tasks()
        elif choice == "3":
            make_study_plan()
        elif choice == "4":
            delete_task()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Please choose 1, 2, 3, 4 or 5.")