""" 
Author: Edwin Mellett
Date Started: 4/3/17
Date Last Modified: 4/6/17

Stock ticker for the Pitt Pharmacy School.
"""

from yahoo_finance import Share
from itertools import cycle
import pygame
import datetime
import configparser
import re
from robobrowser import RoboBrowser
from lxml import etree

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
pitt_blue = (25, 40, 87)
pitt_gold = (181, 161, 103)

stock_list = []

# Set to false to disable full screen.
enable_fullscreen = True

def main():
	# Initialize and display window
	screen, display_width, display_height = init_screen()

	# Initialize variables
	clock = pygame.time.Clock()

	ticker_exit = False
	ticker_start = True

	# Create rectangle for clearing part of screen
	fill_rect = pygame.Surface((display_width, 100))
	rect = pygame.draw.rect(fill_rect, black, (0, 2 * display_height / 7, display_width, 100))

	# Display title picture
	draw_image(screen, 'Pharmacy.png', display_width / 2, display_height / 8)

	# Display leaderboard title
	draw_title(screen, display_width / 2, display_height / 2)

	# Display leaderboard info
	draw_leaderboard(screen, display_width, display_height)
	last_day = datetime.datetime.now().day

	# Update screen
	pygame.display.update()
	
	# Open file with stock symbols
	stocks = open("stocks.txt", 'r')

	# Cycle through stocks gathering stock data
	for symbol in cycle(stocks):
		symbol = symbol.replace('\n', '')
		symbol = symbol.replace(' ', '')

		# Attempt to retrieve stock data.
		# Skip stock if an exception is raised.
		try:
			cur_stock = Share(symbol)
		except:
			continue


		# Prepare text
		large_text = pygame.font.SysFont('arial', 80)
		symbol_label = large_text.render(symbol, 1, white)

		stock_price = cur_stock.get_price()
		stock_change = cur_stock.get_change()

		if stock_price is None or stock_change is None:
			continue

		# Render stock price and change labels
		price_label, change_label = render_stock_info(stock_price, stock_change, large_text)
			
		# Get text widths
		symbol_width = symbol_label.get_width()
		price_width = price_label.get_width()
		change_width = change_label.get_width()

		# Add stock info to list
		stock_list.append(symbol_label)
		stock_list.append(price_label)
		stock_list.append(change_label)
		stock_list.append(symbol_width)
		stock_list.append(price_width)
		stock_list.append(change_width)

		# Wait for info on 5 stocks before starting to display
		if len(stock_list) > 24:
			# Determine starting point for drawing stock info
			if not ticker_start:
				x_coordinate = 0
				del stock_list[:6]
			else:
				x_coordinate = display_width

			# Set to false (Should only be True on start of script)
			ticker_start = False
			# Calculate scroll length based on width of stock info
			scroll_length = -1 * (stock_list[3] + stock_list[4] + stock_list[5] + 30)

			while x_coordinate > scroll_length:
				# Handle events
				ticker_exit = handle_events()

				# Exit while loop
				if ticker_exit:
					break

				# Refresh screen
				screen.blit(fill_rect, (0, 2 * display_height / 7))
				
				# Display stock info
				display_stock_info(screen, x_coordinate, display_height)

				# Update screen
				pygame.display.update()
				x_coordinate = x_coordinate - 3
				clock.tick(45)

			# Update leaderboard once a day at 11 pm
			cur_hour = datetime.datetime.now().hour
			cur_day = datetime.datetime.now().day
			if(cur_day != last_day and cur_hour == 23):
				draw_leaderboard(screen, display_width, display_height)
				last_day = cur_day

			# Exit game
			if ticker_exit:
				break

def init_screen():
	"""
	Initialize fullscreen display.

	Returns:
		A tuple containing the screen object
		and the screen's width and height.
	"""
	pygame.init()
	infoObject = pygame.display.Info()
	width = infoObject.current_w
	height = infoObject.current_h
	if enable_fullscreen:
		screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
	else:
		screen = pygame.display.set_mode((width - 100, height - 100))
	return screen, width, height

def draw_image(screen, image_name, x, y):
	"""
	Draws a given image on the screen.

	Args:
		screen: the display object
		image_name: name of image file
		x: x coordinate to start drawing
		y: y coordinate to start drawing
	"""
	image = pygame.image.load(image_name)
	img_rect = image.get_rect()
	img_rect.center = (x, y)
	screen.blit(image, img_rect)

def draw_title(screen, x, y):
	"""
	Draws the leaderboard title on the screen.

	Args:
		screen: the display object
		x: x coordinate to start drawing
		y: y coordinate to start drawing
	"""
	title_text = pygame.font.SysFont('Century Schoolbook', 80)
	title_label = title_text.render('Investment League Leaderboard', 1, pitt_blue)
	text_rect = title_label.get_rect()
	text_rect.center = (x, y)
	screen.blit(title_label, text_rect)
	pygame.display.update()

def get_credentials():
	"""
	Retrieves credentials from config file.

	Returns:
		A tuple containing the email and password necessary for login.
	"""
	config = configparser.ConfigParser()
	config.read('investopedia.ini')
	email = config['LoginCredentials']['Email']
	password = config['LoginCredentials']['Password']

	return email, password

def clear_leaderboard(screen, width, height):
	"""
	Draws over the current leaderboard to clear it.

	Args:
		screen: the display object
		width: display width
		height: display height
	"""
	clear_rect = pygame.Surface((width, height / 2))
	rect = pygame.draw.rect(clear_rect, black, (0, height / 2, width, 9 * height / 16))
	screen.blit(clear_rect, (0, 9 * height / 16))

def draw_leaderboard(screen, width, height):
	"""
	Retrieve data from investopedia and draw leaderboard on screen.

	Args:
		screen: the display object
		width: display width
		height: display height
	"""
	clear_leaderboard(screen, width, height)
	email, password = get_credentials()

	# Use login credentials to access leaderboard
	base_url = 'http://www.investopedia.com/accounts/login.aspx?'
	browser = RoboBrowser(parser='lxml', history=True)
	browser.open(base_url)
	form = browser.get_form(id='account-api-form')
	form['email'] = email
	form['password'] = password

	browser.submit_form(form)
	browser.open('http://www.investopedia.com/simulator/ranking/')
	leaderboard = browser.select('tr')

	x = width / 15
	y = 9 * height / 16

	for i in range(1, 11):
		data = leaderboard[i].text.replace('\n', '')
		data = data.replace('.                ', '')
		if i == 10:
			data = data[2:]
		else:
			data = data[1:]
		username = ''
		for char in data:
			if char == '(':
				break
			else:
				username = username + char

		if len(username) > 30:
			username = username[:30]
		
		# Display leaderboard info
		info = '{}. {}'.format(i, username)
		text = pygame.font.SysFont('Century Schoolbook', 40)
		label = text.render(info, 1, pitt_gold)
		screen.blit(label, (x, y))
		pygame.display.update()

		if i == 5:
			x = 11 * width / 21
			y = 9 * height / 16
		else:
			y = y + 50


def render_stock_info(stock_price, stock_change, large_text):
	"""
	Renders price and day's change labels.

	Args:
		stock_price: current stock price
		stock_change: current dollar change in stock price
		large_text: font used to render labels

	Returns:
		A tuple containing the price and change labels.
	"""
	if '-' in stock_change:
		price_label = large_text.render(stock_price, 1, red)
		change_label = large_text.render(stock_change, 1, red)
	else:
		price_label = large_text.render(stock_price, 1, green)
		change_label = large_text.render(stock_change, 1, green)

	return price_label, change_label

def handle_events():
	"""
	Event handler for the stock ticker.

	Returns:
		A boolean indicating if the program should exit.
	"""
	ticker_exit = False
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			# Exit game if escape pressed
		    if event.key == pygame.K_ESCAPE:
		        ticker_exit = True
		        break

	return ticker_exit

def display_stock_info(screen, x, y):
	"""
	Draw stocks to screen.

	Args:
		screen: the display object
		x: x coordinate to start drawing
		y: y coordinate to start drawing
	"""
	x_delta = 0

	for i in range(0, len(stock_list), 6):
		screen.blit(stock_list[i], (x + x_delta, 2 * y / 7))
		screen.blit(stock_list[i + 1], (x + x_delta + stock_list[i + 3] + 10, 2 * y / 7))
		screen.blit(stock_list[i + 2], (x + x_delta + stock_list[i + 3] + stock_list[i + 4] + 20, 2 * y / 7))
		x_delta = x_delta + stock_list[i + 3] + stock_list[i + 4] + stock_list[i + 5] + 30

if __name__ == '__main__':
	main()