from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import mysql.connector as mysql


def get_html(url: str):
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0"
        },
    )
    response = urlopen(request, timeout=2)
    html = response.read()
    return html


def get_href(tag):
    try:
        url: str = tag["href"]
        return url
    except KeyError:
        return None


def insert_url(url: str, cursor: mysql.cursor.MySQLCursor):
    try:
        cursor.execute(f'INSERT INTO paginas VALUES ("{url}", false)')
    except mysql.errors.IntegrityError:
        return


def set_url_as_visited(url: str, cursor: mysql.cursor.MySQLCursor):
    cursor.execute(f'UPDATE paginas SET status=TRUE WHERE url="{url}"')


def save_to_database(pagina: str, cursor: mysql.cursor.MySQLCursor):
    print(f"Checking: {pagina}")
    try:
        html = get_html(pagina)
    except Exception:
        return
    soup = BeautifulSoup(html, "html.parser")
    links = soup.select("a")
    for i in links:
        url = get_href(i)
        if url is None or not url.startswith("http"):
            continue
        insert_url(url, cursor)


def get_number_of_entries(cursor):
    cursor.execute("SELECT * FROM paginas")
    rows = cursor.fetchall()
    return len(rows)


conexion = mysql.connect(host="localhost", user="root", passwd="", db="paginas")
cursor = conexion.cursor(buffered=True)

website = input("Ingrese una pagina web: ")
save_to_database(website, cursor)

try:
    while True:
        cursor.execute("SELECT * FROM paginas WHERE status=FALSE")
        pagina = cursor.fetchone()
        if not pagina:
            break
        url = pagina[0]
        try:
            save_to_database(url, cursor)
        except Exception:
            set_url_as_visited(url, cursor)
            continue
        set_url_as_visited(url, cursor)
        entries_number = get_number_of_entries(cursor)
        print(f"Entradas: {entries_number}")
        conexion.commit()
except KeyboardInterrupt:
    pass

conexion.close()
