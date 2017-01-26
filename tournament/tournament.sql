-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE DATABASE tournament;

\connect tournament

CREATE TABLE players (
	p_id 	    serial PRIMARY KEY,
	name	    varchar(20),
	ranking	    integer,
	wins        integer default 0,
	matches     integer default 0
);

CREATE TABLE match_ledger (
    rnd             integer NOT NULL,
    match           serial NOT NULL,
    PRIMARY KEY     (rnd, match)
);

CREATE VIEW  arbitrary_view_for_udacity AS
    SELECT P_id, name, wins, matches FROM players ORDER BY ranking ASC;

--example working insert
--INSERT INTO players  (name, ranking) VALUES ("name", 1)