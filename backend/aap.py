from expenses import expense
from expense_manager import ExpenseManager



p1=expense("movie",670,"entertainment")
p2=expense("food",500,"grocery")
manager=ExpenseManager()
manager.add_expense(p1)
manager.add_expense(p2)
manager.show_expenses()
print(manager.total_expense())

