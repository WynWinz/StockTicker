from yahoo_finance import Share
from itertools import cycle
import pygame
import time
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

def main():

	# Initialize and display window
	screen, display_width, display_height = init_screen()

	# Initialize variables
	clock = pygame.time.Clock()

	ticker_exit = False
	ticker_start = True

	# Create rectangle for clearing part of screen
	fill_rect = pygame.Surface((display_width, 100))
	rect = pygame.draw.rect(fill_rect, blue, (0, 2 * display_height / 7, display_width, 100))

	# Display title picture
	draw_image(screen, 'Pharmacy.png', display_width, display_height)

	# Display leaderboard title
	draw_title(screen, display_width, display_height)

	# Display leaderboard info
	draw_leaderboard(screen, display_width, display_height)

	# Update screen
	pygame.display.update()
	
	# Open file with stock symbols
	stocks = open("stocks.txt", 'r')

	# Cycle through stocks gathering stock data
	for symbol in cycle(stocks):
		symbol = symbol.replace('\n', '')
		symbol = symbol.replace(' ', '')
		cur_stock = Share(symbol)

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
				clock.tick(60)

			# Exit game
			if ticker_exit:
				break

def init_screen():
	pygame.init()
	infoObject = pygame.display.Info()
	display_width = infoObject.current_w
	display_height = infoObject.current_h
	screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
	return screen, display_width, display_height

def draw_image(screen, image_name, width, height):
	image = pygame.image.load(image_name)
	img_rect = image.get_rect()
	img_rect.center = (width / 2, height / 8)
	screen.blit(image, img_rect)

def draw_title(screen, width, height):
	title_text = pygame.font.SysFont('Century Schoolbook', 80)
	title_label = title_text.render('Investment League Leaderboard', 1, pitt_blue)
	text_rect = title_label.get_rect()
	text_rect.center = (width / 2, height / 2)
	screen.blit(title_label, text_rect)
	pygame.display.update()

def get_credentials():
	config = configparser.ConfigParser()
	config.read('investopedia.ini')
	email = config['LoginCredentials']['Email']
	password = config['LoginCredentials']['Password']

	return email, password

def draw_leaderboard(screen, width, height):
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
	if '-' in stock_change:
		price_label = large_text.render(stock_price, 1, red)
		change_label = large_text.render(stock_change, 1, red)
	else:
		price_label = large_text.render(stock_price, 1, green)
		change_label = large_text.render(stock_change, 1, green)

	return price_label, change_label

def handle_events():
	ticker_exit = False
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			# Exit game if escape pressed
		    if event.key == pygame.K_ESCAPE:
		        ticker_exit = True
		        break

	return ticker_exit

def display_stock_info(screen, x, height):
	x_delta = 0

	for i in range(0, len(stock_list), 6):
		screen.blit(stock_list[i], (x + x_delta, 2 * height / 7))
		screen.blit(stock_list[i + 1], (x + x_delta + stock_list[i + 3] + 10, 2 * height / 7))
		screen.blit(stock_list[i + 2], (x + x_delta + stock_list[i + 3] + stock_list[i + 4] + 20, 2 * height / 7))
		x_delta = x_delta + stock_list[i + 3] + stock_list[i + 4] + stock_list[i + 5] + 30

if __name__ == '__main__':
	main()