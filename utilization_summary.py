import csv
import os
import datetime
import urllib.request
import json
import tock_blocks

TOCK_API_KEY = os.environ['TOCK_API_KEY']

MONTH_NAME_LIST = ["January", "February", "March",
                   "April", "May", "June", "July", "August",
                   "September", "October", "November", "December"
                  ]

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def all_users_from_file(userfile, args):
    data_source = 'api'
    if args.file is not None:
        data_source = args.file
    print("{}TOCK BLOCKS:{} Generating the utilization report from the data in {}.".format(color.PURPLE, color.END, data_source))
    users = tock_blocks.read_csv_to_list(userfile)
    if args.file is not None:
        time_entries = tock_blocks.read_csv_to_list(args.file)
    else:
        time_entries = get_data_from_tock()
    today = datetime.date.today()
    months = find_months(today, args)
    user_list = [0] * len(users)
    for user_index in range(len(users)):
        user_list[user_index] = users[user_index] + \
            utilization_calculator(
                users[user_index][0], months, time_entries, today)
    write_output(args, user_list, months, today)
    print(color.PURPLE+"TOCK BLOCKS:"+color.END+" Completed generating the utilization summary. Please view the report in the file "+ args.outfile +".")

def find_months(today, args):
    months = [0, 0]
    if args.beginmonth is None:
        months[0] = today.month - 2
    if args.lastmonth is None:
        months[1] = today.month + 1
    if months[1] == 0:
        months[1] = MONTH_NAME_LIST.index(args.lastmonth)+1
    if months[0] == 0:
        months[0] = MONTH_NAME_LIST.index(args.beginmonth)+1
        if months[0] >= months[1]:
            months[0] = months[0] - 12
    return months

def utilization_calculator(user, months, time_entries, today):
    # Grab user
    user_entries = tock_blocks.get_user_entries(user, time_entries)
    # Calculate each month billable/ utilization / total for that user
    user_values = [0] * (months[1]-months[0])
    array_ind = 0
    for x in range(months[0], months[1]):
        start_month = calculate_month_year(x, today)
        month_time_entries = tock_blocks.get_entries_in_month(
            start_month+"-01", user_entries
            )
        billable_hours = calc_billable_hours(month_time_entries)
        internal_hours = calc_internal_hours(month_time_entries)
        total_hours = calc_total_hours(month_time_entries)
        billable_percent = 0.0
        internal_percent = 0.0
        if total_hours > 0:
            billable_percent = round(billable_hours/total_hours*100, 1)
            internal_percent = round(internal_hours/total_hours*100, 1)
        utilizable_percent = round((billable_percent + internal_percent), 1)
        user_values[array_ind] = [billable_percent, internal_percent, utilizable_percent]
        array_ind += 1
    return user_values

def calculate_month_year(month_value, today):
    year_to_use = today.year
    x = month_value
    if month_value <= 0:
        year_to_use = year_to_use - 1
        x = month_value + 12
    start_month = ""
    if x < 10:
        start_month = "0"+str(x)
    elif month_value == 12:
        start_month = "12"
    else:
        start_month = str(x)
    start_month = str(year_to_use) + '-' + start_month
    return start_month

#TODO convert to lamdas
def calc_hour_generator(calculator_method):
    def nestedEntryIterator(entries):
        hour_count = 0
        for entry in entries:
            if calculator_method:
                hour_count += float(entry['hours_spent'])
    return nestedEntryIterator

def calc_billable_hours(entries):
    billable_hours_count = 0.0
    for entry in entries:
        if entry['billable']:
            billable_hours_count = billable_hours_count + float(entry['hours_spent'])
    return billable_hours_count

def calc_internal_hours(entries):
    internal_hours = 0.0
    for entry in entries:
        if entry['project_name'][:22] == "TTS Acq / Internal Acq" and entry['billable'] == False:
            internal_hours = internal_hours + float(entry['hours_spent'])
    return internal_hours

def calc_total_hours(entries):
    total_hours = 0.0
    for entry in entries:
        total_hours = total_hours + float(entry['hours_spent'])
    return total_hours

def monthly_and_average(user_list_row, sub_array_ind):
    filtered_list = [i[sub_array_ind] for i in user_list_row[3:]]
    filtered_list.append(round(mean(filtered_list[-3:]), 1))
    return filtered_list

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def get_data_from_tock():
    print(color.PURPLE+"TOCK BLOCKS:"+color.END+' Downloading data from tock! This is a big file. It could take several minutes.')
    url = 'https://tock.18f.gov/api/timecards.json?after=2017-10-01'
    headers = {}
    headers['Authorization'] = 'token %s' % TOCK_API_KEY

    req = urllib.request.Request(url, headers = headers)
    html = urllib.request.urlopen(req).read()
    parsed_reponse = json.loads(html.decode("utf-8"))
    print(color.PURPLE+"TOCK BLOCKS:"+color.END+' Completed downloading tock data. Now processing the data.')
    return parsed_reponse

def write_output(args, user_list, months, today):
    file_to_write = develop_filename(args, today)
    with open(file_to_write, 'w') as outcsv:
        writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        if months[0] <= 0: # check if starting in previous year
            first_month = months[0] + 11
            months_to_print = MONTH_NAME_LIST[first_month:] + MONTH_NAME_LIST[:months[1]-1]
        else:
            months_to_print = MONTH_NAME_LIST[months[0]-1+months[1]-1]
        header_row = ['Name', 'Position', 'Team', 'Project type']+months_to_print+['Average for last quarter']
        writer.writerow(header_row)
        for item in user_list:
            toprow = [item[0], item[1], item[2], 'Billable']+monthly_and_average(item, 0)
            middlelist = ['', '', '', 'Internal projects'] + monthly_and_average(item, 1)
            bottom = ['', '', '', 'Utilization percentage'] + monthly_and_average(item, 2)
            writer.writerow(toprow)
            writer.writerow(middlelist)
            writer.writerow(bottom)
            writer.writerow(['']*(len(item)+1))

def develop_filename(args, today):
    if args.outfile is not None:
        return args.outfile
    return 'outfile-{}.csv'.format(today.strftime("%Y-%m-%d"))
