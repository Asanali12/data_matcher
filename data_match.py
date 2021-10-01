import sqlite3
import datetime



con = sqlite3.connect("db/signals.sqlite")

cur = con.cursor()

input_signals = []
recorded_images = []
matched = []

for row in cur.execute('SELECT * FROM signals;'):
    list_row = list(row)
    list_row[1] = datetime.datetime.strptime(list_row[1], '%Y-%m-%d %H:%M:%S.%f')
    input_signals.append(list_row)

for row in cur.execute('SELECT id, dateTime, state FROM images;'):
    list_row = list(row)
    list_row[1] = datetime.datetime.strptime(list_row[1], '%Y-%m-%d %H:%M:%S.%f')
    recorded_images.append(list_row)

con.close()



for i in range(len(recorded_images)-1):
    records_exists = False
    for user_inp in input_signals:
        if ( user_inp[1] >= recorded_images[i][1] and user_inp[1] < recorded_images[i+1][1]):
            matched.append([ recorded_images[i][0], recorded_images[i][1], recorded_images[i][2], user_inp[0], user_inp[1], user_inp[2], user_inp[3] ])
            records_exists = True
    if records_exists == False:
        matched.append([ recorded_images[i][0], recorded_images[i][1], recorded_images[i][2], None, None, None, None ])

records_exists = False
for user_inp in input_signals:
    if ( user_inp[1] >= recorded_images[len(recorded_images)-1][1]):
        matched.append([ recorded_images[len(recorded_images)-1][0], recorded_images[len(recorded_images)-1][1], recorded_images[len(recorded_images)-1][2], user_inp[0], user_inp[1], user_inp[2], user_inp[3] ])
        records_exists = True
if records_exists == False:
    matched.append([ recorded_images[len(recorded_images)-1][0], recorded_images[len(recorded_images)-1][1], recorded_images[len(recorded_images)-1][2], None, None, None, None ])

count_present_no_input = 0
count_absent_no_input = 0
for record in matched:
    if record[2] == 'Present' and record[3] == None:
        count_present_no_input += 1
    if record[2] != 'Present' and record[3] == None:
        count_absent_no_input += 1

count = 0
for image in recorded_images:
    if image[2] != 'Present':
        count += 1
print("input signals:", len(input_signals))
print("recorded images:", len(recorded_images))
print("matched:", len(matched))
print("present with no input: ", count_present_no_input, (count_present_no_input/len(recorded_images))*100, "%" )
print("total non-present: ", count)
print("non-present with no input: ", count_absent_no_input)
print("non-present with input: ", count - count_absent_no_input)

f = open("output.txt", "w")
f.write('\n'.join(map(str,matched)))
f.close()

#plt.scatter(x, record_count)
#plt.ylabel('record stats')
#plt.show()