#-------------------------------------------------------------------------------
# Name:        import
# Purpose:     BATS Europe PITCH data import and conversion into one minute format
#
# Author:      Radomirs Cirskis
#
# Created:     05/31/2011
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import sys
import os
import os.path
import argparse
import datetime
import glob
import time
import tempfile
import re

def getArgs():
    """
    Command argument parser

    Returns structure:
        args.server
        args.port
        args.db
        args.user
        args.password
        args.input

    """
    parser = argparse.ArgumentParser(description='BATS Europe PITCH data import and conversion into one minute format')
    parser.add_argument( '-s', '--server', help='Server', default='localhost')
    parser.add_argument( '-P', '--port', help='Server communication port', default=3306)
    parser.add_argument( '-d', '--db', help='Database, e.g., cdrg_alpha', default='stock')
    parser.add_argument( '-u', '--user', help='DB User', default='root')
    parser.add_argument( '-p', '--password', help='User password', default='')
    parser.add_argument( 'input', help='BATS Europe PITCH data file')

    args = parser.parse_args()
    return args

def getScriptAbsPath( scriptName ):
    if os.name == 'posix':
	    return os.path.join( os.getcwd(), scriptName )
    else:
        return os.path.join( os.path.dirname( __file__ ), scriptName )

def setMySqlCommand( args):
    """
    Create mysql command with parameters for executing a script file
    """
    global sqlCmd
    sqlCmd = "mysql -u%(user)s -h%(host)s -P%(port)s -D%(db)s -v -v -v -f " % {
        'host': args.server,
        'user': args.user,
        'db'  : args.db,
        'port': args.port
    }
    if args.password!= None and args.password!='':
        sqlCmd += " -p%s " % args.password
    return sqlCmd

def getMySqlCommand():
    """
    a gloal variable wrapper
    """
    global sqlCmd
    return sqlCmd

def startTimer():
    """
    Sets/resets timer
    """
    global g_time_start
    g_time_start = time.time()

def getTimeSpent():
    """
    Get time (seconds) spent
    """
    global g_time_start
    return (time.time()-g_time_start)

def getDateFromFileName( file_name):
    """
    Extracts date from the file name like "xxx YYYY-MM-DD xxx"
    """
    date_match = re.search('(20\d\d-[01]\d-[0-3]\d)', file_name )

    return date_match.group(1)

def showMsg( message):
    """
    Displays a message printing it to the standart streem STDERR
    """
    sys.stderr.write( message+'\n' )

def loadRawData( fileName):
    """
    Loads all rows, skipping the header row, from CSV file.
    """

    tempScript = tempfile.mktemp('.sql')
    f = open( tempScript, 'w' )
    f.write(
    """
TRUNCATE TABLE message;

-- DROP INDEX message_order_id_idx ON message;
-- DROP INDEX message_order_id_idx2 ON message;
DROP INDEX message_id_idx ON message;
DROP INDEX message_idx ON message;

ALTER TABLE message DISABLE KEYS;

LOAD DATA CONCURRENT /* LOCAL */
    INFILE '%(file)s'
    IGNORE /* REPLACE */
    INTO TABLE message
    FIELDS TERMINATED BY ','
    -- ENCLOSED BY ''
    LINES TERMINATED BY '\\n'
    -- LINES TERMINATED BY '\\r\\n'
    -- IGNORE 1 LINES
    (
        id,
        time_stamp,
        `minute`,
        order_id,
        message_type,
        side_indicator,
        shares,
        symbol,
        price );

ALTER TABLE message ENABLE KEYS;

INSERT INTO import_file ( file_name, file_date) VALUES ('%(file)s', '%(date)s');

""" % { 'file':fileName.replace('\\','\\\\'), 'date':getDateFromFileName( fileName) } )
    f.close()
    cmd = getMySqlCommand()+"<\""+tempScript+"\""
    os.system( cmd  )

def processRows():
    """
    Invokes process_rows.sql to process loaded rows from the CSV file
    """
    cmd = getMySqlCommand()+"<\""+ getScriptAbsPath('process_rows.sql') +"\""
    os.system( cmd  )

def main():
    """
    1. parse parameters;
    2. transforms fixed value file into CSV;
    3. loads file and prcesses it;
    """
    time_start = time.time()
    args = getArgs()
    setMySqlCommand( args)
    # data source:
    source = os.path.abspath( args.input)
    if not os.path.exists( source ):
        raise Exception("File %s doesn't exist!" % args.input)

    # transforms into CSV file:
    csv_source = source.strip()+'.csv'

    startTimer()
    trpitch_cmd = "%s \"%s\" >\"%s\"" % ( getScriptAbsPath('trpitch'), source, csv_source)
    showMsg( "Executing %s\n" % trpitch_cmd )
    os.system( trpitch_cmd )
    showMsg( "\nData transformation completed in %.5f sec.\n" % getTimeSpent() )

    startTimer()
    loadRawData(csv_source)
    showMsg( "\nData loading completed in %.5f sec.\n" % getTimeSpent() )

    startTimer()
    processRows()
    showMsg( "\nData processing completed in %.5f sec.\n" % getTimeSpent() )

    showMsg( "\n\n### Data import completed in %.5f sec. ###\n\n"
        % (time.time()-time_start))

if __name__ == '__main__':
    main()
