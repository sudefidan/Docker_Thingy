CREATE TABLE IF NOT EXISTS User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    access_level INT NOT NULL
);

CREATE TABLE IF NOT EXISTS Community (
    community_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(255),
    owner_id INT,
    FOREIGN KEY (owner_id) REFERENCES User(user_id)
);

CREATE TABLE IF NOT EXISTS EventType (
    event_type_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Event (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    virtual_link VARCHAR(255),
    location VARCHAR(255),
    event_type INT,
    community_id INT,
    FOREIGN KEY (event_type) REFERENCES EventType(event_type_id),
    FOREIGN KEY (community_id) REFERENCES Community(community_id)
);

CREATE TABLE IF NOT EXISTS Post (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    date DATE NOT NULL,
    user_id INT,
    community_id INT,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (community_id) REFERENCES Community(community_id)
);

CREATE TABLE IF NOT EXISTS Subscribed (
    community_id INT,
    user_id INT,
    PRIMARY KEY (community_id, user_id),
    FOREIGN KEY (community_id) REFERENCES Community(community_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);