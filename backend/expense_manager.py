import json
import os

from expenses import Expense


class ExpenseManager:

    def __init__(self):
        self.expenses = []


    def load_expenses(self):

        file_path = os.path.join(
            os.path.dirname(__file__),
            "expenses.json"
        )

        with open(file_path, "r") as file:
            data = json.load(file)

        for item in data:

            expense = Expense(
                item["title"],
                item["amount"],
                item["category"]
            )

            self.expenses.append(expense)


    def add_expense(self, expense):

        self.expenses.append(expense)


    def get_expenses(self):

        return self.expenses


    def delete_expense(self, title):

        for expense in self.expenses:

            expense_title, category = expense.get_details()

            if title == expense_title:

                self.expenses.remove(expense)

                return "Expense deleted successfully"

        return "Expense not found"


    # ================= UPDATE =================

    def update_expense(
        self,
        old_title,
        new_title,
        new_amount,
        new_category
    ):

        for expense in self.expenses:

            title, category = expense.get_details()

            if title == old_title:

                result = expense.set_amount(new_amount)

                if result != "amount update successfully":
                    return result


                result = expense.set_details(
                    new_title,
                    new_category
                )

                if result != "title and category update successfully":
                    return result


                return "Expense updated successfully"


        return "Expense not found"


    def search_expense(self, title):

        for expense in self.expenses:

            expense_title, category = expense.get_details()

            if title == expense_title:

                return (
                    f"Expense found: {expense_title}, "
                    f"Amount: {expense.get_amount()}, "
                    f"Category: {category}"
                )

        return "Expense not found"


    def total_expense(self):

        total = 0

        for expense in self.expenses:

            total += expense.get_amount()

        return total


    def save_expenses(self):

        data = []

        for expense in self.expenses:

            title, category = expense.get_details()

            data.append({
                "title": title,
                "amount": expense.get_amount(),
                "category": category
            })


        file_path = os.path.join(
            os.path.dirname(__file__),
            "expenses.json"
        )

        with open(file_path, "w") as file:

            json.dump(
                data,
                file,
                indent=4
            )