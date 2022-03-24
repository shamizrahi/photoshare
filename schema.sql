CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

CREATE TABLE Users (
    user_id int4 AUTO_INCREMENT,
    email varchar(255) UNIQUE NOT NULL,
    password varchar(255) NOT NULL,
    first_name	varchar(255) NOT NULL,
    last_name	varchar(255) NOT NULL,
    dob	date NOT NULL,
    hometown varchar(255) NOT NULL,
    gender varchar(255) NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE Albums
(
	album_id int4 AUTO_INCREMENT,
	album_name varchar(255) NOT NULL,
	user_id int4,
	album_date	date NOT NULL,
	FOREIGN KEY (user_id) REFERENCES Users(user_id),
	PRIMARY KEY (album_id)
);

CREATE TABLE Pictures
(
	picture_id int4 AUTO_INCREMENT,
	user_id int4,
	imgdata longblob ,
	caption VARCHAR(255),
    album_id int,
    FOREIGN KEY(user_id) references Users(user_id),
    FOREIGN KEY(album_id) references Albums(album_id),
	PRIMARY KEY (picture_id)
);

CREATE TABLE Tags
(
	tag_id int4 AUTO_INCREMENT,
	tag varchar(255),
	PRIMARY KEY (tag_id)
);

CREATE TABLE Tagged_With
(
	picture_id int4,
	tag_id int4,
	FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id),
	FOREIGN KEY (tag_id) REFERENCES Tags(tag_id)
);

CREATE TABLE Comments
(
	comment_id int4 AUTO_INCREMENT,
	test varchar(255),
	comment_owner int4,
	comment_date date,
	picture_id	int4,
	FOREIGN KEY(comment_owner) REFERENCES Users(user_id),
	FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id),
	PRIMARY KEY(comment_id)
);

CREATE TABLE Likes
(
	user_id int4,
	picture_id int4,
	FOREIGN KEY (user_id) REFERENCES Users(user_id),
	FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id),
    PRIMARY KEY (picture_id, user_id)
);

CREATE TABLE Friends
(
	user_id int4,
	friend_id int4,
	FOREIGN KEY (user_id) REFERENCES Users(user_id),
	FOREIGN KEY (friend_id) REFERENCES Users(user_id),
	PRIMARY KEY (user_id, friend_id)
);