-- FORMAT:
-- CREATE INDEX index_name ON table_name (col1, col2, ...);

-- Create index for logging in
CREATE INDEX login_index ON users (u_username, u_password);

-- Create index for song name search
CREATE INDEX song_search_index ON song (s_songname);