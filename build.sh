#!/bin/bash

########################################################################################################################

if [[ -f /usr/local/rt/setup.sh ]]
then
    source /usr/local/rt/setup.sh
fi

########################################################################################################################

grcc --output grc ./grc/spectro.grc

grcc --output grc ./grc/spectro-uhd-1.grc
grcc --output grc ./grc/spectro-uhd-2.grc

grcc --output grc ./grc/spectro-osmo-1.grc
grcc --output grc ./grc/spectro-osmo-2.grc

grcc --output grc ./grc/spectro-fake-1.grc
grcc --output grc ./grc/spectro-fake-2.grc

########################################################################################################################

cat > ./rt/spectro.py << EOF
# -*- coding:utf-8 -*-
########################################################################################################################
# Author: Jerome ODIER
# Email: jerome@odier.xyz
# URL: http://odier.xyz/
#
# Radio Telescope
#
# Copyright (c) 2022-XXXX Jérôme Odier
########################################################################################################################

import numpy as np

from gnuradio import gr
from gnuradio import fft
from gnuradio import uhd
from gnuradio import blocks

from gnuradio.fft import window

########################################################################################################################

$(awk '/class spectro/{f=1} /def argument_parser/{f=0} f' ~/.grc_gnuradio/spectro.py | sed "s/    def/    ####################################################################################################################\n\n    def/" | sed 's/[*]/ * /g' | sed 's/  [*]  / * /g' | sed 's/ [*] :/*:/')

########################################################################################################################
EOF

########################################################################################################################

for N in 1 2
do
    cat > ./rt/spectro_uhd_$N.py << EOF
# -*- coding:utf-8 -*-
########################################################################################################################
# Author: Jerome ODIER
# Email: jerome@odier.xyz
# URL: http://odier.xyz/
#
# Radio Telescope
#
# Copyright (c) 2022-XXXX Jérôme Odier
########################################################################################################################

try:
    from gnuradio import uhd
except ModuleNotFoundError as e:
    print(e.__str__())

from gnuradio import gr
from gnuradio import blocks
from gnuradio import zeromq

from .spectro import spectro

########################################################################################################################

$(awk '/class spectro/{f=1} /def argument_parser/{f=0} f' ./grc/spectro_uhd_$N.py | sed "s/    def/    ####################################################################################################################\n\n    def/" | sed 's/[*]/ * /g' | sed 's/  [*]  / * /g' | sed 's/ [*] :/*:/')

########################################################################################################################
EOF
done

########################################################################################################################

for N in 1 2
do
    cat > ./rt/spectro_osmo_$N.py << EOF
# -*- coding:utf-8 -*-
########################################################################################################################
# Author: Jerome ODIER
# Email: jerome@odier.xyz
# URL: http://odier.xyz/
#
# Radio Telescope
#
# Copyright (c) 2022-XXXX Jérôme Odier
########################################################################################################################

try:
    import osmosdr
except ModuleNotFoundError as e:
    print(e.__str__())

from gnuradio import gr
from gnuradio import blocks
from gnuradio import zeromq

from .spectro import spectro

########################################################################################################################

$(awk '/class spectro/{f=1} /def argument_parser/{f=0} f' ./grc/spectro_osmo_$N.py | sed "s/    def/    ####################################################################################################################\n\n    def/" | sed 's/[*]/ * /g' | sed 's/  [*]  / * /g' | sed 's/ [*] :/*:/')

########################################################################################################################
EOF
done

########################################################################################################################

for N in 1 2
do
    cat > ./rt/spectro_fake_$N.py << EOF
# -*- coding:utf-8 -*-
########################################################################################################################
# Author: Jerome ODIER
# Email: jerome@odier.xyz
# URL: http://odier.xyz/
#
# Radio Telescope
#
# Copyright (c) 2022-XXXX Jérôme Odier
########################################################################################################################

from gnuradio import gr
from gnuradio import analog
from gnuradio import blocks
from gnuradio import zeromq

from .spectro import spectro

########################################################################################################################

$(awk '/class spectro/{f=1} /def argument_parser/{f=0} f' ./grc/spectro_fake_$N.py | sed "s/    def/    ####################################################################################################################\n\n    def/" | sed 's/[*]/ * /g' | sed 's/  [*]  / * /g' | sed 's/ [*] :/*:/')

########################################################################################################################
EOF
done

########################################################################################################################

rm -f ./grc/spectro.py ./grc/spectro.block.yml

rm -f ./grc/spectro_uhd_1.py ./grc/spectro_uhd_2.py

rm -f ./grc/spectro_osmo_1.py ./grc/spectro_osmo_2.py

rm -f ./grc/spectro_fake_1.py ./grc/spectro_fake_2.py

########################################################################################################################
