
import requests
import time
import re


def get_count(line):
    count = re.findall(r"x\d+", line)
    count = int(count[0][1:]) if count else 1
    return count


def get_time(line):
    # mins and seconds given
    if re.search(r" +\d{1,2}[\-]\d{1,2} +", line):
        time = re.findall(r" +\d{1,2}[\-]\d{1,2} +", line)[0].split('-')
        mins = int(time[0])
        secs = int(time[1])

    # only mins given
    elif re.search(r" +\d{1,2} +", line):
        mins = int(re.findall(r" +\d{1,2} +", line)[0])
        secs = 0

    # time (min/sec) not given. defaults to 1 second
    else:
        mins = 1
        secs = 0

    return mins, secs


def extract_caller_info(line):
    # words = [word.lower() for word in words]
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
        mins, secs = get_time(line)

    # invalid data entry.
    else:
        status = -1

    return name, mins, secs, count, status


def extract_agent_info(line):
    status = -1
    mins = 1
    secs = 0
    count = 1

    # successful <min>-<sec> <count>
    if re.search(r"successful", line):
        count = get_count(line)
        mins, secs = get_time(line)
        status = 1

    # state error <min>-<sec> <count>
    elif re.search(r"state *error", line):
        count = get_count(line)
        mins, secs = get_time(line)
        status = 2

    # invalid data entry
    else:
        status = -1

    return mins, secs, count, status


def fill_caller_form(my_name, their_name, mins, secs, status):
    """ fill a single form and tick check boxes according to minutes """

    caller_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdhy_rcn6VBdUSRKbDTz5TqyGTY9NT-LE9FZbkvOb2A8-VyJw/formResponse"

    result = ""
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
    if status == 1:
        values["entry.739539018.other_option_response"] = "silent call"
        result = "silent call"
    elif status == 2:
        values["entry.931257732"] = "Unable to establish connection with the agent"
        values["entry.6405329"] = "Not applicable"
        values["entry.739539018"] = "Not Applicable"
        result = "unanswered call"
    elif status == 3:
        values["entry.905041685"] = "Call disconnecting after ringing before reaching the announcement"
        values["entry.931257732"] = "Unable to establish connection with the agent"
        values["entry.6405329"] = "Not applicable"
        values["entry.739539018"] = "Not Applicable"
        result = "disconnected call"
    else:
        result = "successful call: " + their_name

    # repeat until successful
    fail_status = 1
    while fail_status:
        fail_status = fill_form(caller_form_url, values, result)


def fill_agent_form(my_name, mins, secs, status):
    """ fill a single form and tick check boxes according to minutes """

    agent_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdxGqR1cYpGCQp23wK6dgZwzQPlQqqaAIo61EpIfUM401i6pg/formResponse"

    result = ""
    values = {
        # my name and id
        "entry.46240384": my_name,
        # call duration
        "entry.738177074": str(mins)+"-"+str(secs),
        # entry box 1 url_2
        "entry.1153667312": "Passed for URL 2",
        # entry box 1 url_1
        "entry.1153667312": "Passed for URL 1",
        # entry box 2
        "entry.1362397944": "Passed",
        # entry box 3
        "entry.207091415": "Passed",
        # entry box 4
        "entry.1764449265": "Passed",
        # entry box 5
        "entry.929355429": "Passed",
    }
    if status == 1:
        values["entry.2130452503"] = "Passed"
        result = "successful - " + str(mins)+"m "+str(secs) + "s"
    elif status == 2:
        values["entry.2130452503"] = "Unable to come back into READY state"
        result = "state error - " + str(mins)+"m "+str(secs) + "s"

    # repeat until successful
    fail_status = 1
    while fail_status:
        fail_status = fill_form(agent_form_url, values, result)


def fill_form(form_url, values, result):
    # post request of form and check for errors
    fail_status = 0
    try:
        response = requests.post(form_url, data=values, timeout=2)
        print(result)
        # time.sleep(0)
        fail_status = 0
    except Exception as err:
        print(' ***( ERROR: ', err, ') -> ', result)
        fail_status = 1
    return fail_status


if __name__ == "__main__":
    my_name = "qwerty 123456"
    print("Current NAME/ID: ", my_name)

    # select option (caller or agent side)
    print("\nSelect your Option:")
    option = input("Caller(1) / Agent(2) ").strip()

    # for every entry in caller file, fill form
    if option == "1":
        filename = open("caller.txt", "r")
    elif option == "2":
        filename = open("agent.txt", "r")
    else:
        exit(1)

    # for every entry in file, fill form
    for line in filename.readlines():
        line = line.lower().rstrip()

        # if line exists and is uncommented
        if line and not re.search(r"^ *[\#]", line):
            line = " " + line + " "

            # extract useful info from line
            if option == "1":
                their_name, mins, secs, count, status = extract_caller_info(
                    line)
            elif option == "2":
                mins, secs, count, status = extract_agent_info(line)

            # fill form using info if valid entry
            if status != -1:
                for i in range(count):
                    if option == "1":
                        fill_caller_form(my_name, their_name,
                                         mins, secs, status)
                    elif option == "2":
                        fill_agent_form(my_name, mins, secs, status)

            # discard if invalid entry
            else:
                print(" *INVALID ENTRY DISCARDED -> ", line)
