# **Task1**
# Read a text file and create a dictionary of character frequencies. Use a single for loop to calculate each character's frequency without any built-in functionalities.
with open('textfile.txt', 'r') as text:
    content = text.read()  # Corrected spelling from 'contant' to 'content'
frequency = {}

for char in content:  # Corrected spelling from 'contant' to 'content'
    frequency[char] = frequency.get(char, 0) + 1
print(frequency)

# **Task2**
#Sort a list without using any built-in functions.
def sort_list(unsorted_list):
    n = len(unsorted_list)
    for i in range(n):
        for j in range(0, n - i - 1):
            if unsorted_list[j] > unsorted_list[j + 1]:
                # Swap elements
                unsorted_list[j], unsorted_list[j + 1] = unsorted_list[j + 1], unsorted_list[j]
    print(unsorted_list)

# Initialize the list to be sorted
unsorted_numbers = [30, 5, -10, 15, 12, -26]
sort_list(unsorted_numbers)

# **Task3**
# Difference between sort and sorted function
# *Sort()*
# It is a method of list objects.
# It modifies the list in place and does not return a new list.
# Syntax: list.sort()

def sort_function(list):
    list.sort()
    print(list)
list = [10, 12, -15, -30, 79, 5]
sort_function(list)

# *Sorted()*
# It is a built-in function that can take any iterable (like lists, tuples, strings) and returns a new sorted list.
# It does not modify the original iterable.
# Syntax: sorted(iterable)

def sort_iterable(iterable):
    sorted_list = sorted(iterable)
    print(sorted_list)

my_touple = (10, 12, -15, -30, 79, 5)
sort_iterable(my_touple)

my_list = [10, 12, -15, -30, 79, 5]
sort_iterable(my_list)

my_string = 'lkjkjhvhcghd'
sort_iterable(my_string)

# **Lambda function**
# Anonymous: Lambda functions don’t require a name (unlike regular functions defined using def).
# Single Expression: They can only contain a single expression. You cannot include statements or multiple expressions.
# Quick and Easy: They are often used for short-term tasks or operations where a full function definition would be unnecessary.
# lambda arguments: expression

add_lambda = lambda a, b : a+b
add_lambda(6, 10)

numbrs = [1, 3, 5, 9]
doubled = list(map(lambda a : a * 2 , numbrs))
print(doubled)

numbrs = [1, 2, 3, 4, 5, 6]
Even_numbers = list(filter(lambda a : a % 2 == 0, numbrs))
print(Even_numbers)


# **dunder methods**
# *1. __init__ Method*
# Purpose: The __init__ method is a constructor that initializes a new object when it is created. It is called automatically when an object of a class is instantiated.
# Usage: It sets up initial values for the object's attributes.
# Signature: It typically takes self as its first argument, followed by any other parameters needed for initialization.

class BankAccount:
    def __init__(self, name , initial_balance):
        self.name = name
        self.balance = initial_balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            print('Deposit successful. Updated balance is : ', self.balance)
    def withdraw(self, amount):
        if self.balance != 0 and amount <= self.balance:
            self.balance -= amount
            print('Withdraw Successful. New balance is :', self.balance)
    def check_balance(self):
        print('Your account balance is : ', self.balance)
    def get_accountholder_name(self):
        print('AccountHolder Name is : ', self.name)

def main():
    print(' ABC Bank')

    name = input('Enter accountHolder Name')
    initial_balance = int(input('Enter your initial balance'))
    Account = BankAccount(name , initial_balance)

    print('Enter 1 to for cash deposit')
    print('Enter 2 to for cash withdraw')
    print('Enter 3 to check accout balance')
    print('Enter 4 to exit')

    choice = int(input('Enter your choice:'))
    if choice == 1:
        amount = int(input('Enter amount to deposit:'))
        Account.deposit(amount)
    if choice == 2:
        amount = int(input('Enter amount to withdraw:'))
        Account.withdraw(amount)
    if choice == 3:
        Account.check_balance()
    if choice == 4:
        amount = int(input('Enter amount to deposit:'))
        Account.deposit(amount)
if __name__ == '__main__':
    main()
