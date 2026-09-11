class expense:
    def __init__(self, title, amount, category):
        self.__title=title
        self.__amount=amount
        self.__category=category

    
    def get_amount(self):
        return self.__amount


    def set_amount(self,amount):
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
        