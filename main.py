import os
import csv


def check_cal_data(walk_dir):
    csv_title = "Ultrasound Depth and Focus Not Found.csv"
    os.remove("Calibration Files to Take.csv")
    for (root, dirs, files) in os.walk(walk_dir):
        if csv_title in files:
            find_missing_cal(os.path.join(root, csv_title))
            print(root)


def find_missing_cal(file_path):
    with open(file_path, newline='') as csvfile:
        cal_reader = csv.reader(csvfile, quotechar='|')
        for row in cal_reader:
            if "Scan name" not in row:
                write_missing_cal(row[1:])


def write_missing_cal(new_cal_line):
    with open('Calibration Files to Take.csv', 'a', newline='') as csvfile:
        writier = csv.writer(csvfile, delimiter=",")
        writier.writerow(new_cal_line)


if __name__ == '__main__':
    check_cal_data(r"S:\13. STIMULUS DATA\STIM001")
