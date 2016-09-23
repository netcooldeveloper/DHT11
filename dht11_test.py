# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time

msleep = lambda x: time.sleep(x/1000.0)
usleep = lambda x: time.sleep(x/1000000.0)

SEPA_MIN  = 20
DIFF_HUMI = -7
DIFF_TEMP = 0
DEBUG_MODE= 0

def bin2dec(string_num):
    return str(int(string_num,2))

end_flag = 0

while end_flag < 30:
    data = []

    GPIO.setmode(GPIO.BCM)

    msleep(800)

    GPIO.setup(17,GPIO.OUT,initial=GPIO.HIGH)

    msleep(40)

    GPIO.output(17,GPIO.LOW)

    msleep(18)

    GPIO.setup(17,GPIO.IN,pull_up_down=GPIO.PUD_UP)

    for i in range(0,4000):
        data.append(GPIO.input(17))
    #    usleep(0.5)
    GPIO.cleanup()

    bit_count = 0
    tmp = 0
    count = 0

    HumidityBitHigh = ""
    HumidityBitLow  = ""

    TemperatureBitHigh = ""
    TemperatureBitLow = ""
    CrcBit = ""

    try:
        while data[count] == 1:
            count = count + 1

        i = 0
        while i < 32:
            zero_count = 0
            bit_count = 0

            while data[count] == 0:
                zero_count = zero_count + 1
                count = count + 1
               
                if zero_count > 50:
                    break

            if DEBUG_MODE == 1:
                print "0:" + "{0:>4}".format(count),

            while data[count] == 1:
                bit_count = bit_count + 1
                count = count + 1
                
                if bit_count > 50:
                    break

            if zero_count < 10:
                continue


            if DEBUG_MODE == 1:
                print "1:{0:>4}".format(count),
                print "zero:{0:>4}".format(zero_count), 
                print "bit:{0:>4}".format(bit_count)

            if bit_count > SEPA_MIN:
                Bit = "1"
            else:
                Bit = "0"

            if i>=0 and i<8:
                HumidityBitHigh = HumidityBitHigh + Bit

            if i>=8 and i<16:
                HumidityBitLow  = HumidityBitLow  + Bit

            if i>=16 and i<24:
                TemperatureBitHigh = TemperatureBitHigh + Bit

            if i>=24 and i<32:
                TemperatureBitLow = TemperatureBitLow + Bit

            i = i + 1
    except:
        print "ERR_RANGE_0"
        exit(0)

    if DEBUG_MODE == 1:
        print "HumidityBitHigh   : " + HumidityBitHigh    + " int ( {0:>4} )".format(int(bin2dec(HumidityBitHigh)))
        print "HumidityBitLow    : " + HumidityBitLow     + " int ( {0:>4} )".format(int(bin2dec(HumidityBitLow)))
        print "TemperatueBitHigh : " + TemperatureBitHigh + " int ( {0:>4} )".format(int(bin2dec(TemperatureBitHigh)))
        print "TemperatueBitLow  : " + TemperatureBitLow  + " int ( {0:>4} )".format(int(bin2dec(TemperatureBitLow)))

    try:
        for i in range(0,8):
            zero_count = 0
            bit_count = 0

            while data[count] == 0:
                tmp = 1
                zero_count = zero_count + 1
                count = count + 1
                if zero_count > 50:
                    break

            if DEBUG_MODE == 1:
                print "0:" + "{0:>4}".format(count),

            while data[count] == 1:
                bit_count = bit_count + 1
                count = count + 1
                if bit_count > 50:
                    break

            if DEBUG_MODE == 1:
                print "1:{0:>4}".format(count),
                print "zero:{0:>4}".format(zero_count),
                print "bit:{0:>4}".format(bit_count)

            if bit_count > SEPA_MIN:
                CrcBit = CrcBit + "1"
            else:
                CrcBit = CrcBit + "0"

    except:
        print "ERR_RANGE_1"
        exit(0)

    Crc = int(bin2dec(CrcBit))

    if DEBUG_MODE == 1:
        print "crc : " + CrcBit + " int( {0:>3} )".format(Crc)

    Humidity    = int(bin2dec(HumidityBitHigh))    + int(bin2dec(HumidityBitLow))
    Temperature = int(bin2dec(TemperatureBitHigh)) + int(bin2dec(TemperatureBitLow))

    if Crc == 0:
        print "ERR_DATA"
        end_flag = end_flag + 1
        continue

    if Humidity + Temperature - Crc != 0:
        print "ERR_CRC"
        end_flag = end_flag + 1
        continue

    print "Humidity   : {0:>3} %".format(DIFF_HUMI + Humidity) 
    print "Temperature: {0:>3} C".format(DIFF_TEMP + Temperature) 
    end_flag = 99

