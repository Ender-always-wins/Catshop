from tabulate import tabulate
import matplotlib.pyplot as plt
import pyrebase

myconfig = {'apiKey': "AIzaSyDN3sMAj-uTrhMe_d1Y9zqdhN1o_XQNTo0",
    'authDomain': "flipazon-cd07b.firebaseapp.com",
    'databaseURL': "https://flipazon-cd07b-default-rtdb.asia-southeast1.firebasedatabase.app",
    'projectId': "flipazon-cd07b",
    'storageBucket': "flipazon-cd07b.appspot.com",
    "messagingSenderId": "142613116213",
    'appId': "1:142613116213:web:b4f34d78539c3d7e0e487c",
    'measurementId': "G-DZP9ZSNMYB"}

firebase = pyrebase.initialize_app(myconfig)

db = firebase.database()

class Customer:
    def __init__(self, name):
        self.name = name
        self.cart = db.child("customers").child(name).child("cart").get().val()

    def set_cart(self):
        self.cart = db.child("customers").child(self.name).child("cart").get().val()

    def show_cart(self):
        data = db.child("products").get().val()
        temp = [[0, "Name", "Quantity", "Price by piece", "Total price"]]
        i = 0
        self.set_cart()
        for a, b in self.cart.items():
            if i != 0:
                temp.append([i, a, b, data[a]["price"], data[a]["price"]*b])
            i += 1
        print(tabulate(temp))

    def add_to_cart(self, item, quantity):
        self.set_cart()
        if item not in self.cart:
            db.child("customers").child(self.name).child("cart").child(item).set(quantity)
        else:
            q1 = db.child("customers").child(self.name).child("cart").child(item).get().val() + quantity
            db.child("customers").child(self.name).child("cart").child(item).set(q1)

    def remove_from_cart(self, item, quantity):
        self.set_cart()
        if item in self.cart:
            q1 = db.child("customers").child(self.name).child("cart").child(item).get().val() 
            if quantity >= q1:
                db.child("customers").child(self.name).child("cart").child(item).set(0)
            else:
                db.child("customers").child(self.name).child("cart").child(item).set(q1-quantity)
        else:
            print("Item not in cart")

    def checkout(self):
        user = db.child("customers").child(self.name)
        if user.child("budget").get().val() > 0:
            self.set_cart()
            amount = 0
            for name, val in self.cart.items():
                if name != "None":
                    if val < db.child("products").child(name).child("stock").get().val():
                        price = db.child("products").child(name).child("price").get().val()
                        cost = db.child("products").child(name).child("cost").get().val()
                        stock = db.child("products").child(name).child("stock").get().val()
                        seller_name = db.child("products").child(name).child("seller").get().val()
                        seller = db.child("sellers").child(seller_name).get().val()
                        units_sold = seller["products"][name]["units_sold"]
                        profit = seller["profit"]
                        
                        db.child("products").child(name).child("stock").set(stock - val)
                        db.child("sellers").child(seller_name).child("products").child(name).child("stock").set(stock - val)
                        db.child("sellers").child(seller_name).child("products").child(name).child("units_sold").set(units_sold + val)
                        db.child("sellers").child(seller_name).child("profit").set(profit + val*(price-cost))
                        amount += val*(price-cost)

                    else:
                        price = db.child("products").child(name).child("price").get().val()
                        cost = db.child("products").child(name).child("cost").get().val()
                        stock = db.child("products").child(name).child("stock").get().val()
                        seller_name = db.child("products").child(name).child("seller").get().val()
                        seller = db.child("sellers").child(seller_name).get().val()
                        units_sold = seller["products"][name]["units_sold"]
                        profit = seller["profit"]

                        db.child("sellers").child(seller_name).child("products").child(name).child("units_sold").set(units_sold + stock)
                        db.child("sellers").child(seller_name).child("products").child(name).child("stock").set(0)
                        db.child("sellers").child(seller_name).child("profit").set(profit + stock*(price-cost))
                        db.child("products").child(name).child("stock").set(0)
                        amount += stock*(price-cost)

            budget = db.child("customers").child(self.name).child("budget").get().val()
            db.child("customers").child(self.name).child("budget").set(budget - amount)
            print(f"Debitting {amount} from your account")
            db.child("customers").child(self.name).child("cart").set({"None" :-1})
        else:
            print("Negative funds!")

for k in range(1):
    a = ''
    while a.lower() not in ("c", "customer", "s", "seller"):
        a = input("Are you a customer(c) or seller(s)?: ")
    a = a.lower()

    ls = ""
    while ls.lower() not in ("l", "s", "login", "signup"):
        ls = input("Do you want to login(l) or signup(s)?: ")
    ls = ls.lower()

    if ls in ("l", "login"):
        if a in ("c", "customer"):
            
            while True:
                username = input("Enter your username please: ")
                if username in db.child("customers").get().val():
                    break
                else:
                    print("Wrong username")

            for k in range(3):
                password = input("Enter you password: ")
                if password == db.child("customers").child(username).child("password").get().val():
                    break
            else:
                print("Too many failed attempts, Retry again later.")
                break

            print("Login successful!")

        elif a in ("s", "seller"):
            username = input("Enter your username: ")
            while username not in db.child("sellers").get().val():
                print("invalid username")
                username = input("Enter your username: ")
            for k in range(3):
                password = input("Enter your password: ")
                if password == db.child("customers").child(username).child("password").get().val():
                    break
            else:
                print("Too many failed attempts, Retry again later.")
                break

    elif ls in ("s", "signup"):
        if a in ("c", "customer"):
            while True:
                username = input("Enter your username please: ")
                if username in db.child("customers").get().val():
                    print("Sorry username is taken")
                else:
                    break
            password = input("Create a strong password: ")
            budget = input("Enter your budget: ")
            db.child("customers").child(username).set({"password" : password, "budget" : budget, "cart": {"None": -1}})
        else:
            username = input("Enter the username in your customer account: ")
            if username in db.child("customers").get().val() and username not in db.child("sellers").get().val():
                print("Customer account found")
                password = input("Enter your password: ")
                if password == db.child("customers").child(username).child("password").get().val():
                    db.child("sellers").child(username).set({"products": {"None":-1}, "profit": 0}) 
                    print("Succesfully created your seller account!")
                else:
                    print("Access denied")
                    break
            else:
                print("Either you dont have a customer account or you already have a seller account!")
                break

    if a in ("c", "customer"):
        current_cust = Customer(username)

        while True:

            act = input("Do you want to checkout(c), manipulate your cart(m), set your budget(b) or quit(q): ")

            if act.lower() in ("q", "quit"):
                break

            elif act.lower() in ("m", "manipulate", "cart"):
                current_cust.show_cart()

                while True:

                    what = input(
                        "Do you want to add stuff to your cart(a), remove stuff from your cart(r), or quit(q): ")

                    if what.lower() in ("q", "quit"):
                        break

                    elif what.lower() in ("a", "add"):
                        print("This is a list of available items: ")
                        shop = [["S. No.", "Name", "Price"]]
                        i = 1
                        for item in db.child("products").get().val():
                            shop.append([i, item, db.child("products").child(item).child("price").get().val()])
                            i += 1
                        print(tabulate(shop))
                        nums = input("Enter name and quantity of item you want to add to cart seperated by a space if you want multiple items seperate the name-quantity pairs by a comma: ").split(",")
                        names = db.child("products").get().val()
                        for n_q in nums:
                            name, quantity = n_q.split()
                            if name.lower() in names:
                                current_cust.add_to_cart(name.lower(), int(quantity))
                            else:
                                print(f"{name} is not in the list of available items!")
                        print('Your updated cart is: ')
                        current_cust.show_cart()

                    elif what.lower() in ("r", "remove"):
                        print("This is your cart")
                        current_cust.show_cart()
                        a = input("Enter name and quantity of the item you want to remove seperated by a space, if you want to remove multiple items split them with a comma!: ")
                        mylist = [(info.split()[0].lower(), int(info.split()[1])) for info in a.split(",")]
                        for a, b in mylist:
                            current_cust.remove_from_cart(a, b)
                        print("This is your updated cart")
                        current_cust.show_cart()

            elif act.lower() in ("b", "budget", "u", "set"):
                budget = int(input("Enter your new budget: "))
                confirmation = input("Confirm your password: ")
                if confirmation == db.child("customers").child(username).child("password").get().val():
                    print(f'Adding {budget - db.child("customers").child(username).child("budget").get().val()} to your account' 
                        if (db.child("customers").child(username).child("budget").get().val()-budget<=0)
                        else f'Removing {db.child("customers").child(username).child("budget").get().val()-budget} from your account')
                    db.child("customers").child(username).child("budget").set(budget)
                else:
                    print("Wrong password!")

            elif act.lower() in ("c", "checkout"):
                a = input("Are you sure you want to checkout(y/n)?: ")
                if a.lower() in ("y", "yes"):
                    current_cust.checkout()
                else:
                    print("Okay! Then feel free to browse around the store")
            else:
                print("Invalid input")

    elif a in ("s", "seller"):
        while True:
            act = input("Do you want to see your statistics(s), add new products(a), restock existing products(r), redeem profit(p) or quit(q)?: ")

            if act.lower() in ("q", "quit"):
                break

            elif act.lower() in ("a", "add"):
                name = input("Enter the name of your product: ")
                name = name.lower()
                stock = int(input("Enter the stock of your product: "))
                cost = int(input("Enter the cost of your object: "))
                profit = int(input("Enter the profit per sale you want of your object: "))
                db.child("sellers").child(username).child("products").child(name).set({"cost": cost, "profit_unit": profit, "stock": stock, "units_sold": 0})
                db.child("products").child(name).set({"cost":cost, "price": (cost+profit), "seller":username, "stock":stock})
            
            elif act.lower()  in ("r", "restock"):
                name = input("Which unit do you want to restock: ")
                name = name.lower()
                setd = int(input("How many more units do you want to add: "))
                stock = db.child("sellers").child(username).child("products").child(name).child("stock").get().val()
                db.child("sellers").child(username).child("products").child(name).child("stock").set(stock + setd)
                db.child("products").child(name).child("stock").set(stock + setd)
            
            elif act.lower() in ("p", "profit", "redeem", "redeem profit"):
                profit = db.child("sellers").child(username).child("profit").get().val()
                db.child("sellers").child(username).child("profit").set(0)
                budget = db.child("customers").child(username).child("budget").get().val()
                db.child("customers").child(username).child("budget").set(budget + profit)
        
            elif act.lower() in ("s", "statistics"):
                gt = input("Do you want graphical statistics(g) or simple tabular form(t)?: ")
                if gt.lower() in ("t", "tabular"):
                    mywork = [["S. No.", "Name", "Cost", "Profit Margin", "Units Sold", "Profit earned from this item"]]
                    i = 1
                    for item in db.child("sellers").child(username).child("products").get().val():
                        mywork.append([i, item, db.child("sellers").child(username).child("products").child(item).child("cost").get().val(), db.child("sellers").child(username).child("products").child(item).child("profit_unit").get().val(), db.child("sellers").child(username).child("products").child(item).child("units_sold").get().val(), db.child("sellers").child(username).child("products").child(item).child("profit_unit").get().val()*db.child("sellers").child(username).child("products").child(item).child("units_sold").get().val()])
                        i += 1
                    print(tabulate(mywork))
                elif gt.lower() in ("g", "graph", "graphical"):
                    names = list(db.child("sellers").child(username).child("products").get().val().keys())
                    pu = input("Do you want data by profit earned per item(p) or units sold per item(u)?: ")
                    if pu.lower() in ("p", "profit"):
                        profits = [db.child("sellers").child(username).child("products").child(name).child("units_sold").get().val()*db.child("sellers").child(username).child("products").child(name).child("profit_unit").get().val() for name in names]
                        plt.bar(names, profits)
                        plt.show()
                    elif pu.lower() in ("u", "units"):
                        units = [db.child("sellers").child(username).child("products").child(name).child("units_sold").get().val() for name in names]
                        plt.bar(names, units)
                        plt.show()
