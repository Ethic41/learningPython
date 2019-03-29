# Author: Dahir Muhammad Dahir
# Date: 23th-03-2019

from bank import Account

class ATM(Account):
    def __init__(self):
        print("\n===[ Welcome To AirRayz Non-Profit Bank [lolz] ]===\n")
        self.userAccountNumber = input("\nPlease Enter Your Account Number:\n\n")
        self.userPIN = input("\nPlease Enter Your Secret PIN:\n\n")
        Account.__init__(self, self.userAccountNumber, self.userPIN)
    

    def accessATM(self):
        if self.authenticated():
            while(True):
                print("Welcome {}, What would you like to do today?\n".format(self.userAccountNumber))
                self.action = input("\n[1] Withdraw CASH        [2] Deposit CASH\n[3] Open New Account     [4] Transfer Funds\n[5] Change PIN           [6] Check Balance\n[7] Exit\n\n")
                
                if self.action == "1":
                    self.cashWithdrawal()
                
                elif self.action == "2":
                    self.cashDeposit()
                
                elif self.action == "3":
                    self.openNewAccount()

                elif self.action == "4":
                    self.transferFunds()
                
                elif self.action == "5":
                    self.changePIN()
                
                elif self.action == "6":
                    print("\n===[ Your Account Balance is: {}]===\n\n".format(self.accountBalance()))
                
                elif self.action == "7":
                    print("\n==={ Thank You For Banking With Us }===")
                    exit()
                    
                else:
                    print("Incorrect Choice...Please choose between [1 - 5]")
    

    def authenticated(self):
        if self.validateAccountNumber(self.userAccountNumber) and self.validatePIN(self.userPIN):
            self.authenticateQuery = "SELECT account_number FROM accounts WHERE account_number='{}' AND pin='{}'".format(self.userAccountNumber, self.hashPIN(self.userPIN))

            self.mycursor.execute(self.authenticateQuery)
            self.mycursor.fetchone()

            if self.mycursor.rowcount > 0:
                return True
            
            else:
                print("Incorrect Account Number or PIN entered\n")
                return False
        else:
            print("Incorrect Account Number or Pin entered...\n")
            return False
