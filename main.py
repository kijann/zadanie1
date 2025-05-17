import requests
import subprocess
import time
import crypt

from concurrent.futures import ThreadPoolExecutor

total_user_count = 100
new_accounts_per_loop = 5
break_between_new_accounts = 2
password = crypt.crypt("123P@ssw0rd", crypt.mksalt(crypt.METHOD_SHA512))
made_users = 0

# Funkcja zwraca dane użytkownika lub None, jeśli status != 200
def get_user():
    request = requests.get("https://randomuser.me/api/")
    if request.status_code != 200:
        return None
    user_json = request.json()
    if user_json.get("results") and len(user_json["results"]) > 0:
        firstname = user_json["results"][0]["name"]["first"]
        lastname = user_json["results"][0]["name"]["last"]
        username = user_json["results"][0]["login"]["username"]
        return [firstname, lastname, username]
    return None

# funkcja tworzy uzytkownika
def make_user():
    global made_users
    firstname, lastname, username = get_user()
    # sprawdzenia czy uzytkownik istnieje
    check_user_result = subprocess.run(['id', username], capture_output=True, text=True)
    if check_user_result.returncode == 0:
        print(f"uzytkownik {username} juz istnieje")
        return None
        # tworzenie użytkownika
    make_user_result = subprocess.run(['useradd', '-m', '-c', f"{firstname} {lastname}", '-p', password, username], capture_output=True)
    if make_user_result.returncode != 0:
        print(f"nie udalo utworzyc sie uzytkownika {username}: {make_user_result.stderr}")
        return None
    else:
        made_users = made_users + 1
        print(f"utworzono uzytkownika {username} nr {made_users}")
# Funkcja tworzy użytkowników w partiach po 5
def make_users(total_user_count, new_accounts_per_loop, break_between_new_accounts):
    global made_users
    while True:
        with ThreadPoolExecutor(max_workers=new_accounts_per_loop) as executor:
            for i in range(new_accounts_per_loop):
                executor.submit(make_user)
        if made_users%new_accounts_per_loop==0:
            time.sleep(break_between_new_accounts)
        if made_users>=total_user_count:
           break

make_users(total_user_count, new_accounts_per_loop, break_between_new_accounts)
