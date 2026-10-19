drop table if exists  proof_of_concept;
create table proof_of_concept
( f1 char(100), f2 char(20) );

LOAD DATA CONCURRENT /* LOCAL */ 
    INFILE 'E:\\2010-08-05_EU_pitch_SHORTENED'
    IGNORE /* REPLACE */
    INTO TABLE proof_of_concept
    -- FIELDS TERMINATED BY '' 
    -- ENCLOSED BY ''
    LINES TERMINATED BY '\n'
    -- LINES TERMINATED BY '\r\n'
    -- IGNORE 1 LINES
    (
            @line)
    SET
    f1 = substring( @line, 1, 35),
    f2 = substring( @line, 36, 11);

-- Records: 9,536,695 rows in 331.625 sec = ~6min
-- 1,600,000 rows per min
