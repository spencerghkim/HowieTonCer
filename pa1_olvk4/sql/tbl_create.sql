DROP DATABASE group108;
CREATE DATABASE group108;

USE group108;

CREATE TABLE user (username VARCHAR(20), firstname VARCHAR(20), lastname VARCHAR(20), password VARCHAR(20), email VARCHAR(40), PRIMARY KEY (username));
CREATE TABLE album (albumid INT PRIMARY KEY, title VARCHAR(50), created DATE, lastupdated DATE, username VARCHAR(20), FOREIGN KEY (username) REFERENCES user(username));
CREATE TABLE photo (picid VARCHAR(40) PRIMARY KEY, url VARCHAR(255), format CHAR(3), date DATE);
CREATE TABLE contain (albumid INT, picid VARCHAR(40), caption VARCHAR(255), sequencenum INT, PRIMARY KEY (albumid, picid), FOREIGN KEY (albumid) REFERENCES album(albumid), FOREIGN KEY (picid) REFERENCES photo(picid));
