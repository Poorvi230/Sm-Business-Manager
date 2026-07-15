def main():
    while True:
        print("\n" + "="*30)
        print("    SMALL BUSINESS SUITE")
        print("="*30)
        print("1. Inventory Management")
        print("2. Payroll Calculator")
        print("3. CRM (Customer Tickets)")
        print("4. Exit Program")
        print("="*30)

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            print("\n--> Opening Inventory Module...")

        elif choice == '2':
            print("\n--> Opening Payroll Module...")

        elif choice == '3':
            print("\nOpening CRM Module")

        elif choice == '4':
            print("\nExisting Business Suite. Have a great day!")
            break 

        else: 
            print("\nInvalid input. Please enter a number between 1 and 4")

if __name__ == "__main__":
    main()
    