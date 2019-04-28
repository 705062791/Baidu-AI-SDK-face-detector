#from Face_finder import *
import Face_finder
import threading
import cv2
picture_path = 'C:/data/soft_engnering/test/1.jpg'
groupIdlist = 'test'
App_id = '16085513'
Aip_id = 'ghqF0ATL4OzZs2hhfxEe4Eg3'
Secret_key = 'DeqeFVPDPm5WkIleoDSlb66IN0TCCDeM'
thread_lock_for_detect_face = threading.Lock()

input_picture = cv2.imread(picture_path)

#启动
FaceFinder = Face_finder.Face_finder(input_picture)

FaceFinder.set_parameter_of_aip(App_id,Aip_id,Secret_key)

FaceFinder.start_server()

#识别图中的人脸
search_result = FaceFinder.detect_face()

face_list = FaceFinder.process_the_face_detected(search_result,input_picture)


#多线程请求识别人脸
#建立线程
thread_list = []
for i in range(len(face_list)):
    thread_list.append(threading.Thread(target = FaceFinder.thread_for_detect_face,
                                        args = (face_list[i],thread_lock_for_detect_face,i)))

for i in range(len(face_list)):
    thread_list[i].start()

for i in range(len(face_list)):
    thread_list[i].join()

detect_result = FaceFinder.result_list

print('over')
