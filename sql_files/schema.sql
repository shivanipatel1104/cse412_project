DROP TABLE IF EXISTS playlistsongs, likedsongs, playlist, song, album, artist, users CASCADE;

CREATE TABLE "users" (
	u_userID SERIAL PRIMARY KEY, 
	u_username VARCHAR(30) UNIQUE NOT NULL,
	u_name VARCHAR(50) NOT NULL,
	u_email VARCHAR(50) UNIQUE NOT NULL,
	u_password VARCHAR(255) NOT NULL,
	u_userType VARCHAR(20) NOT NULL CHECK (u_userType IN ('artist', 'user'))
);
	
CREATE TABLE "artist" (
	a_artistID SERIAL PRIMARY KEY,
   	a_artistName VARCHAR(50) UNIQUE NOT NULL,
   	a_country VARCHAR(50) NOT NULL,
   	a_genre VARCHAR(50) NOT NULL,
    	a_userID INT UNIQUE NOT NULL,
	a_pop INT, 
    FOREIGN KEY (a_userID) REFERENCES users(u_userID) ON DELETE CASCADE
);

CREATE TABLE "album" (
    al_albumID SERIAL PRIMARY KEY,
    al_albumName VARCHAR(50) NOT NULL, 
    al_artistID INT NOT NULL, 
    al_releaseDate DATE NOT NULL,
	UNIQUE (al_albumName, al_artistID), 
	FOREIGN KEY (al_artistID) REFERENCES artist(a_artistID) ON DELETE CASCADE
);

CREATE TABLE "song" (
	s_songID SERIAL PRIMARY KEY,
s_albumID INT NOT NULL, 
	s_songname VARCHAR(50) NOT NULL,
	s_genre VARCHAR(50) NOT NULL,
	duration TIME NOT NULL,
	s_times_played INT,
	UNIQUE (s_songname, s_albumID),
	FOREIGN KEY (s_albumID) REFERENCES album(al_albumID) ON DELETE CASCADE
);

CREATE TABLE "playlist" (
	p_playlistID SERIAL PRIMARY KEY, 
	p_playlistname VARCHAR(50) NOT NULL,
	p_author_userID INT NOT NULL,
	p_timeCreated TIMESTAMP DEFAULT NOW(),
	p_liked INT,
	FOREIGN KEY (p_userID) REFERENCES users(u_userID) ON DELETE CASCADE
);

CREATE TABLE "playlistsongs" (
	ps_playlistID INT NOT NULL,
	ps_songID INT NOT NULL,
	PRIMARY KEY (ps_playlistID, ps_songID),
	FOREIGN KEY (ps_playlistID) REFERENCES playlist(p_playlistID) ON DELETE CASCADE,
	FOREIGN KEY (ps_songID) REFERENCES song(s_songID) ON DELETE CASCADE	
);

CREATE TABLE "playlist_followers" (
  pf_id SERIAL PRIMARY KEY,
  pf_playlistID INT NOT NULL,
  pf_userID INT NOT NULL,
  FOREIGN KEY (pf_playlistID) REFERENCES playlist(p_playlistID) ON DELETE CASCADE,
  FOREIGN KEY (pf_userID) REFERENCES users(u_userID) ON DELETE CASCADE,
  UNIQUE (pf_playlistID, pf_userID)
);

CREATE TABLE "likedsongs" ( 
	l_userID INT NOT NULL,
	l_songID INT NOT NULL,
	PRIMARY KEY (l_userID, l_songID),
	FOREIGN KEY (l_userID) REFERENCES users(u_userID) ON DELETE CASCADE,
	FOREIGN KEY (l_songID) REFERENCES song(s_songID) ON DELETE CASCADE
);
