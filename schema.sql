CREATE DATABASE IF NOT EXISTS universal_knowledge_db;
USE universal_knowledge_db;

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS knowledge (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(180) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(80) NOT NULL,
    source VARCHAR(180) DEFAULT 'User contribution',
    tags VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    FULLTEXT INDEX ft_knowledge (title, content, tags)
);

INSERT IGNORE INTO categories (name, description) VALUES
('Computer Science', 'Computing, software and algorithms'),
('Artificial Intelligence', 'AI, machine learning and intelligent systems'),
('Science', 'Scientific concepts and discoveries'),
('Mathematics', 'Mathematical concepts and methods'),
('Healthcare', 'Health and medical knowledge'),
('History', 'Historical events and civilizations'),
('Technology', 'Emerging and applied technologies');

INSERT INTO knowledge (title, content, category, source, tags) VALUES
('What is a Database Management System?',
 'A DBMS is software that enables users to define, create, maintain and control access to databases. It provides data storage, retrieval, security, integrity and concurrency features.',
 'Computer Science', 'DBMS Fundamentals', 'DBMS SQL database data'),
('What is Artificial Intelligence?',
 'Artificial Intelligence is a field of computing focused on systems that perform tasks associated with human intelligence, such as learning, reasoning, perception and language understanding.',
 'Artificial Intelligence', 'AI Fundamentals', 'AI machine learning neural networks'),
('What is a Primary Key?',
 'A primary key is a column or set of columns that uniquely identifies each row in a relational table. Primary key values must be unique and cannot be NULL.',
 'Computer Science', 'Relational Database Concepts', 'SQL keys constraints'),
('What is Data Normalization?',
 'Normalization organizes relational data to reduce redundancy and improve data integrity. Common normal forms include 1NF, 2NF and 3NF.',
 'Computer Science', 'Database Design', 'normalization 1NF 2NF 3NF');
