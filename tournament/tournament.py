""" Tournament.
Implementation of a Swiss-system tournament

this middleware is the API for interacting with the pg database
"""

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def print_status_and_close(curs, conn):
    """ prints the status of the cursor and closes cursor and connection"""
    print('status of db request')
    print(curs.statusmessage)
    curs.close()
    conn.close()


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    curs = conn.cursor()
    curs.execute("DELETE FROM match_ledger")
    curs.execute("UPDATE players SET wins = 0,  matches = 0")
    conn.commit()
    print_status_and_close(curs, conn)


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    curs = conn.cursor()
    result = curs.execute("DELETE FROM players")
    conn.commit()
    print_status_and_close(curs, conn)
    return result


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    curs = conn.cursor()
    curs.execute("SELECT count(*) FROM players")
    result = int(curs.fetchall()[0][0])
    print_status_and_close(curs, conn)
    return result


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    curs = conn.cursor()
    curs.execute(
                "SELECT ranking FROM players ORDER BY ranking DESC"
    )

    lowest_current = curs.fetchone()
    print 'lowest curr'
    print lowest_current
    if not lowest_current:
        lowest_current = 0
    else:
        lowest_current = lowest_current[0]

    curs.execute(
                "INSERT INTO players (name, ranking) VALUES (%s, %s)",
                (name, str((lowest_current + 1)))
    )
    conn.commit()
    print_status_and_close(curs, conn)


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    swissPairings()
    conn = connect()
    curs = conn.cursor()
    curs.execute(
                "SELECT * FROM arbitrary_view_for_udacity"
    )
    result = curs.fetchall()
    print_status_and_close(curs, conn)
    return result

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    curs = conn.cursor()
    curs.execute(
        "UPDATE players SET matches = matches + 1 WHERE p_id in (%s, %s)",
        (winner, loser)
    )

    curs.execute(
        "UPDATE players SET wins = wins + 1 WHERE p_id = {}".format(winner)
    )

    print("note - match ledger auto increments." +
          "if a match before this was not registered, it will not be added to the ledger chronologically." +
          "\n\n -- The ledger is not used to create matchups but for logging purposes only, so this only effects" +
          " record keeping.")

    conn.commit()
    print_status_and_close(curs, conn)

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn = connect()
    curs = conn.cursor()
    curs.execute(
                "SELECT rnd FROM match_ledger ORDER BY rnd DESC"
    )
    last_round = curs.fetchone()
    print 'last round'
    print last_round
    if not last_round:
        last_round = 0
    else:
        last_round = last_round[0]

    curs.execute(
        "INSERT INTO match_ledger (rnd) VALUES ({})".format(last_round + 1)
    )
    conn.commit()

    curs.execute(
        "SELECT * FROM players ORDER BY wins DESC"
    )

    unranked = curs.fetchall()

    new_rank = 1
    for player in unranked:
        curs.execute(
            "UPDATE players SET ranking = %s WHERE p_id = %s",
            (str(new_rank), player[0])
        )
        new_rank += 1

    curs.execute(
        "SELECT * FROM players ORDER BY ranking ASC"
    )
    rankings = curs.fetchall()
    matches = []
    match = ()
    for plyr in rankings:
        match = match + (plyr[0],plyr[1])
        if not len(match) == 2:
             matches.append(match)
             match = ()
        print matches
        print match

    return matches
