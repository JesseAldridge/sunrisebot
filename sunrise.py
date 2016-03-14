from datetime import datetime, timedelta
import ephem
import csv
from pytz import timezone
import pytz
import random 

def to_flag(country_code):
    a = 0x1f1e6
    out = [chr(a + ord(i) - ord('A')) for i in country_code.upper()]
    return ''.join(out)

def sunrise_times(lat, lon):
	city = ephem.Observer()
	city.pressure = 0
	city.horizon = '-0:34'
	city.lat, city.lon = lat, lon
	city.date = datetime.utcnow()
	after = str(city.next_rising(ephem.Sun(), use_center = True))
	after_time = datetime.strptime(after, '%Y/%m/%d %H:%M:%S')
	prev = str(city.previous_rising(ephem.Sun(), use_center = True))
	prev_time = datetime.strptime(prev, '%Y/%m/%d %H:%M:%S')
	return prev_time, after_time

def closest_to_sunrise(info_array):
	current_time = datetime.utcnow()
	later = filter(lambda d: d['date'] > current_time, info_array)
	after_date = min(later, key = lambda d: d['date'])
	earlier = filter(lambda d: d['date'] < current_time, info_array)
	prev_date = max(earlier, key = lambda d: d['date'])
	diff = current_time - prev_date['date']
	other_diff = after_date['date'] - current_time
	if diff < other_diff:
		return prev_date, True
	else:
		return after_date, False

def get_country_name(country_code):
	with open('countries.txt') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=',', fieldnames = ['name', 'code'])
		for row in reader:
			code = row['code']
			if country_code == code:
				return row['name']

def get_emoji_string():
	rare_emoji = [' 🐓']
	emoji_string = ' 🌞'
	if random.randint(1,50) == 2:
		emoji_string.append(random.choice(rare_emoji))
	return emoji_string

def prepare_city_data():
	arr = []
	with open('city_data.txt') as csvfile:
		reader = csv.DictReader(csvfile, delimiter='\t', fieldnames = ['name', 'lat', 'long', 'timezone', 'population', 'country_code'])
		for row in reader:
			population = int(row['population'])
			previous_sunrise, next_sunrise = sunrise_times(row['lat'], row['long'])
			for sunrise_date in [previous_sunrise, next_sunrise]:
				arr.append({'date': sunrise_date, 'city': row['name'], 'population': population, 'country_code': row['country_code']})
	return arr

def generate_cute_tweet(rise_phrase, time_phrase, city, country, flag):
	emoji_beginning = "🌅🌅🌅 "
	emoji_end = get_emoji_string()
	greeting = random.choice(["Mornin'", "Good morning"])
	option1 = "The sun %(rise_phrase)s above %(city)s, %(country)s %(flag)s %(time_phrase)s" % locals()
	option2 = "%(greeting)s, %(city)s, %(country)s! %(flag)s The sun %(rise_phrase)s above you %(time_phrase)s" % locals()
	return emoji_beginning + random.choice([option1,option2]) + emoji_end


def get_sunrise():
	winner, previous = closest_to_sunrise(prepare_city_data())
	current_time = datetime.utcnow()
	time_diff = (winner['date'] - current_time).seconds
	time_phrase = 'right now'
	rise_phrase = 'is rising'
	if previous:
		time_diff = (current_time - winner['date']).seconds
	if time_diff >= 120:
		if previous:
			time_phrase = "%s minutes ago" %(time_diff//60)
			rise_phrase = "rose"
		else:
			time_phrase = "%s minutes from now" %(time_diff//60)
			rise_phrase = "will rise"
	return generate_cute_tweet(rise_phrase, time_phrase, winner['city'], get_country_name(winner['country_code']), to_flag(winner['country_code']))


if __name__ == "__main__":
	print(get_sunrise())








