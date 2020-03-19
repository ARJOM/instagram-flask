CREATE TABLE users (
	username varchar(80),
	name varchar(80),
	email varchar(80) UNIQUE,
	password varchar(20) NOT NULL,
	CONSTRAINT user_pk PRIMARY KEY (username)
);

CREATE TABLE photos (
	id serial,
	published_date date NOT NULL,
	description varchar(2200),
	username varchar(80),
	photo varchar(255) NOT NULL,
	CONSTRAINT photo_pk PRIMARY KEY (id),
	CONSTRAINT user_fk FOREIGN KEY (username) REFERENCES users(username)
);

CREATE TABLE followers (
	followed varchar(80),
	follower varchar(80),
	CONSTRAINT follower_fk FOREIGN KEY (follower) REFERENCES users(username),
	CONSTRAINT followed_fk FOREIGN KEY (followed) REFERENCES users(username)
);

CREATE TABLE comments (
	id serial,
	created_date date NOT NULL,
	content varchar(2200) NOT NULL,
	photo integer NOT NULL,
	username VARCHAR(80) NOT NULL,
	CONSTRAINT comment_pk PRIMARY KEY (id),
	CONSTRAINT photo_fk FOREIGN KEY (photo) REFERENCES photos(id),
	CONSTRAINT user_fk FOREIGN KEY (username) REFERENCES users(username)
);

CREATE TABLE likes (
	username varchar(80),
	photo integer,
	CONSTRAINT like_pk PRIMARY KEY (username, photo),
	CONSTRAINT user_fk FOREIGN KEY (username) REFERENCES users(username),
	CONSTRAINT photo_fk FOREIGN KEY (photo) REFERENCES photos(id)
);

CREATE VIEW photoinfo AS
SELECT p.id, p.published_date, p.description, p.username, p.photo, count(*) AS likes
FROM photos p, likes l
WHERE p.id=l.photo
GROUP BY p.id, p.published_date, p.description, p.username, p.photo