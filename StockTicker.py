from yahoo_finance import Share
from itertools import cycle
import pygame
import time

def main():
	# Open file with stock symbols
	stocks = open("stocks.txt", 'r')

	# Initialize and display window
	pygame.init()
	infoObject = pygame.display.Info()
	display_width = infoObject.current_w
	display_height = infoObject.current_h
	screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

	# Initialize variable
	stock_list = []

	black = (0, 0, 0)
	white = (255, 255, 255)
	red = (255, 0, 0)
	green = (0, 255, 0)
	blue = (0, 0, 255)

	clock = pygame.time.Clock()
	game_exit = False
	game_start = True

	fill_rect = pygame.Surface((display_width, 100))
	rect = pygame.draw.rect(fill_rect, black, (0, display_height / 2, display_width, 100))
	
	# Cycle through stocks gathering stock data
	for symbol in cycle(stocks):
		symbol = symbol.replace('\n', '')
		symbol = symbol.replace(' ', '')
		cur_stock = Share(symbol)

		# Prepare text
		large_text = pygame.font.SysFont('arial', 60)
		symbol_label = large_text.render(symbol, 1, white)

		stock_price = cur_stock.get_price()
		stock_change = cur_stock.get_change()

		# Render positive or negative price and change
		if '-' in stock_change:
			price_label = large_text.render(stock_price, 1, red)
			change_label = large_text.render(stock_change, 1, red)
		else:
			price_label = large_text.render(stock_price, 1, green)
			change_label = large_text.render(stock_change, 1, green)
			
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

		if len(stock_list) > 24:
			if not game_start:
				x_coordinate = 0
				del stock_list[:6]
			else:
				x_coordinate = display_width

			game_start = False
			scroll_length = -1 * (stock_list[3] + stock_list[4] + stock_list[5] + 30)

			while x_coordinate > scroll_length:
				# Handle events
				for event in pygame.event.get():
					if event.type == pygame.KEYDOWN:
						# Exit game if escape pressed
					    if event.key == pygame.K_ESCAPE:
					        game_exit = True
					        break

				# Exit while loop
				if game_exit:
					break

				# Refresh screen
				screen.blit(fill_rect, (0, display_height / 2))
				x_delta = 0

				for i in range(0, len(stock_list), 6):
					screen.blit(stock_list[i], (x_coordinate + x_delta, display_height / 2))
					screen.blit(stock_list[i + 1], (x_coordinate + x_delta + stock_list[i + 3] + 10, display_height / 2))
					screen.blit(stock_list[i + 2], (x_coordinate + x_delta + stock_list[i + 3] + stock_list[i + 4] + 20, display_height / 2))
					x_delta = x_delta + stock_list[i + 3] + stock_list[i + 4] + stock_list[i + 5] + 30

				pygame.display.update()
				x_coordinate = x_coordinate - 3
				clock.tick(60)

			# Exit game
			if game_exit:
				break

if __name__ == '__main__':
	main()