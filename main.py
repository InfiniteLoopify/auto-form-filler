
import requests
import time
import re


def get_agent_info(words):
    """ convert agent info string to agent name, id, mins and secs """
    time = words[-1]
    mins = 1
    secs = 0
    name = ' '.join(words)
    if not time.isalpha() and len(time) < 6:
        time = time.split('-')
        mins = int(time[0])
        secs = int(time[1]) if len(time) > 1 else 0
        name = ' '.join(words[0:-1])
    return name, mins, secs


def get_count(line):
    count = re.findall(r"x\d+", line)
    count = int(count[0][1:]) if count else 1
    return count


def get_info(line):
    # words = [word.lower() for word in words]
    line = " " + line.lower().rstrip() + " "
    name = "-"
    mins = 1
    secs = 0
    status = 0
    count = 1

    # silent call x<count>
    if re.search(r"silent *call", line):
        count = get_count(line)
        status = 1

    # unanswered call x<count>
    elif re.search(r"unanswered *call", line):
        count = get_count(line)
        status = 2

    # disconnected call x<count>
    elif re.search(r"disconnected *call", line):
        count = get_count(line)
        status = 3

    # successful call: <Name> <6 digit id> <minutes>-<seconds>
    elif re.search(r" +\d{6} +", line):
        status = 0
        name = re.findall(r"[a-z]+", line)
        name = " ".join(name)
        agent_id = str(int(re.findall(r" +\d{6} *", line)[0]))
        name = name + " " + agent_id
        print(name)

        # mins and seconds given
        if re.search(r" +\d{1,2}[\-]\d{1,2} +", line):
            time = re.findall(r" +\d{1,2}[\-]\d{1,2} +", line)[0].split('-')
            mins = int(time[0])
            secs = int(time[1])
            print(mins, secs)

        # only mins given
        elif re.search(r" +\d{1,2} +", line):
            mins = int(re.findall(r" +\d{1,2} +", line)[0])
            secs = 0
            print(mins)

        # time (min/sec) not given. defaults to 1 second
        else:
            mins = 1
            secs = 0

    # invalid data entry.
    else:
        status = -1

    return name, mins, secs, count, status


def fill_form(my_name, their_name, mins, secs):
    """ fill a single form and tick check boxes according to minutes """

    caller_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdhy_rcn6VBdUSRKbDTz5TqyGTY9NT-LE9FZbkvOb2A8-VyJw/formResponse"

    values = {
        # my name and id
        "entry.120477194": my_name,
        # their name and id
        "entry.1251079050": their_name,
        # call duration
        "entry.1262782937": str(mins)+"-"+str(secs),
        # entry box 1
        "entry.905041685": "Passed",
        # entry box 2
        "entry.931257732": "Passed",
        # entry box 3
        "entry.6405329": "Passed",
        # 1 min box
        "entry.739539018": "Passed",
        # 5 min box
        "entry.723410662": "Passed" if mins >= 5 else "Not Applicable",
        # 10 min box
        "entry.1071130003": "Passed" if mins >= 10 else "Not Applicable",
    }

    # post request of form and check for errors
    try:
        response = requests.post(caller_form_url, data=values)
        print(their_name)
        time.sleep(1)
    except Exception as err:
        print('(Error: ', err, ') -> ', their_name)


if __name__ == "__main__":
    my_name = "abcqwe 123456"
    filename = open("file.txt", "r")

    # for every entry in file, fill form
    for line in filename.readlines():
        get_info(line)
        # words = line.split()
        # if words and words[0][0] != '#':  # if line is commented with '#'
        #     is_valid = True if any((val.isdecimal() and len(val) == 6)
        #                            for val in words) and any(val.isalpha()
        #                                                      for val in words) else False
        # if is_valid:
        #     their_name, mins, secs = get_agent_info(words)
        #     fill_form(my_name, their_name, mins, secs)
        # else:
        #     print("Invalid Entry Discarded: ", ' '.join(words))
