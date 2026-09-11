class ExpenseManager:
    def __init__(self):
        self.expenses=[]



    def add_expense(self, expense):
        self.expenses.append(expense)

    def get_expenses(self):
        return self.expenses


    def get__amount(self):
        return self.__amount


    def set__amount(self,amount):
        if amount<=0:
            return "Amount should be greater than 0"
        self.__amount=amount
        return "amount update successfully"


    def get_details(self):
        return self.__title, self.__category

    def set_details(self,title,category):
        if title=="" or category=="":
            return "Title and category should not be empty"
        self.__title=title    
        self.__category=category
        return "title and category update successfully"
    
    


    def show_expenses(self):
        for i in self.expenses:
            title, category = i.get_details()
            print(title,i.get_amount(),category)
    def total_expense(self):
        total=0
        for i in self.expenses:
            total+=i.get_amount()
        return f"Total expense: {total}"



