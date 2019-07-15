

class interLoop():
    """This class is a prototype that creates a while loop which the user can
    interact with. It will display text, wait for user input, and react to
    the user input appropriately.
    """
    def __init__(self, start_msg):
        self.continue_var = True
        self.start_msg = start_msg

    def stuff(self):
        print(start_msg)
        while self.continue_var == True:
            self.user_input = input(">>")
            
