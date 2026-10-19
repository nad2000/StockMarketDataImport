CREATE SCHEMA IF NOT EXISTS stock;

USE stock;

DROP TABLE IF EXISTS message;

CREATE TABLE message
( 
    id INT, -- AUTO_INCREMENT PRIMARY KEY NOT NULL,
    time_stamp INT,
    message_type CHAR(1),
    order_id BIGINT NULL,
    side_indicator CHAR(1) NULL,
    shares MEDIUMINT  NULL,
    symbol VARCHAR(6)  NULL,
    price INT NULL,
    minute INT
)
ENGINE = MyISAM;

DROP TABLE IF EXISTS import_file;

CREATE TABLE import_file
( 
    id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    file_name VARCHAR(2000),
    file_date DATE NULL
)
ENGINE = MyISAM;

