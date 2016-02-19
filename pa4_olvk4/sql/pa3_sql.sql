drop table if exists Comment;
create table Comment (
	commentid integer primary key not null auto_increment,
	picid varchar(40) not null,
	message varchar(140) not null,
	username varchar(20) not null,
	date timestamp default current_timestamp,

	foreign key (picid) references Photo (picid)
);

drop table if exists Favorite;
create table Favorite (
	favoriteid integer primary key not null auto_increment,
	picid varchar(40) not null,
	username varchar(20) not null,
	date timestamp default current_timestamp,

	foreign key (picid) references Photo (picid),
	foreign key (username) references User (username)
);

INSERT INTO Comment (picid, message, username, date) VALUES ('football_s3','This is awesome!','traveler','2015-10-05 21:23:23');
INSERT INTO Comment (picid, message, username, date) VALUES ('football_s3','This is out of this world!','spacejunkie','2015-10-05 21:23:23');
INSERT INTO Comment (picid, message, username, date) VALUES ('football_s3','We should go to a soccer game sometime!','spacejunkie','2015-10-05 21:23:23');
INSERT INTO Comment (picid, message, username, date) VALUES ('football_s2','Sweet football_s2 pic!','spacejunkie','2015-10-05 21:23:25');
INSERT INTO Comment (picid, message, username, date) VALUES ('football_s1','Sweet football_s1 pic!','spacejunkie','2015-10-05 21:24:45');
INSERT INTO Comment (picid, message, username, date) VALUES ('football_s3','Sweet football_s3 pic!','spacejunkie','2015-10-05 21:24:53');
INSERT INTO Comment (picid, message, username, date) VALUES ('football_s1','I\'d love to visit the stadium in football_s1 someday!!','traveler','2015-10-05 21:25:42');
INSERT INTO Comment (picid, message, username, date) VALUES ('football_s2','I\'d love to visit the stadium in football_s2 someday!!','traveler','2015-10-05 21:25:49');
INSERT INTO Comment (picid, message, username, date) VALUES ('football_s3','I\'d love to visit the stadium in football_s3 someday!!','traveler','2015-10-05 21:25:58');


INSERT INTO Favorite (picid, username, date) VALUES ('football_s3','spacejunkie','2015-10-05 22:23:23');
INSERT INTO Favorite (picid, username, date) VALUES ('football_s3','sportslover','2015-10-05 21:23:23');
INSERT INTO Favorite (picid, username, date) VALUES ('football_s2','spacejunkie','2015-10-05 23:23:35');
INSERT INTO Favorite (picid, username, date) VALUES ('football_s2','sportslover','2015-10-05 23:45:35');
INSERT INTO Favorite (picid, username, date) VALUES ('football_s2','traveler','2015-10-05 21:10:35');
INSERT INTO Favorite (picid, username, date) VALUES ('football_s1','traveler','2015-10-05 23:10:35');
INSERT INTO Favorite (picid, username, date) VALUES ('football_s1','spacejunkie','2015-10-05 23:15:35');

UPDATE Contain SET caption='What do you want me to do?' WHERE picid='football_s3';