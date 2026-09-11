"""This module defines the Expense class, which represents an individual expense with a title, amount, and category."""
class Expense:

    """Class to represent an individual expense."""

    def __init__(self, title, amount, category):
        self.__title=title
        self.__amount=amount
        self.__category=category

    
    def get_amount(self):
        """Get the amount of the expense."""
        return self.__amount


    def set_amount(self,amount):
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
        