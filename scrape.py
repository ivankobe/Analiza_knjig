from os import error
import re
import orodja


URL = 'https://www.goodreads.com/list/show/'
NUM_PAGES = 100


def scrape_titles():
    """
    Creates and returns a dictionary containing ten thousand
    best-rated books on goodreads. Keys are book titles (str)
    and values are urls of sites containing additional information.
    """

    pattern = re.compile(
        r'<a title="(?P<title>.+?)" '
        r'href="(?P<href>.+?)">\n')

    movies = dict()
    for i in range(NUM_PAGES):
        num = i + 1
        url = f'https://www.goodreads.com/list/show/{num}'
        filename = f'html_files/lists/top_rated_books_page_{num}'
        orodja.shrani_spletno_stran(url, filename)
        content = orodja.vsebina_datoteke(filename)
        for match in pattern.finditer(content):
            title = match['title']
            title = title.replace('&#39;', "'")
            href = 'https://www.goodreads.com' + match['href']
            movies[title] = href
    return movies


def scrape_books(titles_dict):

    def pattern_author(title):
        return re.compile(
                rf'<!DOCTYPE html>.*'
                rf'<title>{title}.*by (?P<author>.*)</title>',
                re.DOTALL
            )
    
    pattern_rating = re.compile(
        r'<span itemprop="ratingValue">\n'
        r'.*(?P<rating>\d\.\d\d)\n'
        r'</span>',
        re.DOTALL

    )

    pattern_publication_year_fst = re.compile(
        r'<nobr class="greyText">\n'
        r'\s*\(first published.*\D(?P<publication_year>(?<!-)-?\d{1,4})\)\n'
        r'\s*</nobr>'
    )

    pattern_publication_year = re.compile(
        r'Published\n'
        r'.*[a-zA-Z]{4,12} (\d{1,2}th )?(?P<publication_year>\d{1,4}(?!th))'
    )

    pattern_num_pages = re.compile(
        r'<span itemprop="numberOfPages">(?P<num>\d{1,5}) pages</span></div>'
    )

    pattern_genres = re.compile(
        r"""<a class="actionLinkLite bookPageGenreLink" href="/genres/[a-z]{3,10}">(?P<genre>[A-Z][a-z]{2,9})</a>"""
    )

    book_list = list()
    genres_list = list()
    count = 1

    for (title, url) in titles_dict.items():
        
        book = dict()
        filename = f'html_files/books/{title}'

        try:
            orodja.shrani_spletno_stran(url, filename)
            content = orodja.vsebina_datoteke(filename)
            book['title'] = title
            book['order'] = count
            book['author'] = pattern_author(title).findall(content)[0]
            book['rating'] = pattern_rating.findall(content)[0]
            book['num_pages'] = pattern_num_pages.findall(content)[0]
            book_list.append(book)
            genres = pattern_genres.findall(content)[0:5]
            for genre in genres:
                genre_dict = dict()
                genre_dict['title'] = title
                genre_dict['genre'] = genre
                genres_list.append(genre_dict)    
        except:
            continue

        try:
            book['publication_year'] = pattern_publication_year_fst.findall(content)[0]
        except IndexError as e:
            try:
                book['publication_year'] = re.search(pattern_publication_year, content).group('publication_year')
            except:
                continue

        count += 1

    return book_list, genres_list


if __name__=="__main__":
    books, genres = scrape_books(scrape_titles())
    orodja.zapisi_csv(
        books,
        ['title', 'author', 'order', 'rating', 'publication_year', 'num_pages'],
        'data/books.csv'
        )
    orodja.zapisi_csv(
        genres,
        ['title', 'genre'],
        'data/genres.csv'
    )
