use DBI;
use Data::Dumper;


$dsn = 'DBI:SQLite:dbname = mesh.db:"",""';
$dbh = DBI->connect('DBI:SQLite:mesh.db') or die $DBI::errstr;

$sth = $dbh->prepare("SELECT * from messages limit 19");
$rv = $sth->execute() or die $DBI::errstr;

while (my $row = $sth->fetchrow_hashref) {
        print "row ", $i++, "\n";
        for my $col (keys %$row) {
            print "\t$col is $row->{$col}\n";
        }
    }



$dbh->disconnect();

