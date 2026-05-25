#!/usr/bin/env perl
# extract everything what comes in. 
# @Author: ChatGPT:(
# 2026


use strict;
use warnings;
use Device::SerialPort;

my $m;
open my $fh , '>>:raw', "out.log" or die $!;
sub _log{ 
	my ($m) = @_;
	print $fh "$m\n";
}


my $dev = '/dev/ttyACM0';
my $port = Device::SerialPort->new($dev)
    or die "Cannot open $dev\n";

$port->baudrate(115200);
$port->databits(8);
$port->parity('none');
$port->stopbits(1);
$port->handshake('');
$port->write_settings;

$port->write("\r\n");
$port->write("\r\n");

print "Connected to $dev\n";
while (1) {

    my ($count, $data) = $port->read(256);

    if ($count > 0) {

        # show hex
        my $hex = unpack('H*', $data);
        $hex =~ s/(..)/$1 /g;

        print "\n--- RAW BYTES ($count) ---\n";
        print "$hex\n";
	_log("\n_________________________________________________________________\n");
	_log($hex);
	_log("DATA:\n");
	_log($data);
       
        my $ascii = '';

        foreach my $c (split //, $data) {
            my $o = ord($c);

            if ($o >= 32 && $o <= 126) {
                $ascii .= $c;
            } else {
                $ascii .= '.';
            }
        }

        print "ASCII:\n=======================\n$ascii\n===================================\n";
    }

    # IMPORTANT: prevents CPU spin
    select(undef, undef, undef, 0.05);
}
