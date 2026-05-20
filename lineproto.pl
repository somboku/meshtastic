#!/usr/bin/env perl

use strict;
use warnings;
use IO::Socket::INET;
use Device::SerialPort;
use Time::HiRes qw(usleep);

my $SERIAL_DEV  = "/dev/ttyACM0";
my $BAUD        = 115200;

my $TCP_HOST    = "127.0.0.1";
my $TCP_PORT    = 5000;

# --- serial setup ---
my $port = Device::SerialPort->new($SERIAL_DEV)
    or die "Cannot open $SERIAL_DEV\n";

$port->baudrate($BAUD);
$port->databits(8);
$port->parity("none");
$port->stopbits(1);
$port->handshake("none");

$port->read_char_time(0);
$port->read_const_time(100);

print "[*] Listening on $SERIAL_DEV\n";

my $sock;

sub connect_tcp {
    while (1) {
        print "[*] Connecting to $TCP_HOST:$TCP_PORT...\n";

        my $s = IO::Socket::INET->new(
            PeerHost => $TCP_HOST,
            PeerPort => $TCP_PORT,
            Proto    => 'tcp',
        );

        if ($s) {
            $s->autoflush(1);
            print "[+] TCP connected\n";
            return $s;
        }

        print "[-] Connect failed, retrying...\n";
        sleep 1;
    }
}

$sock = connect_tcp();

my $buffer = "";

while (1) {

    my ($count, $data) = $port->read(255);

    if ($count > 0) {
        $buffer .= $data;

        while ($buffer =~ s/^(.*?\n)//) {
            my $line = $1;
            chomp $line;

            next unless length $line;

            print "[RX] $line\n";

            eval {
                print $sock "$line\n";
            };

            if ($@ or !$sock->connected) {
                print "[-] TCP disconnected\n";
                close $sock if $sock;
                $sock = connect_tcp();
            }
        }
    }

    usleep(10000);
}
