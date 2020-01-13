import tkinter as tk
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import datetime

window = tk.Tk()
window.title("web scraper app")
window.geometry("800x550")

my_url = 'https://www.filmweb.pl/showtimes/Wroc%C5%82aw'

# opening up connection and grabbing the page
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()

# html parser
page_soup = soup(page_html, 'html.parser')

# grabs all cinemas
cinemas = page_soup.findAll('a', {'class': 'cinemaLink'})
result_cinemas = []
for cinema in cinemas:
    result_cinemas.append(cinema.text)

def get_movies():
    print('MOVIE')
    selected_cinema = cinemas_list.selection_get()
    print(f'Selected cinema: {selected_cinema}')

    # movies for selected cinema
    cinema_number_index = int(selected_cinema.find('-'))
    user_cinema_link = cinemas[int(selected_cinema[:cinema_number_index])]['href']
    cinema_url = f'https://www.filmweb.pl{user_cinema_link}'
    print(cinema_url)

    # opening up connection and grabbing the page
    cClient = uReq(cinema_url)
    page_cinema_html = cClient.read()
    cClient.close()

    # html parser
    page_cinema_soup = soup(page_cinema_html, 'html.parser')

    # grabs each movie
    containers = page_cinema_soup.findAll('li', {'class': 'sticker bottom-20'})

    # prepare movies list
    movies_info = []
    for container in containers:
        title = container.findAll('h3', {'class': 'filmPreview__title'})[0].string
        year = container.findAll('span', {'class': 'filmPreview__year'})[0].string
        movies_info.append(f'{title} | {year}')

    # show movies
    ix = 1
    for item in movies_info:
        movies_list_label.insert(ix, item)
        ix += 1

    # save results to csv file
    filename = 'movies.csv'
    f = open(filename, 'w')

    # prepare headers
    cinema_header = selected_cinema[:cinema_number_index]
    headers = 'Title; Year; Duration; Rate; Rate_Count; Genres; Hours; Description;'
    f.write(f'Cinema: {cinema_header} \n')
    f.write(f'Date: {datetime.date.today()}\n')
    f.write(headers + '\n')

    # grap info
    for container in containers:
        title = container.findAll('h3', {'class': 'filmPreview__title'})[0].string
        year = container.findAll('span', {'class': 'filmPreview__year'})[0].string
        dur = container.findAll('div', {'class': 'filmPreview__filmTime'})
        if len(dur) > 0:
            duration = dur[0].string
        else:
            duration = 'nd'
        rate = container.findAll('div', {'class': 'rateBox'})
        for item in rate:
            if item.findAll('span', {'class': 'rateBox__rate'}):
                ratee = rate[0].span.text.replace(',', '.')
                ratee_count = rate[0].findAll('span', {'class': 'rateBox__votes--count'})[0].text + ' ' + \
                              rate[0].findAll('span', {'class': 'rateBox__votes--label'})[0].text
            elif item.findAll('span', {'class': 'rateBox__noRate'}):
                ratee = 'nd'
                ratee_count = 'nd'
        desc = container.findAll('div', {'class': 'filmPreview__description'})
        if len(desc) > 0:
            description = desc[0].p.text
        else:
            description = 'nd'
        all_gen = container.findAll('div', {'class': 'filmPreview__info--genres'})
        if len(all_gen) > 0:
            all_genres = all_gen[0].ul.findAll('li')
            genres = ''
            for item in all_genres:
                genres += item.a.text + ' '
        else:
            genres = 'nd'

        all_hours = container.findAll('ul', {'class': 'hoursList'})[0].findAll('li')
        hours = ''
        for item in all_hours:
            hours += item['data-hour'] + ' '
        f.write(
            title + ';' + year + ';' + duration + ';' + ratee + ';' + ratee_count + ';' + genres + ';' + hours + ';' + description + ';' + '\n')
    f.close()

# LABELS

cinema_label = tk.Label(text="Choose cinema:", font=("Segoe", 16))
cinema_label.grid(column=0, row=1)

cinemas_list = tk.Listbox(window, width=50, height=25)
lista = result_cinemas
i = 1
for item in lista:
    cinemas_list.insert(i, f'{i-1}-{item}')
    i += 1
cinemas_list.grid(column=0, row=3, sticky="new")

movies_label = tk.Label(text="Movies:", font=("Segoe", 16))
movies_label.grid(column=1, row=1)

button = tk.Button(text='Go', bg='green', command=get_movies)
button.grid(column=0, row=5, sticky="nsew")

# empty list
movies_list_label = tk.Listbox(window, width=80, height=25)
movies_list_label.grid(column=1, row=3, sticky="new")

button_more_info = tk.Button(text='More', bg='yellow') # command=get_movie_info)
button_more_info.grid(column=1, row=5, sticky="news")

window.mainloop()
