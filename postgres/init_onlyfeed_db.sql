
-- création des tables --

create table if not exists steam_video_games (id INT PRIMARY KEY,
                                              name VARCHAR,
                                              age SMALLINT,
                                              languages VARCHAR,
                                              windows BOOLEAN,
                                              mac BOOLEAN,
                                              linux BOOLEAN,
                                              windows_requirements VARCHAR,
                                              mac_requirements VARCHAR,
                                              linux_requirements VARCHAR,
                                              publishers VARCHAR,
                                              developers VARCHAR,
                                              price INT,
                                              currency VARCHAR,
                                              categories VARCHAR,
                                              genres VARCHAR,
                                              recommendations INT,
                                              release_date TIMESTAMP);

create table if not exists steam_invalid_game_ids (id INT PRIMARY KEY);

create table if not exists steam_game_reviews (id INT PRIMARY KEY,
                                              author_id BIGINT,
                                              game_id INT,
                                              date_create TIMESTAMP,
                                              review TEXT);

create table if not exists steam_game_reviews_flag (game_id INT PRIMARY KEY,
                                                    flag VARCHAR,
                                                    date_maj TIMESTAMP);

create table if not exists of_game_analysis (id SERIAL PRIMARY KEY,
                                             id_game INT,
                                             date_maj TIMESTAMP,
                                             graphism INT,
                                             gameplay INT,
                                             lifetime INT,
                                             immersion INT,
                                             extern INT);

create table if not exists of_words_by_critera (id SERIAL PRIMARY KEY,
                                                word VARCHAR,
                                                critera_id INT);

CREATE TABLE if not exists of_user (id SERIAL PRIMARY KEY,
                                    username VARCHAR,
                                    email VARCHAR,
                                    age SMALLINT);

CREATE TABLE if not exists  of_chatbot_message (id SERIAL PRIMARY KEY,
                                                id_user INT,
                                                type SMALLINT,
                                                date_send TIMESTAMP,
                                                content TEXT);

CREATE TABLE if not exists of_user_critera (id SERIAL PRIMARY KEY,
                                             graphism INT,
                                             gameplay INT,
                                             lifetime INT,
                                             immersion INT,
                                             extern INT,
                                             release TIMESTAMP,
                                             genre VARCHAR,
                                             price INT,
                                             age INT,
                                             plateform VARCHAR)

-- défault insertion --

insert into of_words_by_critera (critera_id, word) VALUES (0, 'graphism');
insert into of_words_by_critera (critera_id, word) VALUES (0, 'visual');
insert into of_words_by_critera (critera_id, word) VALUES (0, 'illustration');
insert into of_words_by_critera (critera_id, word) VALUES (1, 'gameplay');
insert into of_words_by_critera (critera_id, word) VALUES (1, 'playability');
insert into of_words_by_critera (critera_id, word) VALUES (2, 'lifetime');
insert into of_words_by_critera (critera_id, word) VALUES (2, 'durability');
insert into of_words_by_critera (critera_id, word) VALUES (3, 'music');
insert into of_words_by_critera (critera_id, word) VALUES (3, 'history');
insert into of_words_by_critera (critera_id, word) VALUES (4, 'multiplayer');
insert into of_words_by_critera (critera_id, word) VALUES (4, 'community');