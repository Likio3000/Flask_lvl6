# Filename: ./flaskr/schema.sql
# ----- Start of file content -----
-- Ensure tables are dropped before creation to allow repeatable initialization
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

-- User table: Stores login information
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for each user
  username TEXT UNIQUE NOT NULL,       -- Username, must be unique and provided
  password TEXT NOT NULL                 -- Hashed password, must be provided
);

-- Post table: Stores blog post content
CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,     -- Unique ID for each post
  author_id INTEGER NOT NULL,               -- Foreign key linking to the user who wrote the post
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the post was created, defaults to now
  title TEXT NOT NULL,                      -- Title of the post, must be provided
  body TEXT NOT NULL,                       -- Main content of the post, must be provided
  FOREIGN KEY (author_id) REFERENCES user (id) -- Enforce relationship: author_id must exist in user table
    ON DELETE CASCADE -- Optional: If a user is deleted, delete their posts too. Consider implications.
);

-- Optional: Add indexes for performance on frequently queried columns
CREATE INDEX idx_post_author_id ON post (author_id);
CREATE INDEX idx_post_created ON post (created);
CREATE UNIQUE INDEX idx_user_username ON user (username); -- Already implicitly created by UNIQUE constraint, but can be explicit

-- Explanation:
-- - `DROP TABLE IF EXISTS`: Ensures the script can be run multiple times without errors.
-- - `PRIMARY KEY AUTOINCREMENT`: Creates a unique integer ID that automatically increases.
-- - `UNIQUE`: Ensures the value in this column is unique across all rows (e.g., usernames).
-- - `NOT NULL`: Ensures a value must be provided for this column.
-- - `DEFAULT CURRENT_TIMESTAMP`: Automatically sets the column to the current date/time when a row is inserted if no value is provided. SQLite stores this typically as a TEXT ISO8601 string.
-- - `FOREIGN KEY`: Establishes a link between `post.author_id` and `user.id`.
-- - `ON DELETE CASCADE`: (Optional) If a user referenced by posts is deleted, all their posts are also automatically deleted. Remove this if you prefer to handle orphaned posts differently (e.g., set author_id to NULL or prevent user deletion).
-- - `CREATE INDEX`: Improves the speed of lookups based on the indexed columns (e.g., finding all posts by an author or sorting by creation date).
