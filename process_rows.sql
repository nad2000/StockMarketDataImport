
CREATE INDEX message_id_idx ON message(id);
CREATE INDEX message_idx ON message( order_id, message_type, id);

DROP TABLE IF EXISTS e_message;
CREATE /*TEMPORARY*/ TABLE e_message 
-- ENGINE=MyISAM /* TODO: consider MEMORY */
ENGINE=MEMORY /* TODO: consider MEMORY */
SELECT *, CAST(NULL AS UNSIGNED) AS last_a_msg_id  FROM message 
WHERE message_type='E';

-- DROP INDEX e_message_order_id_idx ON e_message;
CREATE /*UNIQUE*/ INDEX e_message_order_id_idx ON e_message( minute, symbol, order_id);

-- Relevant orders
-- DROP TABLE IF EXISTS ord;
-- CREATE TABLE ord 
-- ENGINE=MyISAM /* TODO: consider MEMORY */
-- SELECT DISTINCT order_id FROM e_message;


-- DROP TABLE IF EXISTS symbol;
-- CREATE TABLE symbol
-- ENGINE=MyISAM /* TODO: consider MEMORY */
-- SELECT DISTINCT symbol FROM e_message;

-- Link to the most recent 'A' messages
UPDATE e_message e JOIN 
(
    SELECT e.id, MAX( a.id) AS last_a_msg_id
    FROM e_message e JOIN message a 
    ON a.order_id = e.order_id 
        AND a.message_type='A' 
        AND a.id < e.id
    GROUP BY e.id ) AS last_a 
ON last_a.id = e.id
SET e.last_a_msg_id = last_a.last_a_msg_id;

-- symbol and price of the transaction:
UPDATE e_message e JOIN message a 
    ON a.id = e.last_a_msg_id
SET
    e.symbol = a.symbol, 
    e.price = a.price;

DROP TABLE IF EXISTS onemin_oc;

CREATE TEMPORARY TABLE onemin_oc
ENGINE=MEMORY
SELECT
    flm.symbol,
    flm.minute,
    fm.price AS opening_price,
    lm.price AS closing_price
FROM
(SELECT
    symbol,
    minute,
    MIN( id) first_id, 
    MAX( id) last_id
FROM e_message
GROUP BY symbol, minute) AS flm
JOIN e_message AS fm ON fm.id = flm.first_id
JOIN e_message AS lm ON lm.id = flm.last_id;

DROP TABLE IF EXISTS onemin_mmv;

CREATE TEMPORARY TABLE onemin_mmv
ENGINE=MEMORY
SELECT
    e.symbol, 
    e.minute, 
    MIN( e.price) min_price, 
    MAX( e.price) max_price, 
    SUM( e.shares) AS volume
FROM e_message e
GROUP BY symbol, minute;

SET @file_date = (SELECT file_date FROM import_file ORDER BY id DESC LIMIT 1);

DROP TABLE onemin;
CREATE TABLE onemin
ENGINE=MyISAM
SELECT
    mmv.symbol AS `Symbol`, 
    ( @file_date+SEC_TO_TIME(mmv.minute*60) ) AS `Date`, 
    oc.opening_price AS `Open`,
    mmv.max_price AS `High`, 
    mmv.min_price AS `Low`,
    oc.closing_price AS `Close`,
    mmv.volume AS `Volume`
FROM  onemin_mmv AS mmv JOIN onemin_oc AS oc
ON
    oc.symbol = mmv.symbol
    AND oc.minute = mmv.minute;