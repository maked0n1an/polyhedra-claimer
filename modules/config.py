with open('input_data/proxies.txt', 'r') as file:
    PROXIES = [row.strip() for row in file]

with open('input_data/cookies.txt', 'r') as file:
    COOKIES = [row.strip() for row in file]

with open('input_data/account_names.txt', 'r') as file:
    ACCOUNT_NAMES = [row.strip() for row in file]
