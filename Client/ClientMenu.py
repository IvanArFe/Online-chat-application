import PrivateChat

class ClientMenu:
    def showMenu():
        print("Welcome to Online chat application! Which option would you like to choose?")
        print("[1] Connect to chat")
        print("[2] Subscribe to group chat")
        print("[3] Discover chats")
        print("[4] Acces insult channel")
        print("[5] Exit Online chat")
    
    while True:
        showMenu()
        option = input("Choose an available option option: ")
        try:
            if option == "1":
                print("Would you like to connect to a private chat or a group chat?")
                choice = input("Type private or group please")

                if choice == "private":
                    print("Connecting to private chat...")
                    clientName = input("Enter the corresponding name to the person you want to chat with")
                    
                else:
                    print("Connecting to group chat...")

            elif option == "2":
                print("Subscribing to group chat...")

            elif option == "3":
                print("Discovering chats...")

            elif option == "4":
                print("Accessing insult channel...")

            elif option == "5":
                print("Quitting...")
                break
        except ValueError:
            print("Chosen number is not a valid option!")