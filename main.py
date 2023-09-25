import os
import csv
import yaml
import threading
from time import perf_counter


# Searches all files in walk_dir looking for all instances of "Ultrasound Depth and Focus Not Found.csv". This will
# then read all the depth and focus values from these CSVs and record them in a new CSV which is stored in the
# root folder of this project.
def check_cal_data(walk_dir):
    search_csv = "Ultrasound Depth and Focus Not Found.csv"
    cal_to_take = "Calibration Files to Take.csv"
    if os.path.exists(cal_to_take):
        os.remove(cal_to_take)
    with open(cal_to_take, 'a', newline='') as unique_csvfile:
        writier = csv.writer(unique_csvfile, delimiter=",")
        writier.writerow(["", ""])
    for (root, dirs, files) in os.walk(walk_dir):
        if search_csv in files:
            find_missing_cal(os.path.join(root, search_csv))
            print(root.replace("Ultrasound Calibration Data", ''))
    clean_cal_csv(cal_to_take)


# Parses through the csv file detailing which calibration data is missing and picks out the depth and focus values
# that still need to be captured. These values are passed to a function that writes them to a csv.
def find_missing_cal(file_path):
    with open(file_path, newline='') as csvfile:
        cal_reader = csv.reader(csvfile, quotechar='|')
        for row in cal_reader:
            if "Scan name" not in row:  # Skip the header row at the top
                write_missing_cal(row[1:])  # remove the scan title of the calibration value


# Writes calibration values passed to this function to a csv file. This funciton adds everything and doesn't account
# for duplicates or proper formating.
def write_missing_cal(new_cal_line):
    with open('Calibration Files to Take.csv', 'a', newline='') as csvfile:
        writier = csv.writer(csvfile, delimiter=",")
        writier.writerow(new_cal_line)


# Adds a new line to a csv file. new_line must be given as a list of values. If given a string, each letter from the
# string will be split up as its own value. e.g. Apple -> a,p,p,l,e
def write_csv_line(csv_name, new_line):
    with open(csv_name, 'a', newline='') as csvfile:
        writier = csv.writer(csvfile, delimiter=",")
        writier.writerow(new_line)


# Removes the duplicate data points from the csv containing all missing data points by creating a new csv
# and only allowing unique values to be added.
def clean_cal_csv(cal_csv):
    cal_vals = [['', '']]
    out_vals = []
    new_csv = "Unique Calibration Values.csv"
    if os.path.exists(new_csv):  # removes a csv with the temp name in case code didn't complete last time
        os.remove(new_csv)
    with open(new_csv, 'a', newline='') as unique_csvfile:
        writier = csv.writer(unique_csvfile, delimiter=",")
        writier.writerow(["Depth", "Focus"])
    with open(cal_csv, newline='') as csvfile:
        cal_reader = csv.reader(csvfile, quotechar='|')
        for row in cal_reader:
            if row not in cal_vals:  # Ensure no duplicates are recorded
                cal_vals.append(row)
                out_vals.append(row)
    with open(new_csv, 'a', newline='') as unique_csvfile:
        for val in sorted(out_vals, key=lambda depth_list: float(depth_list[0])):  # sort based on the depth value
            writier = csv.writer(unique_csvfile, delimiter=",")
            writier.writerow(val)
    os.remove(cal_csv)
    os.rename(new_csv, cal_csv)


# Prints the depth values of scans with transmit frequency equal to transmit_freq
def check_frequency(walk_dir, transmit_freq):
    yaml_search_term = "rf.yml"
    for (root, dirs, files) in os.walk(walk_dir):
        rf_yaml = [file_name for file_name in files if yaml_search_term in file_name]
        if rf_yaml:
            yaml_file = yaml_info(os.path.join(root, rf_yaml[0]))
            if float(yaml_file['transmit frequency'][0:-3]) == transmit_freq:
                print(f"Frequency: {yaml_file['imaging depth']} Depth: {yaml_file['transmit frequency']}")

            # if float(yaml_file['imaging depth'][0:-4]) < 100.0:
            #     print(yaml_file['transmit frequency'] + '\n')


# Helps with opening yaml files so their information is easier to access
def yaml_info(yaml_path):
    with open(yaml_path) as file:
        yaml_out = yaml.safe_load(file)
    return yaml_out


# finds participant that has not been unzipped and is still in .tar format
def find_unprocessed(walk_dir):
    unprocessed_paticipants = "Unprocessed Participants.csv"
    if os.path.exists(unprocessed_paticipants):
        os.remove(unprocessed_paticipants)
    for (root, dirs, files) in os.walk(walk_dir):
        processed = True
        for file in files:
            if '.tar' in file:
                processed = False
                for directory in dirs:
                    if file[0:-4] in directory:
                        processed = True
            if not processed:
                participant_path = '/'.join(root.split('\\')[:-1])
                # print(f"participant_path: {participant_path}")
                print(f"root {root}")
                write_csv_line(unprocessed_paticipants, [root])
                break
    if not os.path.exists(unprocessed_paticipants):
        write_csv_line(unprocessed_paticipants, ['All participants processed'])


# Starts each function in the list in its own thread.
def run_threads(thread_functions):
    threads = []
    for function in thread_functions:
        threads.append(threading.Thread(target=function))
        threads[-1].start()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    t1 = perf_counter()
    stim_folder = r"S:\13. STIMULUS DATA"
    function_list = [lambda: check_cal_data(stim_folder), lambda: find_unprocessed(stim_folder)]
    run_threads(function_list)
    # check_cal_data(r"S:\13. STIMULUS DATA")
    # find_unprocessed(r"S:\13. STIMULUS DATA")
    # check_frequency(r"C:\Users\Alex Devlin\Desktop\STIM Data\Calibration Library\BCWMain C3HD3032210A0795", 2.5)
    print(f'Finished in {perf_counter() - t1}')
