from tabulate import tabulate
from collections import Counter
import matplotlib.pyplot as plt
import json

class Customer:
    def __init__(self, name, cart, budget, cart_value):
        self.name = name
        self.cart = cart
        self.budget = budget
        self.cart_value = cart_value

    def show_cart(self):
        with open("Json files/products.json", ) as f:
            file = json.load(f)
        temp = [[0, "Name", "Quantity", "Price by piece", "Total price"]]
        i = 1
        for a, b in self.cart.items():
            temp.append([i, a, b, file[a]["price"], file[a]["price"]*b])
            i += 1
        print(tabulate(temp))

    def add_to_cart(self, item, quantity):
        with open("Json files/products.json", ) as f:
            file = json.load(f)
        if item not in self.cart:
            self.cart[item] = quantity
        else:
            self.cart[item] += quantity
        self.cart_value += file[item]["price"]*quantity
        with open("Json files/customers.json", ) as f:
            file = json.load(f)
        file[self.name]["cart"], file[self.name]["cart_value"] = self.cart, self.cart_value
        with open("Json files/customers.json", "w") as f:
            json.dump(file, f)

    def remove_from_cart(self, item, quantity):
        with open("Json files/products.json", ) as f:
            file = json.load(f)
        if self.cart[item] > quantity:
            self.cart[item] -= quantity
            self.cart_value -= file[item]["price"]*quantity
        else:
            self.cart_value -= file[item]["price"]*self.cart[item]
            del self.cart[item]
        with open("Json files/customers.json", ) as f:
            file = json.load(f)
        file[self.name]["cart"], file[self.name]["cart_value"] = self.cart, self.cart_value
        with open("Json files/customers.json", "w") as f:
            json.dump(file, f)

    def checkout(self):
        with open("Json files\customers.json", ) as f:
            custs = json.load(f)
        with open("Json files\products.json", ) as f:
            file = json.load(f)
        with open("Json files\seller.json", ) as f:
            sellers = json.load(f)
        a = 0
        for name, val in self.cart.items():
            if val <= file[name]["stock"]:
                file[name]["stock"] -= val
                sellers[file[name]["seller"]]["products"][name]["stock"] -= val
                sellers[file[name]["seller"]]["products"][name]["units_sold"] += val
                a += val*(file[name]["price"])
                sellers[file[name]["seller"]]["profit"] += val * sellers[file[name]["seller"]]["products"][name]["profit_unit"]
                
            else:
                print(
                    f"We had only {file[name]['stock']} available of what you want, Sorry! Your total price will be adjusted!")
                sellers[file[name]["seller"]]["profit"] += file[name]["stock"] * \
                    (file[name]["price"]-file[name]["cost"])
                a += file[name]["stock"]*(file[name]["price"])
                sellers[file[name]["seller"]]["products"][name]["units_sold"] += file[name]["stock"]
                sellers[file[name]["seller"]]["products"][name]["stock"] = 0
                file[name]["stock"] = 0
        self.budget = int(self.budget);
        if a > self.budget:
            print("Insufficient funds.")
        else:
            print(f"Debitting {a} from your account")
            self.budget -= a
            self.cart.clear()
            self.cart_value = 0
            custs[self.name]["budget"], custs[self.name]["cart"], custs[self.name]["cart_value"]  = self.budget, self.cart, self.cart_value
            with open("Json files\customers.json", 'w') as f:
                json.dump(custs, f)
            with open("Json files\products.json", "w") as f:
                json.dump(file, f)
            with open("Json files\seller.json", 'w') as f:
                json.dump(sellers, f)

a = ''
while a.lower() not in ("c", "customer", "s", "seller"):
    a = input("Do you want to be a customer(c) or seller(s)?: ")
a = a.lower()

ls = ""
while ls.lower() not in ("l", "s", "login", "signup"):
    ls = input("Do you want to login(l) or signup(s)?: ")
ls = ls.lower()

if ls in ("l", "login"):
    if a in ("c", "customer"):
        with open("Json files/customers.json", ) as myfile:
                custs = json.load(myfile)

        while True:
            username = input("Enter your username please: ")
            if username in custs:
                break
            else:
                print("Wrong username")

        for k in range(3):
            password = input("Enter you password: ")
            if password == custs[username]["password"]:
                break
        else:
            print("Too many failed attempts, Retry again later.")

        print("Login successful!")

    elif a in ("s", "seller"):
        with open("Json files/seller.json", ) as f:
            sellers = json.load(f)
        with open("Json files/customers.json", ) as f:
            custs = json.load(f)
        
        username = input("Enter your username: ")
        while username not in sellers:
            print("invalid username")
            username = input("Enter your username: ")
        for k in range(3):
            password = input("Enter you password: ")
            if password == custs[username]["password"]:
                break
        else:
            print("Too many failed attempts, Retry again later.")

elif ls in ("s", "signup"):
    if a in ("c", "customer"):
        with open("Json files/customers.json", ) as myfile:
            custs = json.load(myfile)
        while True:
            username = input("Enter your username please: ")
            if username in custs:
                print("Sorry username is taken")
            else:
                break
        password = input("Create a strong password: ")
        budget = input("Enter your budget: ")
        custs[username] = {"password": password,
                       "budget": budget, "cart": {}, "cart_value": 0}
        with open("Json files/customers.json", "w") as myfile:
            json.dump(custs, myfile)
    else:
        with open("Json files/seller.json", ) as f:
            seller = json.load(f)
        with open("Json files/customers.json", ) as f:
            customers = json.load(f)
        username = input("Enter the username in your customer account: ")
        if username in customers and username not in seller:
            print("Account found")
            password = input("Enter your password: ")
            if password == customers[username]["password"]:
                seller[username] = {"products": {}, "profit": 0}
                with open("seller.json", "w") as f:
                    json.dump(seller, f) 
                print("Succesfully created your seller account!")
            else:
                print("Access denied")
        else:
            print("Either you dont have a customer account or you already have a seller account!")

if a in ("c", "customer"):
    current_cust = Customer(username, custs[username]["cart"], custs[username]["budget"], custs[username]["cart_value"])

    while True:

        act = input(
            "Do you want to checkout(c), manipulate your cart(m), update your budget(b) or quit(q): ")

        if act.lower() in ("q", "quit"):
            break

        elif act.lower() in ("m", "manipulate", "cart"):
            current_cust.show_cart()

            with open("Json files/products.json", ) as f:
                temp = json.load(f)

            while True:

                what = input(
                    "Do you want to add stuff to your cart(a), remove stuff from your cart(r), or quit(q): ")

                if what.lower() in ("q", "quit"):
                    break

                elif what.lower() in ("a", "add"):
                    print("This is a list of available items: ")
                    shop = [["S. No.", "Name", "Price"]]
                    i = 1
                    for item in temp:
                        shop.append([i, item, temp[item]["price"]])
                        i += 1
                    print(tabulate(shop))
                    nums = map(int, input(
                        "Enter the S. No. of items you want seperated by a comma(if you want multiple objects of one type add the S. No. multiple times): ").split(","))
                    names = [shop[i][1] for i in nums]
                    names = Counter(names)
                    for k, v in names.items():
                        current_cust.add_to_cart(k, v)

                    print('Your updated cart is: ')
                    current_cust.show_cart()

                elif what.lower() in ("r", "remove"):
                    print("This is your cart")
                    current_cust.show_cart()
                    a = input(
                        "Enter name and quantity of the item you want to remove, if you want to remove multiple items split them with a comma!: ")
                    mylist = [(info.split()[0].lower(), int(info.split()[1])) for info in a.split(",")]
                    for a, b in mylist:
                        current_cust.remove_from_cart(a, b)
                    print("This is your updated cart")
                    current_cust.show_cart()

        elif act.lower() in ("b", "budget", "u", "update"):
            budget = int(input("Enter your new budget: "))
            confirmation = input("Confirm your password: ")
            if confirmation == custs[username]["password"]:
                custs[username]["budget"] = budget
                with open("Json files/customers.json", "w") as f:
                    json.dump(custs, f)
                print(f"Successfully updated budget to {budget}")
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
    with open("Json files/products.json",) as prod:
        products = json.load(prod)

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
            sellers[username]["products"][name] = {"profit_unit":profit, "cost":cost, "stock":stock, "units_sold":0}
            products[name] = {"cost": cost, "price": (cost + profit), "seller":username, "stock":stock}
            with open("Json files\products.json", "w") as f:
                json.dump(products, f)
            with open("Json files\seller.json", "w") as f:
                json.dump(sellers, f)
        
        elif act.lower()  in ("r", "restock"):
            name = input("Which unit do you want to restock: ")
            name = name.lower()
            updated = int(input("How many more units do you want to add: "))
            sellers[username]["products"][name]["stock"] += updated
            products[name]["stock"] += updated 
            with open("Json files\products.json", "w") as fp:
                json.dump(products, fp)
            with open("Json files\seller.json", "w") as fp:
                json.dump(sellers, fp)
        
        elif act.lower() in ("p", "profit", "redeem", "redeem profit"):
            custs[username]["budget"] = sellers[username]["profit"]
            sellers[username]["profit"] = 0
            with open("Json files\customers.json", "w") as f:
                json.dump(custs, f)
            with open("Json files\seller.json", "w") as f:
                json.dump(sellers, f)
    
        elif act.lower() in ("s", "statistics"):
            gt = input("Do you want graphical statistics(g) or simple tabular form(t)?: ")
            if gt.lower() in ("t", "tabular"):
                mywork = [["S. No.", "Name", "Cost", "Profit Margin", "Units Sold", "Profit earned from this item"]]
                i = 1
                for item in sellers[username]["products"]:
                    mywork.append([i, item, sellers[username]["products"][item]["cost"], sellers[username]["products"][item]["profit_unit"], sellers[username]["products"][item]["units_sold"], sellers[username]["products"][item]["profit_unit"]*sellers[username]["products"][item]["units_sold"]])
                    i += 1
                print(tabulate(mywork))
            elif gt.lower() in ("g", "graph", "graphical"):
                names = list(sellers[username]["products"].keys())
                pu = input("Do you want data by profit earned per item(p) or units sold per item(u)?: ")
                if pu.lower() in ("p", "profit"):
                    profits = [sellers[username]["products"][name]["units_sold"]*sellers[username]["products"][name]["profit_unit"] for name in names]
                    plt.bar(names, profits)
                    plt.show()
                elif pu.lower() in ("u", "units"):
                    units = [sellers[username]["products"][name]["units_sold"] for name in names]
                    plt.bar(names, units)
                    plt.show()