#!/bin/bash

scp $MBOT/thermoloc_out/* thermoloc_out/
scp $MBOT/thermoslowc_out/* thermoloc_out/
ssh pi@192.168.178.123
