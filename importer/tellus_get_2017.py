import numpy as np

# open files
infilename = '/home/rluijk/Documents/tellus/tellus_data_tellus_expanded_jan2016-okt2017.csv'
outfilename = '/home/rluijk/Documents/tellus/tellus2017.csv'

# write 2017 to new file
infile = open(infilename, 'r', encoding='utf-16-le')
outfile = open(outfilename, 'w')

# read header
header = np.array(next(infile).strip('\n').split('\t'))

# check which column contains timestamp
tijd_indx = np.where(np.array(header) == 'Tijd Tot')[0][0]

# index for relevant columns
usecols = ['Tellus Id', 'Latitude', 'Longitude', 'Meetwaarde', 'Richting', 'Richting 1', 'Richting 2', 'Tijd Van', 'Tijd Tot', 'Representatief']
col_indx = np.where([col in usecols for col in header])[0]

# write header
header = header[col_indx]
outfile.write(';'.join(header) + '\n')

# check for year (2017) and write to new file
for row in infile:
    row = row.split('\t')
    if row[tijd_indx][6:10] == '2017':
        outfile.write(';'.join(np.array(row)[col_indx]) + '\n')

# close files
outfile.close()
infile.close()