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
        self.initialDepositAmount = 5000
        self.accountType = self.chooseAccountType()
        if self.accountType:
            self.lastWithdrawalDate = "0000-00-00 00:00:00"
            self.overdraftAmount = 0
            self.accountNumber = self.getAccountNumber()
            self.atmPIN = self.createATMPin()
            self.accountStatus = "clear"
            self.lastDepositTime = datetime.now().strftime(self.timeFormat)
            
            self.createAccountQuery = "INSERT INTO accounts (account_number, pin, balance, account_type, account_status, last_deposit_date, last_withdrawal_date, overdraft_amount) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(self.accountNumber, self.atmPIN, self.initialDepositAmount,self.accountType, self.accountStatus, self.lastDepositTime, self.lastWithdrawalDate, self.overdraftAmount)

            self.mycursor.execute(self.createAccountQuery) # Execute the query
            self.connection.commit() # Commit it

            if self.mycursor.rowcount > 0:
                print("\n===[ Congratulation Your Account has been created Successfully ]===\n")
                print("===[ Your Account Number is: {} ]===".format(self.accountNumber))
                print("\n===[ And Please Don't Forget Your Secret PIN ]===\n")
                #self.updateAccountNumberRecord(self.accountNumber)
        else:
            print("===[ Sorry, We are unable to open your account right now, please check back later ]===")
    
    
    def chooseAccountType(self):
        while True:
            print("\n===[ We are Glad You Are Here, You will Need N5,000 to OPEN a New Account ]===\n")
            self.askPermission = input("\nWould You Like to Proceed?\n[1] Yes\n[2] No\n\n")
            if self.askPermission == "2":
                return
            elif self.askPermission == "1":
                self.accountType = input("\nSelect Account Type:\n[1] Savings (No Overdraft)\n[2] Checkings (with Overdraft)\n\n")
                if self.accountType == "1":
                    return "savings"
                elif self.accountType == "2":
                    return "checkings"
                else:
                    print("Invalid Entry...")
                    return
            else:
                print("Invalid Entry...Check Your Input...")
    

    def getAccountNumber(self):
        self.getNumQuery = "SELECT account_number FROM accounts"
        self.mycursor.execute(self.getNumQuery)

        for i in self.mycursor:
            self.lastAccountNumber = i

        return int(self.lastAccountNumber[0]) + 1
    

    def validatePIN(self, pin):
        if re.match(self.validPINPattern, pin):
            return True
    

    def validateAccountNumber(self, accountNumber):
        if re.match(self.validAccountNumberPattern, accountNumber):
            return True
    

    def validateAmount(self, amount):
        if re.match(self.validAmountPattern, amount):
            return True
    

    def hashPIN(self, pin):
        return hashlib.sha256(pin.encode("utf-8")).hexdigest()


    def createATMPin(self):
        while True:
            self.enterPIN = input("\nPlease Choose Your New secret PIN [ 4 digits only]:\n\n")
            self.confirmPIN = input("Re-Enter PIN to confirm:\n\n")
            if self.enterPIN == self.confirmPIN:
                if self.validatePIN(self.enterPIN):
                    return self.hashPIN(self.enterPIN)
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
        self.oldPIN = input("\n===[ Please enter your current PIN ]===\n\n")
        self.oldPINHash = self.hashPIN(self.oldPIN)
        self.newPIN = self.createATMPin()

        self.getCurrentPinHashQuery = "SELECT pin FROM accounts WHERE account_number='{}'".format(self.userAccountNumber)
        self.mycursor.execute(self.getCurrentPinHashQuery)
        self.currentPINHash = self.mycursor.fetchone()[0]

        if self.mycursor.rowcount > 0:
            if self.currentPINHash == self.oldPINHash:
                self.updateNewPINQuery = "UPDATE accounts SET pin='{}' WHERE account_number='{}'".format(self.newPIN, self.userAccountNumber)

                self.mycursor.execute(self.updateNewPINQuery)
                if self.mycursor.rowcount > 0:
                    self.connection.commit()
                    print("Your PIN has been changed successfully.\n")
                
                else:
                    print("Sorry we couldn't change your pin...check back later")
            
            else:
                print("the old pin you entered is incorrect...bye\n")

        else:
            print("We couldn't find any record with the account number you specify...Are you sure You have an account with us?\n")

    
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
        self.currentBalance = self.accountBalance()
        print("\nYour Account Balance is: {}\n".format(self.currentBalance))
        self.targetAccountNumber = input("\nEnter Account Number You want to transfer to:\n\n")
        self.targetTransferAmount = input("\nEnter Amount you want to transfer:\n\n")

        if self.debitAccount(self.userAccountNumber, self.targetTransferAmount):
            if self.creditAccount(self.targetAccountNumber, self.targetTransferAmount):
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
            self.getCurrentBalanceQuery = "SELECT balance FROM accounts WHERE account_number='{}'".format(accountNumber)
        else:
            self.getCurrentBalanceQuery = "SELECT balance FROM accounts WHERE account_number='{}'".format(self.userAccountNumber)

        self.mycursor.execute(self.getCurrentBalanceQuery)
        currentBalance = self.mycursor.fetchone()

        if self.mycursor.rowcount > 0:
            return currentBalance[0]
        else:
            print("We were unable to retrieve your account balance please check back later\n")
    

    def creditAccount(self, accountNumber, Amount):
        if self.validateAccountNumber(accountNumber):
            if self.validateAmount(Amount):
                currentAccountBalance = self.accountBalance(accountNumber)

                self.creditQuery = "UPDATE accounts SET balance='{}' WHERE account_number='{}'".format(int(currentAccountBalance) + int(Amount), accountNumber)

                self.mycursor.execute(self.creditQuery)
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
                    self.creditQuery = "UPDATE accounts SET balance='{}' WHERE account_number='{}'".format(int(currentAccountBalance) - int(Amount), accountNumber)

                    self.mycursor.execute(self.creditQuery)
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