# commandline.reminder
a command line reimder tool

plz add below into your bash/zsh configuration

function marley {
    echo -n $* | nc localhost 60102
}

usage:

1. marley remind me in 1 day/d 1 hour/h 1 second/sec/s todo blah blah blah
2. marley list
