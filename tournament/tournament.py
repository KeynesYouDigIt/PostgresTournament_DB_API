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
                "SELECT * FROM players_by_wins"
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
        "select * from players_by_wins"
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
    # curs.execute(
    #     "UPDATE players SET matches = matches + 1 WHERE p_id in"
    #     "(%(win)s, %(lose)s)",
    #     {'win': winner, 'lose': loser}
    # )
    round_to_report = newRound()

    curs.execute(
        "INSERT INTO match_ledger (round_of_play, winner, loser)"
        " VALUES"
        " (%(round)s, %(win)s, %(lose)s)",
        {'round': round_to_report, 'win': winner, 'lose': loser}
    )

    print("note - match ledger auto increments." +
          "if a match before this was not registered, it will not be added" +
          "to the ledger chronologically." +
          "\n\n -- The ledger is not used to create matchups but for logging" +
          "purposes only, so this only effects" +
          " record keeping.")

    conn.commit()
    print_status_and_close(curs, conn)


def newRound():
    """Creates a new round and registres it in match ledger table
    chronologically, functionality needed for swissPairings and report match.

    This function could be removed if a swiss pairing was created for each
    report match, but the testing scripts calls the functions separately, so I
    decided to keep them decoupled.

    The tests can be passed without this function but not if the database is
    normalized, as the match ledger and players tables being connected means
    the tables must be updated at the same time.

    it returns a current round so matches can be recorded under the correct
    round.
    """
    conn = connect()
    curs = conn.cursor()
    curs.execute(
                "SELECT round_of_play FROM match_ledger"
                " ORDER BY round_of_play DESC"
    )
    last_round = curs.fetchone()
    print 'last round'
    print last_round
    if not last_round:
        last_round = 0
    else:
        last_round = last_round[0]

    this_round = last_round + 1

    curs.execute(
        "INSERT INTO match_ledger (round_of_play) VALUES ((%(this_round)s))",
        {'this_round': this_round}
    )
    conn.commit()
    print_status_and_close(curs, conn)

    return this_round


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
    newRound()
    curs.execute(
        "SELECT * FROM players_by_wins"
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
