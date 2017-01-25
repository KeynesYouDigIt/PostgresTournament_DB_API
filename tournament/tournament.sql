-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE DATABASE tournament;

CREATE TABLE players (
	p_id 	    serial PRIMARY KEY,
	name	    varchar(20),
	ranking	    integer NOT NULL,
	wins        integer NOT NULL DEFAULT 0,
	matches     integer NOT NULL DEFAULT 0
);

CREATE TABLE match_ledger (
    rnd             integer NOT NULL,
    match           serial NOT NULL,
    PRIMARY KEY     (rnd, match)
);

--example working insert
--INSERT INTO players  (name, ranking) VALUES ("name", 1)