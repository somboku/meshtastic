#!/usr/bin/env perl

use strict;
use warnings;
use Device::SerialPort;

my $p = '/dev/ttyACM0';

my $port = Device::SerialPort->new($p)
    or die "Cannot open $p: $!";

# Typical Meshtastic serial settings
$port->baudrate(115200);
$port->databits(8);
$port->parity("none");
$port->stopbits(1);
$port->handshake("none");

my $buffer = '';

# Apply settings
$port->write_settings
    or die "Failed to write serial settings";

print "Connected to $p\n";
print "Listening...\n\n";

while (1) {
    my ($count, $data) = $port->read(255);
	
    if ($count > 0) {
	$buffer .= $data;
        print $data;

        while ($buffer =~ s/^(.*?\n)//) {
            my $line = $1;
            print $line;
        }

    }

    select(undef, undef, undef, 0.05);
}
