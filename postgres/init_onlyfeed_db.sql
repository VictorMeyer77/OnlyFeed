

create table if not exists steam_video_games (id INT PRIMARY KEY,
                                              name VARCHAR,
                                              description VARCHAR,
                                              age SMALLINT,
                                              languages VARCHAR,
                                              windows BOOLEAN,
                                              mac BOOLEAN,
                                              linux BOOLEAN,
                                              windows_requirements VARCHAR,
                                              mac_requirements VARCHAR,
                                              linux_requirements VARCHAR,
                                              publisher VARCHAR,
                                              developers VARCHAR,
                                              price DECIMAL,
                                              currency VARCHAR,
                                              categories VARCHAR,
                                              genres VARCHAR,
                                              release_date TIMESTAMP);


create table if not exists steam_game_reviews (id INT PRIMARY KEY,
                                              author_id BIGINT,
                                              date_create TIMESTAMP,
                                              review TEXT);


create table if not exists of_game_analysis(id SERIAL PRIMARY KEY,
                                         id_game INT,
                                         graphism DECIMAL,
                                         gameplay DECIMAL,
                                         lifetime DECIMAL,
                                         immersion DECIMAL,
                                         extern DECIMAL);


CREATE TABLE if not exists of_user (id SERIAL PRIMARY KEY,
                                         username VARCHAR,
                                         email VARCHAR,
                                         age SMALLINT);


CREATE TABLE if not exists  of_chatbot_message (id SERIAL PRIMARY KEY,
                                             id_user INT,
                                             type SMALLINT,
                                             date_send TIMESTAMP,
                                             content TEXT);
