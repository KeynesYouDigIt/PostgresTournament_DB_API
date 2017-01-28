-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament

CREATE TABLE players (
	p_id 	    serial PRIMARY KEY,
	name	    varchar(20),
	ranking	    integer
);

CREATE TABLE match_ledger (
    round_of_play   integer NOT NULL,
    match           serial NOT NULL,
    winner          integer REFERENCES  players (p_id),
    loser           integer REFERENCES players (p_id),
    PRIMARY KEY     (round_of_play, match)
);

CREATE VIEW  players_by_wins AS
    SELECT p.p_id, p.name,
    count(ml_winner_count.winner) as win_count,
    count(ml_match_count.winner + ml_match_count.loser) as matches
    FROM players p
    LEFT OUTER JOIN match_ledger ml_winner_count
        ON p.p_id = ml_winner_count.winner
    LEFT OUTER JOIN match_ledger ml_match_count
        ON p.p_id = ml_match_count.winner OR p.p_id = ml_match_count.loser
    GROUP BY p.p_id
    ORDER BY win_count desc;

--example working insert
--INSERT INTO players  (name, ranking) VALUES ("name", 1)