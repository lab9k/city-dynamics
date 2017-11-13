import pandas as pd
import os


def parse_google(conn, tablename='popular_times', path='data'):

	location_files = [x for x in os.listdir(path) if x.startswith('locations')]

	locations = pd.DataFrame()
	for file in location_files:
	    locations = pd.concat([locations,
	                          pd.read_csv(path + '\\' + file, sep=';')])
	    
	locations.drop('Unnamed: 0',axis=1, inplace=True)
	locations.address = locations.address.str.replace(',',' ')

	measures = pd.read_csv(path + r'\ams_google_data.csv',
	                  encoding='cp1252')

	_, measures['Location_address'] = measures.search_term.str.split('  ',1).str
	measures.drop('name', axis=1, inplace=True)

	google_pop_times = measures.merge(locations,left_on='Location_address',right_on='address')

	to_drop = ['batch','batch_time',
	           'search_term','Location_address',
	           'place_id','rating','popular_times']

	google_pop_times.drop(to_drop, axis=1, inplace=True)

	google_pop_times.scrape_time = pd.to_datetime(google_pop_times.scrape_time)

	google_pop_times.to_sql(name=tablename, con=conn, index=False, if_exists='replace')
