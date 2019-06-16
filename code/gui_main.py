import PySimpleGUI as sg
from Face_finder import Face_finder
from Face_finder import sub_picture
from Face_finder import AipFace
from Face_finder import base64
from PIL import Image
import threading
import cv2
import datetime

def change_img_to_png(imge_filename):
    img = Image.open(imge_filename)
    imge_filename_png = imge_filename.replace('jpg','png')
    img.save(imge_filename_png)
    return imge_filename_png

#将代码链接到gui
class gui:
    #window
    #finder
    def __init__(self):

        #登陆界面
        layout_landing = [
                          [sg.Text('登陆',size=(240,1),justification='center', font=(None, 20), relief=sg.RELIEF_RIDGE)],
                          [sg.Text('',size=(240,1),justification='center', font=(None, 15), relief=sg.RELIEF_RIDGE)],
                          [sg.Text(('groupIDlist')),sg.InputText('',key = 'groupIDlist')],
                          [sg.Text('',size=(240,1),justification='center', font=(None, 15), relief=sg.RELIEF_RIDGE)],
                          [sg.Text(('App_id     ')),sg.InputText('',key = 'App_id')],
                          [sg.Text('',size=(240,1),justification='center', font=(None, 15), relief=sg.RELIEF_RIDGE)],
                          [sg.Text(('Aip_id      ')),sg.InputText('',key = 'Aip_id')],
                          [sg.Text('',size=(240,1),justification='center', font=(None, 15), relief=sg.RELIEF_RIDGE)],
                          [sg.Text(('Secret_key')),sg.InputText('',password_char='*',key = 'Secret_key')],
                          [sg.Text('',size=(240,1),justification='center', font=(None, 15), relief=sg.RELIEF_RIDGE)],
                          [sg.Button(button_text = '登陆',key = 'landing_submit'),sg.Exit(button_text = '退出',key = 'landing_exit')]

                          ]
        #主界面
        frame_layout_Attendance_list = [[sg.Output(size = (40,7),key = 'Attendance_list')]]
        frame_layout_Absent_list = [[sg.Output(size = (40,7),key = 'Absent_list')]]
        layout = [
            [sg.Text('点名系统',size=(720,1),justification='center', font=(None, 25), relief=sg.RELIEF_RIDGE)],
            [sg.Image(filename='C:/data/soft_engnering/linjunjie/1.png',size = (720,480),key = 'IMAGE')],
            [sg.Text('_' *680)],
            [sg.Text(' ' *680)],
            [sg.Text('图片路径'),sg.InputText('请输入图片路径',size = (80,1),key = 'IMAGE_FILE'),sg.FileBrowse('选择')],
            [sg.Frame('到场名单',frame_layout_Attendance_list,font='Any 12',title_color='blue'),
             sg.Frame('缺席名单',frame_layout_Absent_list,font='Any 12',title_color='blue')],
            [sg.Button(button_text = '导出',key = 'output',size = (8,1)),sg.Submit('提交',key = 'submit',size = (8,1)),sg.Exit(button_text = '退出',key = 'exit',size = (8,1))]
             ]
        self.Attend_list = []
        self.unAttend_list = []
        self.window = sg.Window('点名系统',default_element_size=(40, 1), grab_anywhere=False,size = (720,820),location = (0,0)).Layout(layout)
        self.land_window = sg.Window('登陆界面', grab_anywhere=False,size = (360,400),location = (0,0)).Layout(layout_landing)

    def set_parmeter(self,groupIdlist,App_id,Aip_id,Secret_key):
        self.__groupIDlist = groupIdlist
        self.__App_id = App_id
        self.__Aip_id = Aip_id
        self.__Secret_key = Secret_key

    def run_finder(self,path):
       
        thread_lock_for_detect_face = threading.Lock()
        img = cv2.imread(path)
        self.finder = Face_finder(img)
        self.finder.set_parameter_of_aip(self.__groupIDlist,self.__App_id,self.__Aip_id,self.__Secret_key)
        self.finder.start_server()

        #识别图中的人脸
        search_result = self.finder.detect_face()
        face_list = self.finder.process_the_face_detected(search_result,img)
        

        #多线程请求识别人脸
        #建立线程
        thread_list = []
        for i in range(len(face_list)):
            thread_list.append(threading.Thread(target = self.finder.thread_for_detect_face,
                                          args = (face_list[i],thread_lock_for_detect_face,i)))

        for i in range(len(face_list)):
            thread_list[i].start()

        for i in range(len(face_list)):
            thread_list[i].join()

        detect_result = self.finder.result_list
        return [detect_result,search_result]

     
    
        


    def mark_people(self,picture,result):
        img = cv2.imread(picture);
        
        face_num = result['result']['face_num']
        face_locations = []

        #获得脸的位置信息
        for i in range(face_num):
            single_face_location = sub_picture(result['result']['face_list'][i]['location']['left'],
                                               result['result']['face_list'][i]['location']['top'],
                                               result['result']['face_list'][i]['location']['height'],
                                               result['result']['face_list'][i]['location']['width'])
            face_locations.append(single_face_location)

        for i in range(face_num):
            cv2.rectangle(img,
                          (face_locations[i].left,face_locations[i].top),
                          (face_locations[i].left+face_locations[i].width,face_locations[i].top+face_locations[i].height),
                          (255,255,0),
                          1)

        save_marked_path = picture.replace('.png','_mark.png')
        img = cv2.resize(img,(int(img.shape[1]*480/img.shape[0]),int(img.shape[0]*480/img.shape[0])))
        cv2.imwrite(save_marked_path,img)

        return save_marked_path


    def run_gui(self):
        while True:
            [event,values] = self.window.Read()
            if event=='output':
                if len(self.Attend_list)!=0 and len(self.unAttend_list)!=0:
                    time = datetime.datetime.now().strftime('%Y-%m-%d')
                    f = open(time+'.txt','w')
                    
                    #到场名单
                    f.write('到场名单为：\n')
                    for i in range(len(self.Attend_list)):
                        f.write(self.Attend_list[i]+'\n')

                    #缺席名单
                    f.write('缺席名单为：\n')
                    for i in range(len(self.unAttend_list)):
                        f.write(self.unAttend_list[i]+'\n')
                    f.close()
                else:
                    sg.Popup('未生成名单！请点名后再保存！') 
                print('')
            elif event=='submit':
                picture_path = values['IMAGE_FILE']

                #图片的格式可能存疑，需要对图片的格式进行判断。
                #判断图片类型如果不是png，则需要转换为png
                type = picture_path[len(picture_path)-4:len(picture_path)-1]
                if type != 'png':
                 picture_path = change_img_to_png(picture_path)

                #运行识别程序
                result = []
                result = self.run_finder(picture_path)
               
                #返回用户组的成员名单
                user_list = self.finder.return_user_list(self.__groupIDlist)
                user_list = user_list['result']['user_id_list']
                #标注图片
                marked_img_path = self.mark_people(picture_path,result[1])

                #在gui中显示结果

                #显示图片
                sg.Image.Update( self.window.Element('IMAGE'),marked_img_path)
                #显示人名
                #到场名单
                people_name = [];
                for i in range(len(result[0])):
                    people_name.append(result[0][i].name)

                combin_list = user_list + people_name

                Attend_list = people_name;
                unAttend_list = [];

                mark2 = 0
                for i in range(len(user_list)):
                    if mark2 == 0 and i>=1:
                        unAttend_list.append(user_list[i-1])
                    mark2=0
                    for j in range(len(Attend_list)):
                        if user_list[i] == Attend_list[j]:
                            mark2 = 1
                            break;

        
                

                sg.Output.Update(self.window.Element('Attendance_list'),Attend_list )
                sg.Output.Update(self.window.Element('Absent_list'),unAttend_list )
                self.Attend_list = Attend_list
                self.unAttend_list = unAttend_list

                print('')
            elif(event == 'exit'):
                break
    
    def run_land_gui(self):
        while True:
            [event,values] = self.land_window.Read()
            
            if event =='landing_submit':
                #sg.Popup('测试！')
                groupIDlist = values['groupIDlist']
                App_id = values['App_id']
                Aip_id = values['Aip_id']
                Secret_key = values['Secret_key']
                self.set_parmeter(groupIDlist,App_id,Aip_id,Secret_key)
                client = AipFace(self.__App_id,self.__Aip_id,self.__Secret_key)
                test = client.getGroupUsers(groupIDlist)
                if test['error_code'] !=0:
                    sg.Popup('密码或账号输入错误')
                    sg.Input.Update(self.land_window.Element('groupIDlist'),'' )
                    sg.Input.Update(self.land_window.Element('App_id'),'' )
                    sg.Input.Update(self.land_window.Element('Aip_id'),'' )
                    sg.Input.Update(self.land_window.Element('Secret_key'),'' )
                else:
                    sg.Popup('登陆成功')
                    self.run_gui()
                    break
                    


            elif event =='landing_exit':
                break
        

###################################

if __name__ == "__main__":
    print('start')

    window_gui = gui()
    window_gui.run_land_gui()
    #window_gui.run_gui()



#第一个任务向服务器请求用户组名单
