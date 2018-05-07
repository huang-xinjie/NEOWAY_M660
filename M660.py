import sys
import serial 

class M660(object):
    def __init__(self):
        # check at cmd
        if 'OK' not in self.sendATCmd('at\r'):
            print('AT cmd no response.')
            sys.exit(1)
        # check sim
        if 'OK' not in self.sendATCmd('at+cpin?\r'):
            print('No Sim card. Please check!')
            sys.exit(1)
        # set TE to UCS2
        print(self.sendATCmd('at+cscs="UCS2"\r'))
        # check TE
        print(self.sendATCmd('at+cscs?\r'))
        
    def sendATCmd(self, cmd, expect='K', extra=None):
        result = ''
        ser = None
        try:
            ser = serial.Serial('/dev/ttyUSB0', 115200)
            ser.write(cmd.encode())
            if extra:
                ser.write(bytes((extra,)))
            while True:
                c = ser.read().decode()
                result += c
                if expect in result or 'ERROR' in result:
                    ser.close()
                    return result                
        except KeyboardInterrupt:
            if ser is not None:
                ser.close()
        except serial.serialutil.SerialException:
            print('could not open port /dev/ttyUSB0')

    def sendMessage(self, phone, message):
        phone += 'F'
        # 手机号码每两位反转
        phoneNum = ''.join([phone[i:i+2][::-1] for i in range(0, len(phone), 2)])
        msg = ''.join([hex(ord(c))[2:] for c in message])   # 转为Unicode编码
        msgLen = hex(len(msg)//2)[2:].zfill(2)   # 转为16进制, 并补零
        cmd = '0011000BA1' + phoneNum + '0008A7' + msgLen + msg
        cmdLen = (len(cmd) - 2) // 2    # 去掉SCA(00)后的长度再除以2
        
        preCmd = 'at+cmgs=' + str(cmdLen) + '\r'
        result = self.sendATCmd(preCmd, '>')
        print(result, end='')
        if '>' in result:
            result = self.sendATCmd(cmd, extra=26)
            print(result)


if __name__ == '__main__':
    m660 = M660()
    m660.sendMessage('15002972553', '测试')
