#!/bin/bash
cat Input/testcd.in | python3 nautilus.py > Raw/rawcd.out
cat Raw/rawcd.out | ./pretty.sh Input/testcd.in > Output/testcd.out
cat Input/testmkdir.in | python3 nautilus.py > Raw/rawmkdir.out
cat Raw/rawmkdir.out | ./pretty.sh Input/testmkdir.in > Output/testmkdir.out
cat Input/testtouch.in | python3 nautilus.py > Raw/rawtouch.out
cat Raw/rawtouch.out | ./pretty.sh Input/testtouch.in > Output/testtouch.out
cat Input/testmv.in | python3 nautilus.py  > Raw/rawmv.out
cat Raw/rawmv.out | ./pretty.sh Input/testmv.in > Output/testmv.out
cat Input/testcp.in | python3 nautilus.py  > Raw/rawcp.out
cat Raw/rawcp.out | ./pretty.sh Input/testcp.in > Output/testcp.out
cat Input/testpwd_exit.in | python3 nautilus.py > Raw/rawpwd_exit.out
cat Raw/rawpwd_exit.out | ./pretty.sh Input/testpwd_exit.in > Output/testpwd_exit.out
cat Input/testrm.in | python3 nautilus.py  > Raw/rawrm.out
cat Raw/rawrm.out | ./pretty.sh Input/testrm.in > Output/testrm.out
cat Input/testrmdir.in | python3 nautilus.py > Raw/rawrmdir.out
cat Raw/rawrmdir.out | ./pretty.sh Input/testrmdir.in > Output/testrmdir.out