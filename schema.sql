CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Albums CASCADE;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Tags CASCADE;
DROP TABLE IF EXISTS Tagged_with CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS Likes CASCADE;
DROP TABLE IF EXISTS Friends CASCADE;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE NOT NULL,
    password varchar(255) NOT NULL,
    first_name	varchar(255) NOT NULL,
    last_name	varchar(255) NOT NULL,
    dob	date NOT NULL,
    hometown varchar(255) NOT NULL,
    gender	ENUM('F', 'M') NOT NULL,
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Albums
(
album_id int4 AUTO_INCREMENT,
album_name varchar(255) NOT NULL,
user_id int4,
create_date	date NOT NULL,
FOREIGN KEY (user_id) REFERENCES Users(user_id),
PRIMARY KEY (album_id)
);

CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE Tags
(
word varchar(255),
PRIMARY KEY (word)
);

CREATE TABLE Tagged_with
(
picture_id int4,
word varchar(255),
FOREIGN KEY (picture_id) REFERENCES Pictures (picture_id),
FOREIGN KEY (word) REFERENCES Tags (word),
PRIMARY KEY (picture_id, word)
);

CREATE TABLE Comments
(
comment_id int4 AUTO_INCREMENT,
test	varchar(255),
c_owner int4,
c_date	date,
picture_id	int4,
FOREIGN KEY(c_owner) REFERENCES Users(user_id),
FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id),
PRIMARY KEY(comment_id)
);

CREATE TABLE Likes
(
user_id int4,
picture_id int4,
PRIMARY KEY (photo_id, user_id),
FOREIGN KEY (user_id) REFERENCES Users(user_id),
FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id)
);

CREATE TABLE Friends
(
user_id int4,
friend_id int4,
FOREIGN KEY (user_id) REFERENCES Users(user_id),
FOREIGN KEY (friend_id) REFERENCES Users(user_id),
PRIMARY KEY (user_id, friend_id)
);





INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');