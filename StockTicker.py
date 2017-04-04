from yahoo_finance import Share
from itertools import cycle
import configparser
import pygame
import time

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
pitt_blue = (25, 40, 87)

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

def draw_leaderboard(screen, width, height):
	config = configparser.ConfigParser()
	config.read('investopedia.ini')
	username = config['LoginCredentials']['username']
	password = config['LoginCredentials']['password']

	# TODO: Use login credentials to access leaderboard

	# TODO: Display leaderboard info

	text = pygame.font.SysFont('Century Schoolbook', 40)
	label = text.render('1. Wyn Mellett', 1, pitt_blue)
	screen.blit(label, (100, 3 * height / 4))
	pygame.display.update()

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