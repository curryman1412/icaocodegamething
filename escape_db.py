import mariadb


# Database connection

def connect():
    return mariadb.connect(
        host="localhost",
        port=3000,
        user="dbproject",
        password="dbpassword",
        database="flight_game"
    )


# Find airport by ICAO code

def get_airport(ident):

    conn = connect()
    cursor = conn.cursor()

    sql = """
        SELECT ident, name, latitude_deg, longitude_deg, iso_country
        FROM airport
        WHERE LOWER(ident) = LOWER(?)
    """

    cursor.execute(sql, (ident,))

    airport = cursor.fetchone()

    cursor.close()
    conn.close()

    return airport


# Find airport by name

def find_airport(search):

    conn = connect()
    cursor = conn.cursor()

    sql = """
        SELECT ident, name, latitude_deg, longitude_deg, iso_country
        FROM airport
        WHERE LOWER(name) = LOWER(?)
           OR LOWER(name) LIKE LOWER(?)
        LIMIT 10
    """

    search_pattern = "%" + search + "%"

    cursor.execute(
        sql,
        (search, search_pattern)
    )

    airports = cursor.fetchall()

    cursor.close()
    conn.close()

    return airports


# Find nearby airports

def get_nearby_airports(latitude, longitude):

    conn = connect()
    cursor = conn.cursor()

    sql = """
        SELECT
            ident,
            name,
            latitude_deg,
            longitude_deg,
            iso_country
        FROM airport
        WHERE latitude_deg IS NOT NULL
          AND longitude_deg IS NOT NULL
          AND ident IS NOT NULL
          AND type IN (
              'large_airport',
              'medium_airport'
          )
          AND scheduled_service = 'yes'
          AND latitude_deg BETWEEN ? - 15 AND ? + 15
          AND longitude_deg BETWEEN ? - 20 AND ? + 20
    """

    cursor.execute(
        sql,
        (
            latitude,
            latitude,
            longitude,
            longitude
        )
    )

    airports = cursor.fetchall()

    cursor.close()
    conn.close()

    return airports

