python3 OMS_ntuplizer.py --split 0/8 >& log0 &
sleep 1
python3 OMS_ntuplizer.py --split 1/8 >& log1 &
sleep 1
python3 OMS_ntuplizer.py --split 2/8 >& log2 &
sleep 1
python3 OMS_ntuplizer.py --split 3/8 >& log3 &
sleep 1
python3 OMS_ntuplizer.py --split 4/8 >& log4 &
sleep 1
python3 OMS_ntuplizer.py --split 5/8 >& log5 &
sleep 1
python3 OMS_ntuplizer.py --split 6/8 >& log6 &
sleep 1
python3 OMS_ntuplizer.py --split 7/8 >& log7 &
sleep 1

disown %1 %2 %3 %4 %5 %6 %7 %8
