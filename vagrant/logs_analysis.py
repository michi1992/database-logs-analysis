# An HTTP server that remembers your name (in a cookie)

import psycopg2
import datetime

DATABASE_NAME = "news"

def popular_articles():
    # Connect to an existing database
    conn = psycopg2.connect(database=DATABASE_NAME)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Query the database and obtain data as Python objects
    query = """
    SELECT articles.title, count(log.path) AS views
    FROM articles LEFT JOIN log
    ON log.path LIKE concat('%',articles.slug)
    GROUP BY articles.title
    ORDER BY views DESC
    LIMIT 5;
    """
    cur.execute(query)

    pop_articles = cur.fetchall()

    #print the top 5 articles
    for pop_article in pop_articles:
        output_string = "\"" + pop_article[0] + "\" - " + str(pop_article[1]) + " views"
        print(output_string)

    # Close communication with the database
    cur.close()
    conn.close()

    return pop_articles


def popular_authors():
    # Connect to an existing database
    conn = psycopg2.connect(database=DATABASE_NAME)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Query the database and obtain data as Python objects
    subquery = """
    SELECT authors.name, articles.slug
    FROM articles JOIN authors
    ON articles.author = authors.id
    """
    query = """
    SELECT subq.name, count(log.path) AS views
    FROM ({}) AS subq LEFT JOIN log
    ON log.path LIKE concat('%',subq.slug)
    GROUP BY subq.name
    ORDER BY views DESC
    LIMIT 5;
    """.format(subquery)
    cur.execute(query)

    pop_authors = cur.fetchall()

    #print the top 5 authors
    for pop_author in pop_authors:
        output_string = "\"" + pop_author[0] + "\" - " + str(pop_author[1]) + " views"
        print(output_string)

    # Close communication with the database
    cur.close()
    conn.close()

    return pop_authors


def request_errors_analysis():
    # Connect to an existing database
    conn = psycopg2.connect(database=DATABASE_NAME)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    #Create a view in the database
    sql_command = """
    CREATE OR REPLACE VIEW request_stats AS
    SELECT CAST(time as date) AS request_date, count(*) AS total_requests,
    SUM(CASE WHEN status='404 NOT FOUND' THEN 1 ELSE 0 END) AS bad_requests
    FROM log
    GROUP BY request_date;
    """
    cur.execute(sql_command)

    # Query the database and obtain data as Python objects
    # I have also tried 'HAVING error_rate > 1;' instead of
    # 'WHERE bad_requests*100/total_requests > 1;' but somehow it's not working.
    query = """
    SELECT request_date, bad_requests*100/total_requests AS error_rate
    FROM request_stats
    WHERE bad_requests*100/total_requests > 1;
    """
    cur.execute(query)

    error_rates = cur.fetchall()

    #print the error_rates
    for error_rate in error_rates:
        output_string = "\"" + error_rate[0].strftime('%B %d, %Y') + "\" - " + str(error_rate[1]) + "% errors"
        print(output_string)

    # Close communication with the database
    cur.close()
    conn.close()

    return error_rates



if __name__ == '__main__':
    print("\nTop 5 articles:")
    popular_articles()

    print("\nTop 5 authors:")
    popular_authors()

    print("\nDays with error rates higher than 1%:")
    request_errors_analysis()
    print("\n")
