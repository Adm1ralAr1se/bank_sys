from bank.account import Account, User
from bank.authentication import Authenticator
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

# In-memory user storage
users = {
    "alice": User("alice"),
    "bob": User("bob")
}
# Add accounts for users
users["alice"].add_account(Account("1001", "1234", 500))
users["alice"].add_account(Account("1002", "5678", 1500))
users["bob"].add_account(Account("2001", "4321", 800))

auth = Authenticator(users)

# Transaction log
transaction_log = []

# Add this global variable to store update history
update_history = []

def deposit_funds(user):
    print("\nDeposit Funds")
    for idx, acc in enumerate(user.accounts):
        print(f"{idx+1}. Account {acc.account_number} (Balance: ${acc.balance:.2f})")
    try:
        choice = int(input("Select account to deposit into (number): ")) - 1
        if not (0 <= choice < len(user.accounts)):
            print("Invalid selection.")
            return
        selected_acc = user.accounts[choice]
        print("Accepted denominations: 0.05, 0.10, 0.25")
        amount = 0
        while True:
            coin = input("Enter coin to deposit (or 'done' to finish): ")
            if coin.lower() == 'done':
                break
            try:
                coin = float(coin)
                if coin < 0:
                    print("Negative values are not allowed.")
                elif coin in [0.05, 0.10, 0.25]:
                    amount += coin
                else:
                    print("Invalid denomination.")
            except ValueError:
                print("Please enter a valid number or 'done'.")
        if amount > 0:
            selected_acc.balance += amount
            now = datetime.datetime.now()
            # Log the transaction
            transaction_log.append({
                "account_number": selected_acc.account_number,
                "user": user.username,
                "datetime": now.strftime('%Y-%m-%d %H:%M:%S'),
                "type": "+Deposit",
                "amount": amount
            })
            print("\n--- Deposit Receipt ---")
            print(f"Account Number: {selected_acc.account_number}")
            print(f"User Name: {user.username}")
            print(f"Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Amount Deposited: ${amount:.2f}")
            print(f"Current Balance: ${selected_acc.balance:.2f}")
            print("----------------------\n")
        else:
            print("No coins deposited.")
    except Exception as e:
        print("Error during deposit:", e)

# Track daily withdrawals: { (account_number, date): amount_withdrawn }
daily_withdrawals = {}

def withdraw_funds(user):
    print("\nWithdraw Funds")
    for idx, acc in enumerate(user.accounts):
        print(f"{idx+1}. Account {acc.account_number} (Balance: ${acc.balance:.2f})")
    try:
        choice = int(input("Select account to withdraw from (number): ")) - 1
        if not (0 <= choice < len(user.accounts)):
            print("Invalid selection.")
            return
        selected_acc = user.accounts[choice]
        print("Available denominations: 0.05, 0.10, 0.25")
        print(f"Current Balance: ${selected_acc.balance:.2f}")

        # Get today's date string
        today = datetime.date.today().isoformat()
        key = (selected_acc.account_number, today)
        withdrawn_today = daily_withdrawals.get(key, 0)

        if withdrawn_today >= 0.90:
            print("Daily withdrawal limit of $0.90 reached for this account.")
            return

        amount = 0
        coins = []
        while True:
            coin = input("Enter coin to withdraw (or 'done' to finish): ")
            if coin.lower() == 'done':
                break
            try:
                coin = float(coin)
                if coin in [0.05, 0.10, 0.25]:
                    if amount + coin + withdrawn_today > 0.90:
                        print("This withdrawal would exceed the daily limit of $0.90.")
                        continue
                    if selected_acc.balance - amount - coin < 0.05:
                        print("Cannot withdraw: minimum balance of 0.05 required.")
                        continue
                    if amount + coin > selected_acc.balance:
                        print("Insufficient funds for this coin.")
                        continue
                    amount += coin
                    coins.append(coin)
                else:
                    print("Invalid denomination.")
            except ValueError:
                print("Please enter a valid number or 'done'.")
        if amount > 0:
            selected_acc.balance -= amount
            daily_withdrawals[key] = withdrawn_today + amount
            now = datetime.datetime.now()
            # Log the transaction
            transaction_log.append({
                "account_number": selected_acc.account_number,
                "user": user.username,
                "datetime": now.strftime('%Y-%m-%d %H:%M:%S'),
                "type": "-Withdrawal",
                "amount": amount
            })
            print("\n--- Withdrawal Receipt ---")
            print(f"Account Number: {selected_acc.account_number}")
            print(f"User Name: {user.username}")
            print(f"Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Amount Withdrawn: ${amount:.2f}")
            print(f"Current Balance: ${selected_acc.balance:.2f}")
            print("-------------------------\n")
        else:
            print("No coins withdrawn.")
    except Exception as e:
        print("Error during withdrawal:", e)

def create_new_account(user):
    print("\nCreate New Account")
    while True:
        new_acc_num = input("Enter a new account number: ")
        # Check if account number already exists for any user
        exists = False
        for u in users.values():
            for acc in u.accounts:
                if acc.account_number == new_acc_num:
                    exists = True
                    break
            if exists:
                break
        if exists:
            print("Account number already exists. Please choose another.")
        else:
            break
    new_pin = input("Set a 4-digit pincode for the new account: ")
    # Basic validation for PIN
    if not (new_pin.isdigit() and len(new_pin) == 4):
        print("Invalid PIN. Must be 4 digits.")
        return
    new_account = Account(new_acc_num, new_pin, balance=0.05)
    user.add_account(new_account)
    print(f"Account {new_acc_num} created successfully with initial deposit of $0.05.")

def transfer_between_own_accounts(user):
    print("\nTransfer Funds Between Your Accounts")
    if len(user.accounts) < 2:
        print("You need at least two accounts to transfer funds.")
        return
    # List accounts
    for idx, acc in enumerate(user.accounts):
        print(f"{idx+1}. Account {acc.account_number} (Balance: ${acc.balance:.2f})")
    try:
        from_idx = int(input("Select FROM account (number): ")) - 1
        to_idx = int(input("Select TO account (number): ")) - 1
        if from_idx == to_idx:
            print("Cannot transfer to the same account.")
            return
        if not (0 <= from_idx < len(user.accounts)) or not (0 <= to_idx < len(user.accounts)):
            print("Invalid selection.")
            return
        from_acc = user.accounts[from_idx]
        to_acc = user.accounts[to_idx]
        print(f"FROM Account {from_acc.account_number} (Balance: ${from_acc.balance:.2f})")
        print(f"TO Account {to_acc.account_number} (Balance: ${to_acc.balance:.2f})")
        amount = float(input("Enter amount to transfer (multiples of 0.05, 0.10, or 0.25): "))
        if amount <= 0:
            print("Amount must be positive.")
            return
        if amount not in [0.05, 0.10, 0.25] and amount % 0.05 != 0:
            print("Amount must be in valid denominations or multiples of 0.05.")
            return
        if from_acc.balance - amount < 0.05:
            print("Insufficient funds. Minimum balance of $0.05 must remain.")
            return
        from_acc.balance -= amount
        to_acc.balance += amount
        now = datetime.datetime.now()
        # Log the transaction for both accounts
        transaction_log.append({
            "account_number": from_acc.account_number,
            "user": user.username,
            "datetime": now.strftime('%Y-%m-%d %H:%M:%S'),
            "type": "-Transfer (own)",
            "amount": amount
        })
        transaction_log.append({
            "account_number": to_acc.account_number,
            "user": user.username,
            "datetime": now.strftime('%Y-%m-%d %H:%M:%S'),
            "type": "+Transfer (own)",
            "amount": amount
        })
        print("\n--- Transfer Receipt ---")
        print(f"From Account: {from_acc.account_number}")
        print(f"To Account: {to_acc.account_number}")
        print(f"User Name: {user.username}")
        print(f"Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Amount Transferred: ${amount:.2f}")
        print(f"From Account New Balance: ${from_acc.balance:.2f}")
        print(f"To Account New Balance: ${to_acc.balance:.2f}")
        print("------------------------\n")
    except Exception as e:
        print("Error during transfer:", e)

def transfer_to_other_user(user):
    print("\nTransfer Funds to Another User's Account")
    # List user's own accounts
    for idx, acc in enumerate(user.accounts):
        print(f"{idx+1}. Your Account {acc.account_number} (Balance: ${acc.balance:.2f})")
    try:
        from_idx = int(input("Select FROM account (number): ")) - 1
        if not (0 <= from_idx < len(user.accounts)):
            print("Invalid selection.")
            return
        from_acc = user.accounts[from_idx]
        to_acc_num = input("Enter the recipient's account number: ")
        # Find the recipient account and user
        recipient = None
        to_acc = None
        for u in users.values():
            for acc in u.accounts:
                if acc.account_number == to_acc_num:
                    recipient = u
                    to_acc = acc
                    break
            if to_acc:
                break
        if not to_acc:
            print("Recipient account not found.")
            return
        if to_acc.account_number == from_acc.account_number:
            print("Cannot transfer to the same account.")
            return
        amount = float(input("Enter amount to transfer (multiples of 0.05, 0.10, or 0.25): "))
        if amount <= 0:
            print("Amount must be positive.")
            return
        if amount not in [0.05, 0.10, 0.25] and amount % 0.05 != 0:
            print("Amount must be in valid denominations or multiples of 0.05.")
            return
        if from_acc.balance - amount < 0.05:
            print("Insufficient funds. Minimum balance of $0.05 must remain.")
            return
        from_acc.balance -= amount
        to_acc.balance += amount
        now = datetime.datetime.now()
        # Log the transaction for both accounts
        transaction_log.append({
            "account_number": from_acc.account_number,
            "user": user.username,
            "datetime": now.strftime('%Y-%m-%d %H:%M:%S'),
            "type": "-Transfer (to other)",
            "amount": amount
        })
        transaction_log.append({
            "account_number": to_acc.account_number,
            "user": recipient.username,
            "datetime": now.strftime('%Y-%m-%d %H:%M:%S'),
            "type": "+Transfer (from other)",
            "amount": amount
        })
        print("\n--- Transfer Receipt ---")
        print(f"From Account: {from_acc.account_number} (User: {user.username})")
        print(f"To Account: {to_acc.account_number} (User: {recipient.username})")
        print(f"Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Amount Transferred: ${amount:.2f}")
        print(f"From Account New Balance: ${from_acc.balance:.2f}")
        print(f"To Account New Balance: ${to_acc.balance:.2f}")
        print("------------------------\n")
    except Exception as e:
        print("Error during transfer:", e)

def view_transaction_history(user):
    print("\n--- Transaction History ---")
    found = False
    for acc in user.accounts:
        for tx in transaction_log:
            if tx["account_number"] == acc.account_number:
                found = True
                print(f"{tx['datetime']} | {tx['account_number']} | {tx['user']} | {tx['type']} | ${tx['amount']:.2f}")
    if not found:
        print("No transactions found.")
    print("---------------------------\n")

# New function to update personal information (PIN)
def update_personal_info(user):
    print("\nUpdate Personal Information (PIN)")
    # List user's accounts
    for idx, acc in enumerate(user.accounts):
        print(f"{idx+1}. Account {acc.account_number}")
    try:
        acc_idx = int(input("Select account to update PIN (number): ")) - 1
        if not (0 <= acc_idx < len(user.accounts)):
            print("Invalid selection.")
            return
        acc = user.accounts[acc_idx]
        old_pin = input("Enter current PIN: ")
        if old_pin != acc.pincode:
            print("Incorrect PIN. Update aborted.")
            return
        new_pin = input("Enter new 4-digit PIN: ")
        if not (new_pin.isdigit() and len(new_pin) == 4):
            print("Invalid PIN. Must be 4 digits.")
            return
        if new_pin == acc.pincode:
            print("New PIN must be different from the old PIN.")
            return
        old_pincode = acc.pincode
        acc.pincode = new_pin
        now = datetime.datetime.now()
        update_history.append({
            "account_number": acc.account_number,
            "user": user.username,
            "datetime": now.strftime('%Y-%m-%d %H:%M:%S'),
            "old_pin": old_pincode,
            "new_pin": new_pin
        })
        print("PIN updated successfully.")
    except Exception as e:
        print("Error during update:", e)

# New function to view update history
def view_update_history(user):
    print("\n--- PIN Update History ---")
    found = False
    for acc in user.accounts:
        for upd in update_history:
            if upd["account_number"] == acc.account_number:
                found = True
                print(f"{upd['datetime']} | {upd['account_number']} | {upd['user']} | Old PIN: {upd['old_pin']} | New PIN: {upd['new_pin']}")
    if not found:
        print("No update history found.")
    print("--------------------------\n")

def admin_menu():
    print("\n--- SYSTEM ADMINISTRATOR MENU ---")
    while True:
        print("\nAdmin Options:")
        print("1. View all accounts")
        print("2. Freeze/Unfreeze account")
        print("3. Add/Remove funds")
        print("4. View all transaction logs")
        print("5. Activity report")
        print("6. Exit admin menu")
        choice = input("Select an option (1-6): ")
        if choice == '1':
            admin_view_accounts()
        elif choice == '2':
            admin_freeze_unfreeze()
        elif choice == '3':
            admin_fund_management()
        elif choice == '4':
            admin_view_transaction_logs()
        elif choice == '5':
            admin_activity_report()
        elif choice == '6':
            break
        else:
            print("Invalid option.")

def admin_view_accounts():
    print("\n--- All Accounts ---")
    for user in users.values():
        for acc in user.accounts:
            status = "Frozen" if getattr(acc, "frozen", False) else "Active"
            print(f"User: {user.username} | Account: {acc.account_number} | Balance: ${acc.balance:.2f} | Status: {status}")
    print("--------------------")

def admin_freeze_unfreeze():
    acc_num = input("Enter account number to freeze/unfreeze: ")
    for user in users.values():
        for acc in user.accounts:
            if acc.account_number == acc_num:
                acc.frozen = not getattr(acc, "frozen", False)
                status = "Frozen" if acc.frozen else "Unfrozen"
                print(f"Account {acc_num} is now {status}.")
                return
    print("Account not found.")

def admin_fund_management():
    acc_num = input("Enter account number to add/remove funds: ")
    for user in users.values():
        for acc in user.accounts:
            if acc.account_number == acc_num:
                print(f"Current balance: ${acc.balance:.2f}")
                amt = float(input("Enter amount to add (positive) or remove (negative): "))
                if acc.balance + amt < 0:
                    print("Insufficient funds for removal.")
                    return
                acc.balance += amt
                print(f"New balance: ${acc.balance:.2f}")
                return
    print("Account not found.")

def admin_view_transaction_logs():
    print("\n--- All Transaction Logs ---")
    for tx in transaction_log:
        print(f"{tx['datetime']} | {tx['account_number']} | {tx['user']} | {tx['type']} | ${tx['amount']:.2f}")
    print("----------------------------")

def admin_activity_report():
    print("\n--- Activity Report ---")
    account_activity = {}
    for tx in transaction_log:
        acc = tx['account_number']
        account_activity.setdefault(acc, 0)
        account_activity[acc] += 1
    for acc, count in account_activity.items():
        print(f"Account {acc}: {count} transactions")
    print("-----------------------")

# Add this at the start of your main() function:
def main():
    print("Welcome to Simple Bank System")
    while True:
        mode = input("Login as (1) User or (2) Admin? ")
        if mode == '2':
            admin_menu()
            continue
        acc_num = input("Enter your account number: ")
        pin = input("Enter your pincode: ")
        user, msg = auth.login(acc_num, pin)
        if user:
            print(f"Welcome, {user.username}!")
            print("Your accounts:")
            for idx, acc in enumerate(user.accounts):
                print(f"{idx+1}. Account {acc.account_number}")
            choice = int(input("Select account to view balance (number): ")) - 1
            if 0 <= choice < len(user.accounts):
                selected_acc = user.accounts[choice]
                print(f"Account {selected_acc.account_number} balance: ${selected_acc.balance}")
            else:
                print("Invalid selection.")
                break
            # Main menu loop for user actions
            while True:
                print("\nOptions:")
                print("1. Deposit funds")
                print("2. Withdraw funds")
                print("3. Create new account")
                print("4. Transfer between your accounts")
                print("5. Transfer to another user's account")
                print("6. View transaction history")
                print("7. Update personal information (PIN)")
                print("8. View update history")
                print("9. Exit")
                action = input("Select an option (1-9): ")
                if action == '1':
                    deposit_funds(user)
                elif action == '2':
                    withdraw_funds(user)
                elif action == '3':
                    create_new_account(user)
                elif action == '4':
                    transfer_between_own_accounts(user)
                elif action == '5':
                    transfer_to_other_user(user)
                elif action == '6':
                    view_transaction_history(user)
                elif action == '7':
                    update_personal_info(user)
                elif action == '8':
                    view_update_history(user)
                elif action == '9':
                    print("Goodbye!")
                    break
                else:
                    print("Invalid option.")
            break
        else:
            print(msg)
            if msg and "locked" in msg.lower():
                break

if __name__ == "__main__":
    # DO NOT overwrite transaction_log here!
    # transaction_log = [
    #     # Example data structure
    #     # {"account_number": "1001", "user": "alice", "datetime": "2024-06-24 10:00:00", "type": "+Deposit", "amount": 0.25},
    #     # ...
    # ]

    # Build a DataFrame from the transaction log
    df = pd.DataFrame(transaction_log)

    if not df.empty and 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        # Sort by datetime
        df = df.sort_values('datetime')

        # Get unique users (or select specific users)
        unique_users = df['user'].unique()

        # Prepare a dict to track balances over time for each account
        account_balances = defaultdict(list)
        account_dates = defaultdict(list)
        current_balances = {}

        for _, row in df.iterrows():
            acc = row['account_number']
            user = row['user']
            date = row['datetime']
            amt = row['amount']
            typ = row['type']
            # Update balance
            prev = current_balances.get(acc, 0)
            if typ.startswith('+'):
                new_bal = prev + amt
            elif typ.startswith('-'):
                new_bal = prev - amt
            else:
                new_bal = prev  # For other types, adjust as needed
            current_balances[acc] = new_bal
            account_balances[acc].append(new_bal)
            account_dates[acc].append(date)

        # Plot for at least 3 accounts (or users)
        plt.figure(figsize=(10, 6))
        plotted = 0
        for acc in account_balances:
            if plotted >= 3:
                break
            plt.plot(account_dates[acc], account_balances[acc], marker='o', label=f'Account {acc}')
            plotted += 1

        plt.xlabel('Date')
        plt.ylabel('Balance')
        plt.title('User Account Activity Over Time')
        plt.legend()
        plt.tight_layout()
        plt.show()

        # --- System-Wide Daily Transaction Volume Bar Chart ---
        # Classify transaction types
        def classify_type(tx_type):
            if "Deposit" in tx_type:
                return "Deposit"
            elif "Withdrawal" in tx_type:
                return "Withdrawal"
            elif "Transfer" in tx_type:
                return "Transfer"
            else:
                return "Other"

        df['date'] = df['datetime'].dt.date
        df['tx_class'] = df['type'].apply(classify_type)

        # Aggregate daily transaction counts by type
        daily_counts = df.groupby(['date', 'tx_class']).size().unstack(fill_value=0)

        # Plot stacked bar chart
        daily_counts.plot(kind='bar', stacked=True, figsize=(10,6))
        plt.xlabel('Date')
        plt.ylabel('Number of Transactions')
        plt.title('Daily Transaction Volume')
        plt.legend(title='Transaction Type')
        plt.tight_layout()
        plt.show()

        # --- Distribution of Account Balances Histogram ---
        # Get the latest balance for each account from your current_balances dict
        balances = list(current_balances.values())

        # Define bins and labels
        balance_bins = [0, 1, 5, 10, 50, 100, float('inf')]
        balance_labels = ['0-0.99', '1-4.99', '5-9.99', '10-49.99', '50-99.99', '>100']

        plt.figure(figsize=(10, 6))
        plt.hist(balances, bins=balance_bins, edgecolor='black')
        plt.xlabel('Balance Range')
        plt.ylabel('Number of Accounts')
        plt.title('Distribution of Account Balances')
        plt.xticks(
            [(balance_bins[i] + balance_bins[i+1])/2 for i in range(len(balance_bins)-1)],
            balance_labels, rotation=45
        )
        plt.tight_layout()
        plt.show()
    else:
        print("No transaction data available for visualization.")

    main()