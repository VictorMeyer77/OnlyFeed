
-- steam --

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

-- recommandation --

create table if not exists of_game_analysis (id SERIAL PRIMARY KEY,
                                             id_game INT,
                                             date_maj TIMESTAMP,
                                             graphic INT,
                                             gameplay INT,
                                             lifetime INT,
                                             immersion INT,
                                             extern INT);

create table if not exists of_words_by_critera (id SERIAL PRIMARY KEY,
                                                word VARCHAR,
                                                critera_id INT);

create table if not exists of_game_recommandation (id SERIAL PRIMARY KEY,
                                                   of_user_id INTEGER,
                                                   game_id INT,
                                                   model_id INT,
                                                   date_create TIMESTAMP);

create table if not exists of_game_recommandation_model (id SERIAL PRIMARY KEY,
                                                   model_name VARCHAR,
                                                   recommandation_type SMALLINT,
                                                   note DECIMAL,
                                                   nb_test INT,
                                                   near_neight INT,
                                                   alpha INT,
                                                   nb_game_by_cat INT,
                                                   date_maj TIMESTAMP);

create table if not exists of_model_test (id SERIAL PRIMARY KEY,
                                                   id_model INT,
                                                   id_game_test INT,
                                                   id_game_near INT,
                                                   id_game_other_one INT,
                                                   id_game_other_two INT,
                                                   date_create TIMESTAMP);

create table if not exists of_model_test_result (id SERIAL PRIMARY KEY,
                                                   id_test INT,
                                                   id_user INT,
                                                   result INT,
                                                   date_create TIMESTAMP);

create table if not exists of_game_evaluation (id SERIAL PRIMARY KEY,
                                               of_user_id INTEGER,
                                               game_id INT,
                                               rate SMALLINT,
                                               date_create TIMESTAMP);

-- chatbot --

CREATE TABLE if not exists of_user (id SERIAL PRIMARY KEY,
                                    username VARCHAR,
                                    email VARCHAR,
                                    age SMALLINT);

CREATE TABLE if not exists  of_chatbot_message (id SERIAL PRIMARY KEY,
                                                id_user INT,
                                                type SMALLINT,
                                                date_send TIMESTAMP,
                                                content TEXT);


-- défault insertion --

insert into of_words_by_critera (critera_id, word) VALUES (0, 'graphic');
insert into of_words_by_critera (critera_id, word) VALUES (0, 'visual');
insert into of_words_by_critera (critera_id, word) VALUES (0, 'illustration');
insert into of_words_by_critera (critera_id, word) VALUES (1, 'gameplay');
insert into of_words_by_critera (critera_id, word) VALUES (1, 'playability');
insert into of_words_by_critera (critera_id, word) VALUES (2, 'lifetime');
insert into of_words_by_critera (critera_id, word) VALUES (2, 'durability');
insert into of_words_by_critera (critera_id, word) VALUES (2, 'length');
insert into of_words_by_critera (critera_id, word) VALUES (3, 'music');
insert into of_words_by_critera (critera_id, word) VALUES (3, 'history');
insert into of_words_by_critera (critera_id, word) VALUES (4, 'multiplayer');
insert into of_words_by_critera (critera_id, word) VALUES (4, 'community');