# auto-form-filler
Fill online forms in batch automatically using post request


## Instructions
1.   Edit your own name and id in `main.py` file by changing the value of `my_name` variable to `<First Name> <Last Name> <id>`. For example change `my_name` string value to `Edward Elric 123456`.
2.   Write agents name, id, call status, minutes etc in the file named `file.txt`. There are 4 types of queries: Successful Call, Silent Call, Unanswered Call, and Disconnected Call.
        * Succesful Calls: For a Succesful Call entry write in the format `<Name> <id> <Minutes>-<Seconds>`. For example `Steven Gerrard 654321 5-23`, where name = Steven Gerrard, id = 654321, mins = 5, secs = 23. The seconds part can be skipped.
        In `Steven Gerrard 654321 5` secs = 0. The time can also be left to get the default value of 1min and 0sec.
        * Silent Calls: For this, write in the format `silent call x<count>`. For example `silent call x7` means 7 silent calls, so 7 form will be filled. to get the default value of 1 call, skip the count part for example `silent call`.
        * Unanswered Calls: Same as that of silent call except replace it by `unanswered call x<count>`.
        * Disconnected Calls: Same as that of silent call except replace it by `disconnected call x<count>`.
        * Invalid Queries: Queries that do not fulfil above conditions are discarded.
3.   Run the script using command line by running the command `python3 main.py` or by using an IDE. Make sure `file.txt` is in the same directory as `main.py` file.
