
"""Manage and organize expenses."""
class ExpenseManager:

    """Class to manage a list of expenses."""
    def __init__(self):
        self.expenses=[]



    def add_expense(self, expense):
        """Add a new expense to the list."""
        self.expenses.append(expense)

    def get_expenses(self):
        """Get the list of all expenses."""
        return self.expenses


    def get__amount(self):

        """Get the amount of the expense."""
        return self.__amount


    def set__amount(self,amount):

        """Set the amount of the expense."""
        if amount<=0:
            return "Amount should be greater than 0"
        self.__amount=amount
        return "amount update successfully"


    def get_details(self):

        """Get the title and category of the expense."""
        return self.__title, self.__category

    def set_details(self,title,category):

        """Set the title and category of the expense."""
        if title=="" or category=="":
            return "Title and category should not be empty"
        self.__title=title    
        self.__category=category
        return "title and category update successfully"
    
    


    def show_expenses(self):

        """Display all the expenses."""
        for i in self.expenses:
            title, category = i.get_details()
            print(title,i.get_amount(),category)

    def total_expense(self):

        """Calculate the total expense amount."""
        total=0
        for i in self.expenses:
            total+=i.get_amount()
        return f"Total expense: {total}"


    def delete_expense(self,title):
        """Delete an existing expense using its title."""
        for i, expense in enumerate(self.expenses):
            if title==expense.get_details()[0]:
                self.expenses.pop(i)
                return "Expense deleted successfully"
        return "Expense not found"
    def update_expense(self,title):

        """Update an existing expense using its title."""

        try:
            for i,exp in enumerate(self.expenses):
                if title==exp.get_details()[0]:
                    new_title=input("enter new title: ")
                    new_category=input("enter new category: ")
                    new_amount=int(input("enter new amount: ")) 
                    result=self.expenses[i].set_amount(new_amount)
                    
                    if result == "amount update successfully":
                        details=self.expenses[i].set_details(new_title, new_category)
                        if details == "title and category update successfully":
                            return "Expense updated successfully"
                        return details
                    return result  
        except ValueError:
               return "Invalid input. Please enter a valid amount"
        return "Expense not found"



