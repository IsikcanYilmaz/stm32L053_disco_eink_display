# stm32l053_disco_eink_display_practice
![alt text](https://github.com/IsikcanYilmaz/stm32l053_disco_eink_display_practice/blob/master/20170826_104507.jpg)

This is the first thing I did for the STM32L053 Discovery Dev board that I got my hands on recently. 

Done in the Keil IDE using the HAL libraries. 

Run the python program ./eink_thing_client.py for the photo conversion functionality. Browse for a jpg file, move the slider around to get a decent black and white threshold, click transfer to transfer the compressed picture to your STM32L053. 

Transfer is done in UART. Bytes written via DMA to a buffer. Every time the buffer is full, an interrupt is fired, followed by the ISR putting the contents of the buffer to where we want em. 

The result is something like what you see above; the picture of my face on the e-ink display. 
