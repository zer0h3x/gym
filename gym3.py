from datetime import datetime, timedelta
import re
from typing import Dict, List

from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem

# Data storage/admin && member login information stored in dict
user_accounts: dict[str, str] = {"username": "username123"}
mem_login: dict[str, dict] = {}
login_attempts = {}
sess_inf: dict[str, dict] = {
    "S01": {"user_name": "MA Classes", "cost": 1100, "sched": "Evening"},
    "S02": {"user_name": "Spin Classes", "cost": 900, "sched": "Morning"},
}  # Initialized two sessions spin, && MA,
check_in: list[dict] = []  # stores checkin info into a dict
instructor_info: list[dict] = []  # stores instructor info into a dict

current_user = None  # To store the current logged-in user


# authen process
def signup() -> bool:  # account signup verification
    print("\n [+]Welcome to Gym-On-The-Rock Sign Up ")
    username = input("[+]Please enter a username: ").strip()
    if username in user_accounts:
        print("[+]Error 409: username already has alredy been stored")
        return False
    password = input(
        "[+]Enter a unique password: "
    ).strip()  # A strong password & a strong body
    if len(password) < 6:
        print("[+]Error 1001: pass is too short")
        return False
    if not re.search(r"[A-Z]", password):
        print("[+]Error 1002: pass must contain one uppercase")
        return False
    if not re.search(r"[a-z]", password):
        print("[+]Error 1003: pass must contain at least one lowercase")
        return False
    if not re.search(r"\d", password):
        print("[+]Error 1004: pass must contain one digit")
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        print("[+]Error 1005: pass must contain one special char")
        return False
    user_accounts[username] = password
    print("[+]Great, let's start your fitness journey")
    return True


def login() -> bool:
    global current_user
    max_attempts = 3
    lockout_duration = timedelta(minutes=5)

    while True:
        print("[+]Start on your fitness journey, Login")
        username = input("[+]Enter username: ").strip()
        password = input("[+]Enter password: ").strip()

        if username not in login_attempts:
            login_attempts[username] = {"attempts": 0, "lockout_time": None}

        user_data = login_attempts[username]

        if user_data["lockout_time"]:
            if datetime.now() < user_data["lockout_time"]:
                remaining_lockout = user_data["lockout_time"] - datetime.now()
                print(
                    f"Account locked. Try again in {remaining_lockout.seconds // 60} minutes and {remaining_lockout.seconds % 60} seconds."
                )
                continue
            else:
                # Reset lockout after duration has passed
                user_data["attempts"] = 0
                user_data["lockout_time"] = None

        # Val cred
        if username in user_accounts and user_accounts[username] == password:
            print("[+]login attempt successful")
            # Res successful login
            user_data["attempts"] = 0
            current_user = username  # curr user
            return True
        else:
            user_data["attempts"] += 1
            attempts_left = max_attempts - user_data["attempts"]
            print(
                f"[+]Your credentials are invalid, {attempts_left} attempts remaining."
            )

            if user_data["attempts"] >= max_attempts:
                print("[+]Too many failed attempts. The system will logout.")
                return False


def ID_generator() -> str:
    return f"M{len(mem_login)+1:04d}"


def member_checkin() -> None:
    print("\n [+]Welcome to mem checkin :) ")
    while True:
        mem_ID = input("[+]Please enter your five-digit ID: ").strip().upper()
        if re.match(r"^M\d{4}$", mem_ID):
            break
        print("[+]Error 2020: ID must be 5 characters eg. M0007")
    if mem_ID not in mem_login:
        print("[+]Error 1006: Enter valid member ID")
        return
    checkin_time = datetime.now()
    check_in.append({"member_id": mem_ID, "timestamp": checkin_time, "sessions": []})

    print(f"[+]Welcome {mem_login[mem_ID]['first_name']}")
    print("[+]You have the following sessions available: ")
    for sid, session in sess_inf.items():
        print(f"{sid} {session['user_name']} - ${session['cost']} ({session['sched']})")

    while True:
        usr_choice = (
            input(
                "[+]Please enter the session ID (e.g. S01) to be able to register (when finished type F)"
            )
            .strip()
            .upper()
        )
        if usr_choice == "F":
            break
        if usr_choice in sess_inf:
            check_in[-1]["sessions"].append(usr_choice)
            print(f"[+]You registered for {sess_inf[usr_choice]['user_name']}")
        else:
            print("[+]The session ID is invalid")


def add_member():
    print("\n[+]Let's add a new member ---")
    mem_ID = ID_generator()

    while True:
        username = input("[+]Enter your first name: ").strip()
        if username.isalpha():
            break
        print("[+]Error 1008: invalid name, use alpha char only")

    username_last = input("[+]Enter your last name: ").strip()
    con_info = input("[+]Enter your contact/phone number: ")

    while True:
        mem_type = (
            input("[+]Select your membership type (Platinum/Diamond/Gold/Standard) ")
            .strip()
            .title()
        )
        if mem_type in ["Platinum", "Diamond", "Gold", "Standard"]:
            break
        print("Error 1009: please select one valid membership type")

    print("\n[+]Please confirm your details:")
    print(f"[+]First Name: {username}")
    print(f"[+]Last Name: {username_last}")
    print(f"[+]Contact: {con_info}")
    print(f"[+]Memship Type: {mem_type}")

    confirm = input("[+]Verify your info is it correct? (Y/N): ").strip().upper()
    if confirm != "Y":
        print("[+]Addition cancelled")
        return

    mem_login[mem_ID] = {
        "first_name": username,
        "last_name": username_last,
        "contact": con_info,
        "type": mem_type,
        "date": datetime.now().strftime("%Y-%m-%d"),
    }
    print(f"[+]You have successfully added member {mem_ID}")


def sess_mang():
    print("\n [+]Session Management")
    print("[+]Following existing sessions:")
    for sid, s in sess_inf.items():
        print(f"[+][{sid}] {s['user_name']} (${s['cost']})")
    user_prompt = input(
        "\n1. Enter 1 to add new \n2. Enter 2 to update existing sessions: "
    ).strip()

    if user_prompt == "1":
        if sess_inf:
            max_num = max(
                int(sid[1:])
                for sid in sess_inf
                if sid.startswith("S") and sid[1:].isdigit()
            )
            sess_ID = f"S{max_num + 1:02d}"
        else:
            sess_ID = "S01"
        name_s = input("[+]Session Name: ").strip()
        co = int(input("[+]The cost is: $").strip())
        sched = input("Sched = (Morning|Evening|Both): ").strip().title()
        sess_inf[sess_ID] = {"user_name": name_s, "cost": co, "sched": sched}
        print(f"[+]You have successfully added session {sess_ID}")

    elif user_prompt == "2":
        sess_ID = input("[+]Please enter session ID (e.g,S01): ").strip().upper()
        if sess_ID in sess_inf:
            print(f"[+]Your current info: {sess_inf[sess_ID]}")
            sess_inf[sess_ID]["cost"] = int(input("[+]Your new cost is: $").strip())
            sess_inf[sess_ID]["sched"] = input("[+]Your new schedule: ").strip().title()
            print("[+]Your session has been updated ")
        else:
            print("Error 1010: Invalid session ID")


def report_ge():
    print("[+]Welcome to Sys reports")

    print("\n[+]List of all members and the total num of members:")
    for mid, m in mem_login.items():
        print(f"[+]{mid}: {m['first_name']} {m['last_name']} ({m['type']})")
    print(f"\nTotal number of members: {len(mem_login)}")

    print("\n[+]List of all classes and their schedule:")
    for sid, deet in sess_inf.items():
        print(f"[+]{sid}: {deet['user_name']} - ${deet['cost']} ({deet['sched']})")

    c = {"Platinum": 0, "Diamond": 0, "Gold": 0, "Standard": 0}
    mem_fees = {"Platinum": 0, "Diamond": 0, "Gold": 0, "Standard": 0}
    for m in mem_login.values():
        c[m["type"]] += 1
        mem_fees[m["type"]] += mem_price[m["type"]]["cost"]
    print("\n[+]List of members for each membership type and total fees:")
    for t, count in c.items():
        print(f"[+]{t}: {count} members, Total fees: ${mem_fees[t]}")

    class_earnings = {sid: 0 for sid in sess_inf}
    print("\n[+]List of members registered for classes && total earnings:")
    for checkin in check_in:
        for sid in checkin["sessions"]:
            if sid in class_earnings:
                class_earnings[sid] += sess_inf[sid]["cost"]
    for sid, earnings in class_earnings.items():
        print(f"[+]{sid}: Total earnings: ${earnings}")

    print("\n[+]Report for each client with total monthly fee:")
    for mid, m in mem_login.items():
        membership_cost = mem_price[m["type"]]["cost"]
        included_sessions = mem_price[m["type"]]["sessions"]
        discount = mem_price[m["type"]]["discount"]

        all_sessions = []
        for checkin in check_in:
            if checkin["member_id"] == mid:
                all_sessions.extend(checkin["sessions"])

        session_cost = 0
        if len(all_sessions) > included_sessions:
            paid_sessions = all_sessions[included_sessions:]
            for sid in paid_sessions:
                if sid in sess_inf:
                    session_cost += sess_inf[sid]["cost"] * (1 - discount)

        mem_total = membership_cost + session_cost
        print(
            f"[+]{mid}: {m['first_name']} {m['last_name']}, Contact: {m['contact']}, Membership Type: {m['type']}, Total monthly fee: ${mem_total}"
        )

    print("\n[+]You have the following existing sessions:")
    for sid, s in sess_inf.items():
        print(f"[+][{sid}] {s['user_name']} (${s['cost']})")


def add_instructor():
    print("\n[+]Add instructor ")
    instructors_list = [
        "Jaxon Steele",
        "Blake Titan",
        "Ryder Knox",
        "Logan Vega",
        "Dante Storm",
    ]

    print("[+]Available instructors:")
    for i, name in enumerate(instructors_list, 1):
        print(f"{i}. {name}")

    while True:
        try:
            choice = int(input("[+]Select your instructor (1-5): "))
            if 1 <= choice <= 5:
                break
        except:
            pass
        print("[+]Invalid choice.")

    selected = instructors_list[choice - 1]
    first, last = selected.split()

    instr_ID = f"I{len(instructor_info)+1:03d}"

    instructor_info.append(
        {
            "id": instr_ID,
            "name": selected,
            "first_name": first,
            "last_name": last,
            "sessions": [],
        }
    )
    print(f"[+]Instructor {instr_ID} added: {selected}")


def main_menu():
    global current_user

    # Display the current user's details
    if current_user and current_user in user_accounts:
        print(f"\nWelcome, {current_user}!")

        user_sessions = []
        total_cost = 0
        for checkin in check_in:
            if checkin["member_id"] == current_user:
                user_sessions.extend(checkin["sessions"])

        if user_sessions:
            print("[+]Registered sessions:")
            for sid in user_sessions:
                session = sess_inf.get(sid)
                if session:
                    print(f"  - {session['user_name']}: ${session['cost']}")
                    total_cost += session["cost"]
            print(f"[+]Cost of current sessions: ${total_cost}")
        else:
            print("[+]You are not registered.")

    menu = ConsoleMenu(
        title="\033[36mGYM-ON-THE-ROCK\033[0m",
        subtitle="\033[32mBorn From The Fire Birthplace of Strength\033[0m",
    )

    items = [
        FunctionItem("\033[33mMember Check-in\033[0m", member_checkin),
        FunctionItem("\033[32mAdd A Member(s)\033[0m", add_member),
        FunctionItem("\033[34mManage Your Sessions\033[0m", sess_mang),
        FunctionItem("\033[35mAdd an Instructor\033[0m", add_instructor),
        FunctionItem("\033[36mGenerate Your Reports\033[0m", report_ge),
    ]

    for item in items:
        menu.append_item(item)

    menu.show()


def main():
    try:
        banner = r"""
   _____                        ____           _______ _                 _____            _
  / ____|                      / __ \         |__   __| |               |  __ \          | |
 | |  __ _   _ _ __ ___ ______| |  | |_ __ ______| |  | |__   ___ ______| |__) |___   ___| | __
 | | |_ | | | | '_ ` _ \______| |  | | '_ \______| |  | '_ \ / _ \______|  _  // _ \ / __| |/ /
 | |__| | |_| | | | | | |     | |__| | | | |     | |  | | | |  __/      | | \ \ (_) | (__|   <
  \_____|\__, |_| |_| |_|      \____/|_| |_|     |_|  |_| |_|\___|      |_|  \_\___/ \___|_|\_\\
          __/ |
         |___/
"""
        print(banner)
        print("[+]Welcome to Gym-On-The-Rock, The Birth Place of Strength\n")

        while True:
            user_prompt = input(
                "[+]Are you a member? you can become a member by selecting 1. Signing up or 2. Login: "
            )

            if user_prompt == "2" and login():
                main_menu()
                break
            elif user_prompt == "1":
                signup()
            else:
                print("Error 2003: Enter a valid option")
    except KeyboardInterrupt:
        print("\n^C\n[+]Have a nice day:)")
    except Exception as e:
        print(f"[+]An error occurred:(: {e}")
    finally:
        print("[+]Have a nice day:)")


if __name__ == "__main__":
    mem_price = {
        "Platinum": {"cost": 10000, "sessions": 4, "discount": 0.15},
        "Diamond": {"cost": 7500, "sessions": 2, "discount": 0.10},
        "Gold": {"cost": 4000, "sessions": 1, "discount": 0.05},
        "Standard": {"cost": 2000, "sessions": 0, "discount": 0},
    }

    main()
