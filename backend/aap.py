from expenses import Expense
from expense_manager import ExpenseManager



p1=Expense("movie",670,"entertainment")
p2=Expense("food",500,"grocery")
manager=ExpenseManager()
manager.add_expense(p1)
manager.add_expense(p2)

manager.show_expenses()
print(manager.total_expense())
print(manager.delete_expense("movie"))
manager.show_expenses()
print(manager.update_expense("food"))
manager.show_expenses()

