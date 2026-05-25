#!/usr/bin/env perl
# extract everything what comes in. 
# @Author: ChatGPT:(
# 2026


#!/usr/bin/env perl

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
$port->handshake('none');
$port->write_settings;

print "-> Listening for Meshtastic protobuf frames...\n";

my $buffer = '';

while (1) {

    my ($count, $data) = $port->read(256);

    if ($count > 0) {
        $buffer .= $data;
    }

    # keep scanning buffer
    while (1) {
        # find frame start
        my $start = index($buffer, "\x94\xC3");

        last if $start < 0;

        # discard garbage before frame
        if ($start > 0) {
            substr($buffer, 0, $start, '');
        }

        # need at least header
        last if length($buffer) < 4;

        my ($h1, $h2, $len_hi, $len_lo) =
            unpack('C4', substr($buffer, 0, 4));

        my $len = ($len_hi << 8) | $len_lo;

        # wait until full frame arrives
        last if length($buffer) < 4 + $len;

        my $frame = substr($buffer, 0, 4 + $len, '');

        my $payload = substr($frame, 4);

        print "\n=== MESHTASTIC PROTOBUF FRAME ===\n";
        print "Length: $len bytes\n";

        # hex dump
        my $hex = unpack('H*', $payload);
        $hex =~ s/(..)/$1 /g;

        print "Payload HEX:\n$hex\n";

        # printable preview
        print "ASCII preview:\n";

        my $ascii = '';
        for my $c (split //, $payload) {
            my $o = ord($c);
            $ascii .= ($o >= 32 && $o <= 126) ? $c : '.';
        }

        print "$ascii\n";
    }

    select(undef, undef, undef, 0.02);
}
