DROP DATABASE playlistcollab;
CREATE DATABASE IF NOT EXISTS playlistcollab;
USE playlistcollab; 

DROP TABLE IF EXISTS users; 
DROP TABLE IF EXISTS tokens; 
DROP TABLE IF EXISTS playlist;
DROP TABLE IF EXISTS spotifyToken; 

CREATE TABLE users(
    userid int not null AUTO_INCREMENT,
    username varchar(128) not null, 
    pwdhash varchar(256) not null, 
    PRIMARY KEY (userid),
    UNIQUE (username)
);

ALTER TABLE users AUTO_INCREMENT = 101; 

CREATE TABLE tokens(
    token varchar(128) not null,
    userid int not null, 
    expiration_utc datetime not null, 
    PRIMARY KEY (token),
    FOREIGN KEY (userid) REFERENCES users(userid)
);


CREATE TABLE playlist(
    tid int not null AUTO_INCREMENT, 
    userid int not null, 
    song varchar(256) not null, 
    artist varchar(256) not null,
    songID varchar(256) not null, 
    PRIMARY KEY (tid),
    FOREIGN KEY (userid) REFERENCES users(userid),
    UNIQUE(songID)
);

ALTER TABLE playlist AUTO_INCREMENT = 201; 

CREATE TABLE spotifyToken(
    id int not null AUTO_INCREMENT,
    token varchar(256) not null,
    refresh varchar(256) not null,
    expiration_utc datetime not null, 
    PRIMARY KEY (id)
);

ALTER TABLE spotifyToken AUTO_INCREMENT = 1;


DROP USER IF EXISTS 'read-only';
DROP USER IF EXISTS 'read-write';

CREATE USER 'read-only' IDENTIFIED BY 'abc123!!';
CREATE USER 'read-write' IDENTIFIED BY 'def456!!';

GRANT SELECT, SHOW VIEW ON playlistcollab.* 
      TO 'read-only';
GRANT SELECT, SHOW VIEW, INSERT, UPDATE, DELETE, DROP, CREATE, ALTER ON playlistcollab.* 
      TO 'read-write';
      
FLUSH PRIVILEGES