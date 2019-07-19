

class interLoop():
    """This class is a prototype that creates a while loop which the user can
    interact with. It will display text, wait for user input, and react to
    the user input appropriately.
    """
    def __init__(self, start_msg, watch_list):
        """Input:
                start_msg: string. This is a message that is displayed to the
                    user once before the loop begins. This can be an explanation
                    of the program, a list of commands, or a prompt for specific
                    input.
                watch_list: dict. This is a dictionary with n key-value pairs,
                    where n is the number of keywords our loop watches out for.
                        key: string. If the user provided input matches one of
                            the keys in this dictionary, the loop will take the
                            appropriate action (detailed below). For example,
                            "h" might be a valid keyword indicting that the user
                            wants help, and a list of options should be printed.
                            Other keywords might indicate specific methods
                            within the parent object.
                        value: a list containing the following:
                            value[0]: a function or method that should be
                                invoked in response to the user providing this
                                value's key as an input.
                            value[1]: string. A short description of the
                                function or method in value[0], including
                                what kind of input this function expects and
                                any additional options.
                                

                        # watch_list[0]: list of strings of length n. Each entry
                        #     in the list is a keyword that will be compared to
                        #     the user provided input. For example: "h" might
                        #     be a valid keyword indicating that the user wants
                        #     help, and a list of options should be printed. Other
                        #     keywords might indicate specific methods within the
                        #     parent object.
                        # watch_list[1]: a list of functions or methods that
                        #     should be invoked in response to the corresponding
                        #     keyword in watch_list[0]
                        # watch_list[2]: a list of strings of length n. Each entry
                        #     is a short description of the function in
                        #     watch_list[1], including what kind of input this
                        #     function expects and any additional options.
                        # inplement later. Let's not get bogged down
                        # watch_list[3]: a list of length n in which every entry
                        #     is a dictionary containing the following
                        #     information:
                        #         key: an additional option for the corresponding
                        #             function or medod in watch_list[1]. This
                        #             might be "-v", for example, which causes the function or method to print more data than
                        #             it otherwise would.
                        #         value:
        """
        self.continue_var = True
        self.start_msg = start_msg
        self.watch_list = watch_list

    def things(self):
        i = self.user_input.lower().split()
        if i[0] in self.watch_list[0]:
            if len(i) > 1:
                watch_list[]


    def stuff(self):
        """This method begins a while loop that does the following:
            1. Displays a message to the user (i.e. a message explaining the
            program, commands, or prompting the user for specific input)
            2. Waits for user input
            3. Performs specific action in response to the input
            4. Repeat the loop or exit
        """
        print(start_msg)
        while self.continue_var == True:
            self.user_input = input(">>")
            self.things()
