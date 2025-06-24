class Account:
    def __init__(self, account_number, pincode, balance=0):
        self.account_number = account_number
        self.pincode = pincode
        self.balance = balance
        self.locked = False
        self.failed_attempts = 0

    def get_balance(self):
        return self.balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        return False

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False

    def update_pincode(self, new_pincode):
        self.pincode = new_pincode
        return True

class User:
    def __init__(self, username):
        self.username = username
        self.accounts = []  # List of Account objects

    def add_account(self, account):
        self.accounts.append(account)