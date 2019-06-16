from aip import AipFace
import cv2 
import base64
import json
import threading


def img_change_to_BASE64(img):
    image = cv2.imencode('.png',img)[1]
    image_code =str(base64.b64encode(image))[2:-1]
    return image_code

class Face_finder:

    #类变量
    #picture 输入的图片
    #app_id 
    #aip_id
    #secret_key
    #client
    #tpye
    #result_list


    def __init__(self,picture):
        self.picture = img_change_to_BASE64(picture)
        self.type = "BASE64"
        self.result_list = []
        
    def set_parameter_of_aip(self,groupId,app_id,aip_id,secret_key):
        self.groupId = groupId
        self.app_id = app_id
        self.aip_id = aip_id
        self.secret_key = secret_key
        #print('The app_id is {}'.format(self.app_id))
        #print('The aip_id is {}'.format(self.aip_id))
        #print('The secret_key is {}'.format(self.secret_key))


    def start_server(self):
        self.client = AipFace(self.app_id,self.aip_id,self.secret_key)
        #print('start server successfully')

    def search_face(self,groupIdlist,picture):
        search_result = self.client.search(img_change_to_BASE64(picture),"BASE64",groupIdlist)
        return search_result


    def return_user_list(self,groupid):
         user_list = self.client.getGroupUsers(groupid);
         return user_list

    def detect_face(self):
        option = {}
        option['max_face_num'] = 10
        option['face_type'] = 'LIVE'
        search_result = self.client.detect(self.picture,self.type,option)
        return search_result

    def process_the_face_detected(self,result,picture):
        face_num = result['result']['face_num']
        face_locations = []

        #获得脸的位置信息
        for i in range(face_num):
            single_face_location = sub_picture(result['result']['face_list'][i]['location']['left'],
                                               result['result']['face_list'][i]['location']['top'],
                                               result['result']['face_list'][i]['location']['height'],
                                               result['result']['face_list'][i]['location']['width'])
            face_locations.append(single_face_location)

        #在原图中截取
        face_list = []

        for i in range(face_num):
            face = picture[face_locations[i].top:(face_locations[i].top+face_locations[i].height),
                           face_locations[i].left:(face_locations[i].left+face_locations[i].width)]

            face_list.append(face)

        #展示截取的图片
        for i in range(face_num):
            cv2.rectangle(picture,
                          (face_locations[i].left,face_locations[i].top),
                          (face_locations[i].left+face_locations[i].width,face_locations[i].top+face_locations[i].height),
                          (255,255,0),
                          1)

        #cv2.namedWindow('show_face')
        #cv2.imshow('show_face',picture)
        #cv2.waitKey(0)

        return face_list

    def thread_for_detect_face(self,picture,locker,num):
        result = self.search_face( self.groupId,picture)
        #进入临界区
        
        locker.acquire()
        #print("detect {}".format(result['result']['user_list'][0]['user_id']))
        people = detected_people(result['result']['user_list'][0]['user_id'],num)
        self.result_list.append(people)
        locker.release()
        


class sub_picture:
    #left
    #top
    #height
    #width

    def __init__(self,x,y,height,width):
        self.left = int(x)
        self.top = int(y)
        self.height = int(height)
        self.width = int(width)
        
class detected_people:
    #name
    #num_in_picture

    def __init__(self,name,num):
        self.name = name
        self.num_in_picture = num