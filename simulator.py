'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''
import sys
from heapq import heappush, heappop
from copy import deepcopy
input_file = 'input.txt'


class Process:
    last_scheduled_time = 0

    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.remain_time =burst_time
        self.last_time = arrive_time
    # for printing purpose

    def __repr__(self):
        return ('[id %d : arrival_time %d,  burst_time %d]' % (self.id, self.arrive_time, self.burst_time))


def FCFS_scheduling(process_list):
    # store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time, process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

# Input: process_list, time_quantum (Positive Integer)
# Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
# Output_2 : Average Waiting Time


def RR_scheduling(process_list, time_quantum):
    RR_process_list = deepcopy(process_list)
    schedule = []
    current_time = 0
    waiting_time = 0
    length = len(process_list)

    while len(RR_process_list) != 0:
        temp_indicator = 0
        for process in RR_process_list:
            if process.burst_time > 0:
                if current_time >= process.arrive_time:
                    schedule.append((current_time, process.id))
                    if process.last_scheduled_time == 0:
                        waiting_time = waiting_time + \
                            (current_time - process.arrive_time)
                    else:
                        waiting_time = waiting_time + \
                            (current_time - process.last_scheduled_time)
                    if process.burst_time <= time_quantum:
                        duration = process.burst_time
                    else:
                        duration = time_quantum
                    temp_indicator = 1
                    current_time = current_time + duration
                    process.last_scheduled_time = current_time
                    process.burst_time = process.burst_time - duration
                    if process.burst_time <= 0:
                        RR_process_list.remove(process)
        if temp_indicator == 0:
            current_time = RR_process_list[0].arrive_time
        average_waiting_time = waiting_time/float(length)
    return schedule, average_waiting_time


def SRTF_scheduling(process_list):
    current_time = 0
    waiting_time = 0
    schedule = []
    queue = []
    current_process = process_list[0]
    schedule.append((current_process.arrive_time, current_process.id))
    for process in process_list[1:]:
        start_time = current_process.last_time
        current_time = process.arrive_time
        while (current_time > (start_time + current_process.remain_time)):
            start_time = start_time+current_process.remain_time
            if(len(queue)>0):
               remain, current_process = heappop(queue) 
               schedule.append((start_time, current_process.id))
               waiting_time = waiting_time + start_time - current_process.last_time
            else:
                current_process = None
                break
        if current_process != None:
            current_process.remain_time = current_process.remain_time -(current_time - start_time)
            waiting_time = waiting_time + start_time - current_process.last_time
            if current_process.remain_time <= process.last_time:
                heappush(queue, (process.remain_time, process))
                current_process.last_time = current_time
            else:
                current_process.last_time = current_time
                heappush(queue, (current_process.remain_time, current_process))
                current_process = process
                schedule.append((current_time, current_process.id))
        else:
            #start next job
            current_process = process
            schedule.append((current_time, current_process.id))
    while (len(queue) > 0):
        # finish all jobs in the queue
        start_time = current_time+current_process.remain_time
        remain, current_process = heappop(queue)
        schedule.append((start_time, current_process.id))
        waiting_time = waiting_time + (start_time - current_process.last_time)
        current_time = start_time

    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time


def SJF_scheduling(process_list, alpha):
    schedule = []
    current_time = 0
    waiting_time = 0
    length = len(process_list)
    remain_process = [True] * length
    id_list = []

    for process in process_list:
        id_list.append(process.id)
    predict = {i: 5 for i in set(id_list)}

    for count in range(length):
        candidate = []
        for i in range(length):
            if remain_process[i] and process_list[i].arrive_time <= current_time:
                candidate.append(i)
        #print(1, candidate)
        # check empty
        if not len(candidate):
            current_time = process_list[count].arrive_time
            for i in range(length):
                if remain_process[i] and process_list[i].arrive_time <= current_time:
                    candidate.append(i)
        #print(2, candidate)
        temp = []
        for i in candidate:
            temp.append((i, predict[process_list[i].id]))
        # find the index id that will be used to schedule
        index_id, _ = min(temp, key=lambda x: x[1])

        process = process_list[index_id]
        if current_time < process.arrive_time:
            current_time = process.arrive_time
        schedule.append((current_time, process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time

        predict[process.id] = alpha * process.burst_time + \
            (1 - alpha) * predict[process.id]
        remain_process[index_id] = False

    average_waiting_time = waiting_time / float(length)
    return schedule, average_waiting_time

def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array) != 3):
                print("wrong input format")
                exit()
            result.append(Process(int(array[0]), int(array[1]), int(array[2])))
    return result


def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name, 'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n' % (avg_waiting_time))


def main(argv):
    process_list = read_input()
    print("printing input ----")
    for process in process_list:
        print(process)
    print("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time = FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time)
    print("simulating RR ----")
    RR_schedule, RR_avg_waiting_time = RR_scheduling(
        process_list, time_quantum=2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time)
    print("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time = SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time)
    print("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time = SJF_scheduling(
        process_list, alpha=0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time)


if __name__ == '__main__':
    main(sys.argv[1:])
