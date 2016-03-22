import picamera, httplib, requests, io, time
from multiprocessing import Process, Pipe

def postImage():
    camera = picamera.PiCamera()
    s = requests.Session()

    camera.capture('images/file.jpg')

    camera.close()

    files = {'file': ('file.jpg', open('images/file.jpg', 'rb'), 'image/jpeg')}

    r = s.post('http://pelji.se/postImage/', data={'thetitle': 'filefile'}, files=files)

    print r.text
    print r.request.headers

def streaming():
    camera = picamera.PiCamera()
    stream = io.BytesIO()
    s = requests.Session()

    print '[ST] Connecting video stream'

    while True: # connect to server loop
        try:
            conn = httplib.HTTPConnection('pelji.se', 80, timeout = 1)
            print "[ST] Video stream connected?"

            while True: # resolution adjustment loop
                print 'about to set camera resolution'
                camera.resolution = (640, 480)
                camera.framerate = 16
                camera.shutter_speed = 10000
                print 'camera resolution set, about to go for image'

                for image in camera.capture_continuous(stream, format='jpeg', use_video_port=True, quality=10):
                    print 'image'
                    try:
                        print 'trying image'
                        dolzina = stream.tell()
                        podatki = stream.getvalue()
                        s.post('http://pelji.se/pub/?id=testis', data=podatki, headers={'Content-Length': dolzina})
                        print 'posted image to pub'

                    except socket.timeout: #sending image timeout
                        continue

                    stream.seek(0)
                    stream.truncate()

        except KeyboardInterrupt:
            camera.close()
            conn.close()
            exit()

        except Exception as e:
            print '[ST] ' + str(e)
            camera.close()
            conn.close()
            streaming()

def runStreaming():
    streamProcess = Process(target = streaming)
    streamProcess.start()
    streamProcess.join()

def main():
    runStreaming()

if __name__ == '__main__':
    main()
