CREATE DATABASE tracker_db;
USE tracker_db;

CREATE TABLE users(
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100),
email VARCHAR(100),
password VARCHAR(255)
);

CREATE TABLE groups(
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100),
invite_code VARCHAR(10)
);

CREATE TABLE locations(
user_id INT PRIMARY KEY,
group_id INT,
latitude DOUBLE,
longitude DOUBLE
);