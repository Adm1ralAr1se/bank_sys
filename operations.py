class Operations:
    def __init__(self, account):
        self.account = account

    def deposit(self, amount):
        if amount > 0:
            self.account.balance += amount
            return f"Deposited: {amount}. New balance: {self.account.balance}"
        return "Deposit amount must be positive."

    def withdraw(self, amount):
        if 0 < amount <= self.account.balance:
            self.account.balance -= amount
            return f"Withdrew: {amount}. New balance: {self.account.balance}"
        return "Insufficient balance or invalid amount."

    def check_balance(self):
        return f"Current balance: {self.account.balance}"