/**

Transforms BATS Europe PITCH data file wiht fixed format values into
a normalized (stripping of redundant spaces and zeros) CSV format skipping
all records except 'A' and 'E':

    id              Unique ID assigned to the row
    time_stamp      Time stamp in ms
    minute          Minute
    order_id        Decode Order ID value
    message_type    Message type ('A' and 'E')
    side_indicator  'B' or 'S' for 'A' message type
    shares          Number of shares
    symbol          Symbol
    price           Price

*/



#include <iostream>
#include <fstream>
#include <string>

#include <stdio.h>
#include <fcntl.h>
#include <io.h>

using namespace std;

// Decodes Base36 ID inot Integer
unsigned long long order_id ( const char *line) { // 10 (12)
    unsigned long long id = 0;
    char code;
    for ( int p = 10; p < 22; p++)
    {
        id *= 36;
        code = line[p];
        if( code != '0' )
        {
            id += code - ( code > 64 ? 55 : 48 );
        }
    }
    return id;
}

// Extracts date value from the file name
string get_date( const string file_name) {
    string s = file_name;
    for (unsigned int p=0; p < s.length() ; p++ ) {
        if ( isdigit(s[p]) && isdigit(s[p+1]) && isdigit(s[p+2]) && isdigit(s[p+3]) && s[p+4]=='-'
             && isdigit(s[p+5]) && isdigit(s[p+6]) && s[p+7]=='-' && isdigit(s[p+8]) && isdigit(s[p+9]))
        {
            return s.substr(p,10);
        }
    }
    return "";
}

int main (int argc, char *argv[])
{

    if ( argc < 2) {
        cerr << "Missing source data file name and output file name!";
        return 1;
    }
    char *file_name = argv[1];
    ifstream source (file_name, ios::in /* | ios::binary */);
    if ( !source) {
        cerr << printf( "File '%s' does not exist!", file_name);
        return 2;
    }

    //char *output_file_name = argv[2];
    //ofstream outfile( output_file_name, ios::binary | std::ios_base::out );


    // string file_date = get_date( file_name);

    char line[100];
    char msg_type;
    long long lineno = 1;
    //cout.setf( ios::binary );
    cout.imbue(std::locale("C"));
    _setmode( fileno( stdout ), _O_BINARY ); // Work-arround to forse end-of-line = '\n'
    cout << "id,time_stamp,minute,order_id,message_type,side_indicator,shares,symbol,price\n";
    while( source.good() ) {
        source.getline(line,100);
        if ( source.eof() ) break;
        msg_type = line[9];
        if( msg_type!='A' && msg_type!='E' ) continue; // skip all excep 'A' and 'E' messages

        int msec = 0;
        for ( int p=1; p < 9; p++) {
            msec *= 10;
            char c = line[p];
            if (c != '0') msec += (c-48);
        }
        int min = msec / 60000 +1;
        cout << lineno++ << ',' << msec << ',' << min << ',';
        // cout.write( &line[1], 8 ); // Timstamp
        // cout.put(',');
        // cout << printf( "%s %02d:%02d:%02d,", file_date.c_str() , hour, min, sec );
        unsigned long long id = order_id( line);
        cout << id << ',' << msg_type << ',';
        int p; // position
        int sp; // starting position
        int fl; // field length
        if ( msg_type=='A') {
            cout.put( line[22]);
            cout.put(',');
            sp = 23; fl = 6;
            for ( p=sp; line[p]=='0' && p < sp+fl; p++ );
            if (p<sp+fl) cout.write( &line[p],fl-(p-sp)); // Shares
            cout.put(',');
            for ( p=1; line[29+p]!=' '&&p<7;p++ );
            if (p>6) p=6; cout.write( &line[29],p); // Symbol
            cout.put(',');
            sp = 35; fl = 10;
            for ( p=sp; line[p]=='0' && p < sp+fl; p++ );
            if (p<sp+fl) cout.write( &line[p],fl-(p-sp)); // Price
        } else if ( msg_type=='E') {
            cout.put(',');
            sp = 22; fl = 6;
            for ( p=sp; line[p]=='0' && p < sp+fl; p++ );
            if (p<sp+fl) cout.write( &line[p],fl-(p-sp)); // Shares
            // cout.put(','); cout.put(','); // No symbol
        } // else continue;
        //cout << ',' << line;
        // cout << endl;
        cout << '\n';
    }
    // ios_base::fmtflags f = source.flags();
    source.close();
    cout.flush();
    return 0;
}
