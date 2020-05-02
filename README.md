# stm32l053_disco_eink_display_practice
![alt text](https://github.com/IsikcanYilmaz/stm32l053_disco_eink_display_practice/blob/master/20170826_104507.jpg)

This is the first thing I did for the STM32L053 Discovery Dev board that I got my hands on recently. 

Done in the Keil IDE using the HAL libraries. 

Run the python program ./eink_thing_client.py for the photo conversion functionality. Browse for a jpg file, move the slider around to get a decent black and white threshold, click transfer to transfer the compressed picture to your STM32L053. 

The result is something like what you see above; the picture of my face on the e-ink display. 

--

UPDATE:
Got more versed on the ST platform. The data transfer now uses DMA and is now way faster. Usage goes like so: load the fw, you'll see the red LED blink. Open up eink_thing_client.py, browse for a picture, adjust using the slider, hit transfer. Once the transfer completes, your picture should appear on the eink screen.

ugh I cant even look at this repo anymore. its from a time when i didnt know shit about shit.
