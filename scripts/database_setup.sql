-- AI Assistant Database Setup Script
-- Run this script to create the database and tables

CREATE DATABASE IF NOT EXISTS ai_assistant;
USE ai_assistant;

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_input TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    function_type VARCHAR(50) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_function_type (function_type)
);

-- Create feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT,
    rating ENUM('helpful', 'not_helpful') NOT NULL,
    comment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_rating (rating)
);

-- Insert sample data for testing (optional)
INSERT INTO conversations (user_input, ai_response, function_type) VALUES
('What is the capital of France?', 'The capital of France is Paris. It is located in the north-central part of the country and serves as the political, economic, and cultural center of France.', 'question'),
('Summarize this text: Python is a programming language...', 'Summary: Python is a versatile programming language known for its simplicity and wide range of applications in web development, data science, and automation.', 'summarize'),
('Write a short story about AI', 'Once upon a time, in a world where technology and nature coexisted harmoniously, there lived a young inventor named Alex...', 'creative'),
('Give me study tips', 'Effective Study Tips: 1. Create a dedicated study space 2. Use the Pomodoro Technique 3. Practice active recall...', 'advice');

-- Create indexes for better performance
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp DESC);
CREATE INDEX idx_feedback_timestamp ON feedback(timestamp DESC);

SHOW TABLES;
SELECT 'Database setup completed successfully!' as Status;




