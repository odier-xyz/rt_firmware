#!/bin/bash

########################################################################################################################

if [[ -f /usr/local/rt/setup.sh ]]
then
    source /usr/local/rt/setup.sh
fi

########################################################################################################################

grcc --output grc grc/spectro.grc

grcc --output grc grc/spectro-uhd.grc

grcc --output grc grc/spectro-osmo.grc

########################################################################################################################

cat > rt/spectro.py << EOF
# -*- coding:utf-8 -*-
########################################################################################################################

import numpy as np

from gnuradio import gr
from gnuradio import fft
from gnuradio import uhd
from gnuradio import blocks

from gnuradio.fft import window

########################################################################################################################

$(awk '/class spectro/{f=1} /def argument_parser/{f=0} f' ~/.grc_gnuradio/spectro.py | sed "s/    def/    ####################################################################################################################\n\n    def/" | sed 's/[=]/ = /g' | sed 's/  [=]  / = /g' | sed 's/[*]/ * /g' | sed 's/  [*]  / * /g' | sed 's/ [*] :/*:/')

########################################################################################################################
EOF

########################################################################################################################

cat > rt/spectro_uhd.py << EOF
# -*- coding:utf-8 -*-
########################################################################################################################

import correctiq

from gnuradio import gr
from gnuradio import uhd
from gnuradio import blocks
from gnuradio import zeromq

from .spectro import spectro

########################################################################################################################

$(awk '/class spectro/{f=1} /def argument_parser/{f=0} f' grc/spectro_uhd.py | sed "s/    def/    ####################################################################################################################\n\n    def/" | sed 's/[=]/ = /g' | sed 's/  [=]  / = /g' | sed 's/[*]/ * /g' | sed 's/  [*]  / * /g' | sed 's/ [*] :/*:/')

########################################################################################################################
EOF

########################################################################################################################

cat > rt/spectro_osmo.py << EOF
# -*- coding:utf-8 -*-
########################################################################################################################

import osmosdr
import correctiq

from gnuradio import gr
from gnuradio import blocks
from gnuradio import zeromq

from .spectro import spectro

########################################################################################################################

$(awk '/class spectro/{f=1} /def argument_parser/{f=0} f' grc/spectro_osmo.py | sed "s/    def/    ####################################################################################################################\n\n    def/" | sed 's/[=]/ = /g' | sed 's/  [=]  / = /g' | sed 's/[*]/ * /g' | sed 's/  [*]  / * /g' | sed 's/ [*] :/*:/')

########################################################################################################################
EOF

########################################################################################################################

rm -f grc/spectro_uhd.py

rm -f grc/spectro_osmo.py

########################################################################################################################
