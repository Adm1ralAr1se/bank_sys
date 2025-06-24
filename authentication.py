class Authenticator:
    def __init__(self, users):
        self.users = users  # Dict: username -> User

    def login(self, account_number, pincode):
        for user in self.users.values():
            for account in user.accounts:
                if account.account_number == account_number:
                    if account.locked:
                        return None, "Account is locked due to too many failed attempts."
                    if account.pincode == pincode:
                        account.failed_attempts = 0
                        return user, None
                    else:
                        account.failed_attempts += 1
                        if account.failed_attempts >= 3:
                            account.locked = True
                            return None, "Account locked after 3 failed attempts."
                        return None, f"Incorrect pincode. Attempt {account.failed_attempts}/3."
        return None, "Account not found."