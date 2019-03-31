# Author: Dahir Muhammad Dahir
# Date: 20th-03-2019

from connection import MakeConnection
import hashlib
import re
from datetime import datetime, timedelta


class Account(MakeConnection):
    def __init__(self, userAccountNumber, userPIN):
        MakeConnection.__init__(self)
        self.validPINPattern = re.compile(r"\d{4}\b")
        self.validAccountNumberPattern = re.compile(r"3\d{9}\b")
        self.validAmountPattern = re.compile(r"\d{2,}\.{0,1}\d{0,}$")
        self.timeFormat = r"%Y-%m-%d %H:%M:%S"
        self._24hours = timedelta(hours=24)
        self.userAccountNumber = userAccountNumber
        self.userPIN = userPIN

    def openNewAccount(self):
        initialDepositAmount = 5000
        accountType = self.chooseAccountType()
        if accountType:
            lastWithdrawalDate = "0000-00-00 00:00:00"
            overdraftAmount = 0
            accountNumber = self.getAccountNumber()
            atmPIN = self.createATMPin()
            accountStatus = "clear"
            lastDepositTime = datetime.now().strftime(self.timeFormat)

            createAccountQuery = "INSERT INTO accounts (account_number, pin, balance, account_type, account_status, last_deposit_date, last_withdrawal_date, overdraft_amount) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                accountNumber, atmPIN, initialDepositAmount, accountType, accountStatus,
                lastDepositTime, lastWithdrawalDate, overdraftAmount)

            self.mycursor.execute(createAccountQuery)  # Execute the query
            self.connection.commit()  # Commit it

            if self.mycursor.rowcount > 0:
                print("\n===[ Congratulation Your Account has been created Successfully ]===\n")
                print("===[ Your Account Number is: {} ]===".format(accountNumber))
                print("\n===[ And Please Don't Forget Your Secret PIN ]===\n")
                # self.updateAccountNumberRecord(accountNumber)
        else:
            print("===[ Sorry, We are unable to open your account right now, please check back later ]===")

    @staticmethod
    def chooseAccountType():
        while True:
            print("\n===[ We are Glad You Are Here, You will Need N5,000 to OPEN a New Account ]===\n")
            askPermission = input("\nWould You Like to Proceed?\n[1] Yes\n[2] No\n\n")
            if askPermission == "2":
                return
            elif askPermission == "1":
                accountType = input(
                    "\nSelect Account Type:\n[1] Savings (No Overdraft)\n[2] Checkings (with Overdraft)\n\n")
                if accountType == "1":
                    return "savings"
                elif accountType == "2":
                    return "checkings"
                else:
                    print("Invalid Entry...")
                    return
            else:
                print("Invalid Entry...Check Your Input...")

    def getAccountNumber(self):
        getNumQuery = "SELECT account_number FROM accounts"
        self.mycursor.execute(getNumQuery)

        lastAccountNumber = 0
        for i in self.mycursor:
            lastAccountNumber = i

        return int(lastAccountNumber[0]) + 1

    def validatePIN(self, pin):
        if re.match(self.validPINPattern, pin):
            return True

    def validateAccountNumber(self, accountNumber):
        if re.match(self.validAccountNumberPattern, accountNumber):
            return True

    def validateAmount(self, amount):
        if re.match(self.validAmountPattern, amount):
            return True

    @staticmethod
    def hashPIN(pin):
        return hashlib.sha256(pin.encode("utf-8")).hexdigest()

    def createATMPin(self):
        while True:
            enterPIN = input("\nPlease Choose Your New secret PIN [ 4 digits only]:\n\n")
            confirmPIN = input("Re-Enter PIN to confirm:\n\n")
            if enterPIN == confirmPIN:
                if self.validatePIN(enterPIN):
                    return self.hashPIN(enterPIN)
                else:
                    print("Please 4 digits PIN only...Try Again")
            else:
                print("Pin Mismatch...Try Again..")

    def changePIN(self):
        """Allow users to change their PIN by providing their old PIN and
        the new one"""
        if not self.validateAccountNumber(self.userAccountNumber):
            print("\nInvalid Account was provided...\n")
            return
        oldPIN = input("\n===[ Please enter your current PIN ]===\n\n")
        oldPINHash = self.hashPIN(oldPIN)
        newPIN = self.createATMPin()

        getCurrentPinHashQuery = "SELECT pin FROM accounts WHERE account_number='{}'".format(
            self.userAccountNumber)
        self.mycursor.execute(getCurrentPinHashQuery)
        currentPINHash = self.mycursor.fetchone()[0]

        if self.mycursor.rowcount > 0:
            if currentPINHash == oldPINHash:
                updateNewPINQuery = "UPDATE accounts SET pin='{}' WHERE account_number='{}'".format(newPIN,
                                                                                                         self.userAccountNumber)

                self.mycursor.execute(updateNewPINQuery)
                if self.mycursor.rowcount > 0:
                    self.connection.commit()
                    print("Your PIN has been changed successfully.\n")

                else:
                    print("Sorry we couldn't change your pin...check back later")

            else:
                print("the old pin you entered is incorrect...bye\n")

        else:
            print(
                "We couldn't find any record with the account number you specify...Are you sure You have an account with us?\n")

    def cashWithdrawal(self):
        """Allow account holders to withdraw money from their account"""
        print("\n===[ AirRayz Cash Withdrawal ]===\n")
        targetAmount = input("Enter the amount you wish to withdraw:\n\n")
        if self.debitAccount(self.userAccountNumber, targetAmount):
            print("\n===[ Withdrawal successful, Please take your cash]===\n")
        else:
            print("\nCouldn't withdraw at the moment, please check back later")

    def cashDeposit(self):
        """Allow account holders to deposit money to their own account
        or to other account holders"""
        print("\n===[ AirRayz Cash Deposit ]===\n")
        targetAccountNumber = input("Enter the account number you want to deposit to:\n\n")
        targetAmount = input("Enter the amount you wish to deposit:\n\n")
        if self.creditAccount(targetAccountNumber, targetAmount):
            print("===[ Cash Deposit Successful ]===")
        else:
            print("Cash deposit failed check back later")

    def transferFunds(self):
        """transfer funds to other users, requires the account number of the receiver
        the method also attempt reversal of funds in case of failed transfer"""

        print("\n===[ AirRayz Funds Transfer]===\n")
        currentBalance = self.accountBalance()
        print("\nYour Account Balance is: {}\n".format(currentBalance))
        targetAccountNumber = input("\nEnter Account Number You want to transfer to:\n\n")
        targetTransferAmount = input("\nEnter Amount you want to transfer:\n\n")

        if self.debitAccount(self.userAccountNumber, targetTransferAmount):
            if self.creditAccount(targetAccountNumber, targetTransferAmount):
                print("===[ transfer completed successfully ]===\n")
            else:
                print("Transfer failed...check back later\n")
        else:
            print("Unable to process your transfer...please check back later.\n")

    def accountBalance(self, accountNumber=""):
        """Get the current user account balance, if the optional account number
        argument is specified, the method retrieves the balance for the
        specified account number"""
        if accountNumber:
            getCurrentBalanceQuery = "SELECT balance FROM accounts WHERE account_number='{}'".format(accountNumber)
        else:
            getCurrentBalanceQuery = "SELECT balance FROM accounts WHERE account_number='{}'".format(
                self.userAccountNumber)

        self.mycursor.execute(getCurrentBalanceQuery)
        currentBalance = self.mycursor.fetchone()

        if self.mycursor.rowcount > 0:
            return currentBalance[0]
        else:
            print("We were unable to retrieve your account balance please check back later\n")

    def creditAccount(self, accountNumber, Amount):
        if self.validateAccountNumber(accountNumber):
            if self.validateAmount(Amount):
                currentAccountBalance = self.accountBalance(accountNumber)

                creditQuery = "UPDATE accounts SET balance='{}' WHERE account_number='{}'".format(
                    int(currentAccountBalance) + int(Amount), accountNumber)

                self.mycursor.execute(creditQuery)
                if self.mycursor.rowcount > 0:
                    self.connection.commit()
                    return True
                else:
                    return False
            else:
                print("\nInvalid Amount Entered.\n")
                return False
        else:
            print("\nAccount Number is Invalid\n")
            return False

    def debitAccount(self, accountNumber, Amount):
        if self.validateAccountNumber(accountNumber):
            if self.validateAmount(Amount):
                currentAccountBalance = self.accountBalance(accountNumber)

                if int(currentAccountBalance) >= int(Amount):
                    creditQuery = "UPDATE accounts SET balance='{}' WHERE account_number='{}'".format(
                        int(currentAccountBalance) - int(Amount), accountNumber)

                    self.mycursor.execute(creditQuery)
                    if self.mycursor.rowcount > 0:
                        self.connection.commit()
                        return True
                    else:
                        return False
                else:
                    print("\nInsufficient Funds...\n")
                    return False
            else:
                print("\nInvalid Amount Entered.\n")
                return False
        else:
            print("\nAccount Number is Invalid\n")
            return False
