drop table if exists entries;
create table entries (
	id integer primary key autoincrement,
	title string not null,
	text string not null
);

drop table if exists members;
create table members (
	id integer primary key autoincrement,
	userid string not null,
	password string not null,
	nickname string not null
);


