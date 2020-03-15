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
	likes integer,
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

CREATE OR REPLACE FUNCTION UpdateLikes()
RETURNS TRIGGER AS $$
DECLARE
value INTEGER;
BEGIN
	SELECT likes FROM photos INTO value;
	IF NEW IS NOT NULL THEN
		UPDATE photos SET likes=value+1;
		RETURN NEW;
	ELSE
		IF OLD IS NOT NULL THEN
			UPDATE photos SET likes=value-1;
			RETURN OLD;
		END IF;
	END IF;
END
$$ LANGUAGE PLPGSQL;
CREATE TRIGGER UpdateLikes
BEFORE INSERT OR DELETE ON likes
FOR EACH ROW
EXECUTE PROCEDURE UpdateLikes();