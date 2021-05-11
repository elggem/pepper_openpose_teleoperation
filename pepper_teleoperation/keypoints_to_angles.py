import sys

from socket_receive import SocketReceive

import numpy as np

class KeypointsToAngles:
    # Body parts associated to their index
    body_mapping = {'0':  "Nose", 
                    '1':  "Neck", 
                    '2':  "RShoulder",
                    '3':  "RElbow",
                    '4':  "RWrist",
                    '5':  "LShoulder",
                    '6':  "LElbow",
                    '7':  "LWrist",
                    '8':  "MidHip"}
    

    ## method __init__
    #
    # Initialization method 
    def __init__(self):
        # init start flag
        self.start_flag = True

        # initialize socket for receiving the 3D keypoints
        self.sr = SocketReceive()

        print("Start receiving keypoints...")
    
    ## method __del__
    #
    # delete class
    def __del__(self):
        self.stop_receiving()
        del self.sr

    ## method stop_receiving
    #
    # stop the receive keypoints loop
    def stop_receiving(self):
        self.start_flag = True

    ## function vector_from_points
    #
    # calculate 3D vector from two points ( vector = P2 - P1 )
    def vector_from_points(self, P1, P2):
        vector = [P2[0] - P1[0], P2[1] - P1[1], P2[2] - P1[2]]
        return vector

    ## function obtain_LShoulderPitchRoll_angles
    # 
    # Calculate left shoulder pitch and roll angles
    def obtain_LShoulderPitchRoll_angles(self, P1, P5, P6, P8):
        # Construct 3D vectors (bones) from points
        v_1_5 = self.vector_from_points(P1, P5)
        v_5_1 = self.vector_from_points(P5, P1)
        v_6_5 = self.vector_from_points(P6, P5)
        v_5_6 = self.vector_from_points(P5, P6)

        # # Calculate normal of the 1_5_6 plane
        # n_1_5_6 = np.cross(v_1_5, v_6_5)

        # Left torso Z axis
        v_8_1 = self.vector_from_points(P8, P1)

        # Left torso X axis 
        n_8_1_5 = np.cross(v_8_1, v_5_1)
        # n_8_1_5 = np.cross(v_5_1, v_8_1)

        # Left torso Y axis
        # R_left_torso = np.cross(v_8_1, n_8_1_5)
        R_left_torso = np.cross(n_8_1_5, v_8_1) # Left-right arm inverted

        # Intermediate angle to calculate positive or negative final Pitch angle
        intermediate_angle = np.arccos(np.dot(v_5_6, v_8_1) / (np.linalg.norm(v_5_6))*(np.linalg.norm(v_8_1)))
        
        # Module of the LShoulderPitch angle
        theta_LSP_module = np.arccos(np.dot(v_8_1, np.cross(R_left_torso, v_5_6))/(np.linalg.norm(v_8_1) * np.linalg.norm(np.cross(R_left_torso, v_5_6))))

        # Positive or negative LShoulderPitch
        if intermediate_angle <= np.pi/2 :
            LShoulderPitch = -theta_LSP_module
        else:
            LShoulderPitch = theta_LSP_module
    
        # Formula for LShoulderRoll
        # LShoulderRoll = (np.pi/2) - np.arccos((np.dot(v_5_6, R_left_torso)) / (np.linalg.norm(v_5_6) * np.linalg.norm(R_left_torso)))
        LShoulderRoll =  np.arccos((np.dot(v_5_6, R_left_torso)) / (np.linalg.norm(v_5_6) * np.linalg.norm(R_left_torso))) - (np.pi/2) # Left-right arm inverted

        # Return LShoulder angles
        return LShoulderPitch, LShoulderRoll
    
    ## function obtain_RShoulderPitchRoll_angles
    # 
    # Calculate right shoulder pitch and roll angles
    def obtain_RShoulderPitchRoll_angle(self, P1, P2, P3, P8):
        # Construct 3D vectors (bones) from points
        v_2_3 = self.vector_from_points(P2, P3)
        v_1_2 = self.vector_from_points(P1, P2)
        v_2_1 = self.vector_from_points(P2, P1)

        # Right torso Z axis
        v_8_1 = self.vector_from_points(P8, P1)
        # Right torso X axis
        n_8_1_2 = np.cross(v_8_1, v_1_2)
        # Right torso Y axis
        # R_right_torso = np.cross(v_8_1, n_8_1_2) 
        R_right_torso = np.cross(n_8_1_2,v_8_1) # Left-right arm inverted

        # # Normal to plane 1_2_3
        # n_1_2_3 = np.cross(v_2_3, v_2_1)

        # Module of the RShoulderPitch angle
        theta_RSP_module = np.arccos(np.dot(v_8_1, np.cross(R_right_torso, v_2_3))/(np.linalg.norm(v_8_1) * np.linalg.norm(np.cross(R_right_torso, v_2_3))))
        
        # Intermediate angle to calculate positive or negative final Pitch angle
        intermediate_angle = np.arccos(np.dot(v_2_3, v_8_1) / (np.linalg.norm(v_2_3))*(np.linalg.norm(v_8_1)))

        # Positive or negative RShoulderPitch
        if intermediate_angle <= np.pi/2 :
            RShoulderPitch = - theta_RSP_module
        else:
            RShoulderPitch = theta_RSP_module

        # Formula for RShoulderRoll
        # RShoulderRoll =  (np.pi/2) - np.arccos((np.dot(v_2_3, R_right_torso)) / (np.linalg.norm(v_2_3) * np.linalg.norm(R_right_torso))) 
        RShoulderRoll =  np.arccos((np.dot(v_2_3, R_right_torso)) / (np.linalg.norm(v_2_3) * np.linalg.norm(R_right_torso))) - (np.pi/2) # Left-right arm inverted

        # Return RShoulder angles
        return RShoulderPitch, RShoulderRoll

    ## function obtain_LElbowYawRoll_angle
    # 
    # Calculate left elbow yaw and roll angles
    def obtain_LElbowYawRoll_angle(self, P1, P5, P6, P7):
        # Construct 3D vectors (bones) from points
        v_6_7 = self.vector_from_points(P6, P7)
        v_1_5 = self.vector_from_points(P1, P5)

        # Left arm Z axis
        v_6_5 = self.vector_from_points(P6, P5)
        # Left arm X axis
        # n_1_5_6 = np.cross(v_6_5, v_1_5) 
        n_1_5_6 = np.cross(v_1_5, v_6_5) # Right-Left arms inverted
        # Left arm Y axis
        R_left_arm = np.cross(v_6_5, n_1_5_6)

        # Normal of 5_6_7 plane
        n_5_6_7 = np.cross(v_6_5, v_6_7) 

        # Formula to calculate the module of LElbowYaw angle
        theta_LEY_module = np.arccos(np.dot(n_1_5_6, n_5_6_7) / (np.linalg.norm(n_1_5_6) * np.linalg.norm(n_5_6_7))) 

        # Intermediate angles to choose the right LElbowYaw angle
        intermediate_angle_1 = np.arccos(np.dot(v_6_7, n_1_5_6) / (np.linalg.norm(v_6_7) * np.linalg.norm(n_1_5_6)))
        intermediate_angle_2 = np.arccos(np.dot(v_6_7, R_left_arm) / (np.linalg.norm(v_6_7) * np.linalg.norm(R_left_arm)))

        # Choice of the correct LElbowYaw angle using intermediate angles values
        if intermediate_angle_1 <= np.pi/2:
            LElbowYaw = -theta_LEY_module 
        else:
            if intermediate_angle_2 > np.pi/2:
                LElbowYaw = theta_LEY_module 
            elif intermediate_angle_2 <= np.pi/2:
                LElbowYaw = theta_LEY_module - (2 * np.pi)

        # Formula for LElbowRoll angle
        LElbowRoll = np.arccos(np.dot(v_6_7, v_6_5) / (np.linalg.norm(v_6_7) * np.linalg.norm(v_6_5))) - np.pi
        
        # Return LElbow angles
        return LElbowYaw, LElbowRoll

 
    ## function obtain_RElbowYawRoll_angle
    # 
    # Calculate right elbow yaw and roll angles
    def obtain_RElbowYawRoll_angle(self, P1, P2, P3, P4):
        # Construct 3D vectors (bones) from points
        v_3_4 = self.vector_from_points(P3, P4)
        v_1_2 = self.vector_from_points(P1, P2)
        # v_2_3 = self.vector_from_points(P2, P3)

        # Left arm Z axis
        v_3_2 = self.vector_from_points(P3, P2)
        # Left arm X axis
        n_1_2_3 = np.cross(v_3_2, v_1_2)  # -- OUT --
        # n_1_2_3 = np.cross(v_1_2, v_3_2)    # -- IN --  Right-left arms inverted
        # Left arm Y axis
        R_right_arm = np.cross(v_3_2, n_1_2_3)

        # normal to the 2_3_4 plane
        # n_2_3_4 = np.cross(v_3_2, v_3_4)
        n_2_3_4 = np.cross(v_3_4, v_3_2)


        # Formula to calculate the module of RElbowYaw angle
        theta_REY_module = np.arccos(np.dot(n_1_2_3, n_2_3_4) / (np.linalg.norm(n_1_2_3) * np.linalg.norm(n_2_3_4)))

        # Intermediate angles to choose the right RElbowYaw angle
        intermediate_angle_1 = np.arccos(np.dot(v_3_4, n_1_2_3) / (np.linalg.norm(v_3_4) * np.linalg.norm(n_1_2_3)))
        intermediate_angle_2 = np.arccos(np.dot(v_3_4, R_right_arm) / (np.linalg.norm(v_3_4) * np.linalg.norm(R_right_arm)))

        # # Choice of the correct RElbowYaw angle using intermediate angles values
        # print("Module REY: %f" % theta_REY_module)
        # print("IntANg1: %f" % intermediate_angle_1)
        # print("IntANg2: %f" % intermediate_angle_2)

        if intermediate_angle_1 <= np.pi/2:
            RElbowYaw = theta_REY_module
        else:
            if intermediate_angle_2 > np.pi/2:
                RElbowYaw = -theta_REY_module

            elif intermediate_angle_2 <= np.pi/2:
                RElbowYaw = theta_REY_module - (2 * np.pi)
            
        # Formula for RElbowRoll angle
        RElbowRoll = np.pi - np.arccos(np.dot(v_3_4, v_3_2) / (np.linalg.norm(v_3_4) * np.linalg.norm(v_3_2)))

        # Return RElbow angles
        return RElbowYaw, RElbowRoll

    def obtain_HipPitch_angles(self, P0_curr, P8_curr):
        # Calculate vector
        v_0_8_curr = self.vector_from_points(P0_curr, P8_curr)

        # Normals to axis planes
        n_YZ = [1, 0, 0]
        n_XZ = [0, 1, 0]
        n_XY = [0, 0, 1]

        # Project vectors on YZ plane
        v_0_8_curr_proj = v_0_8_curr - np.dot(v_0_8_curr, n_YZ)

        # Calculate HipPitch module
        # omega_HP_module = np.arccos((np.dot(v_0_8_prev_proj, v_0_8_curr_proj))/(np.linalg.norm(v_0_8_prev_proj) * np.linalg.norm(v_0_8_curr_proj)))
        omega_HP_module = np.arccos((np.dot(n_XZ, v_0_8_curr_proj))/(np.linalg.norm(n_XZ) * np.linalg.norm(v_0_8_curr_proj)))

        # Intermediate vector and angle to calculate positive or negative pich
        intermediate_angle = np.arccos(np.dot(v_0_8_curr_proj, n_XY) / (np.linalg.norm(v_0_8_curr_proj) * np.linalg.norm(n_XY)))

        # Choose positive or negative pitch angle
        if intermediate_angle > np.pi/2:
            HipPitch = np.pi - omega_HP_module 
        else:
            HipPitch = omega_HP_module - np.pi
        
        return HipPitch
    
    def obtain_HeadYaw_angles(self, P0, P1):
        # print(P0)
        # print(P1)

        # Calculate vector
        v_1_0 = self.vector_from_points(P1, P0)
        # print(v_1_0)
        # Normals to axis planes
        n_YZ = [1, 0, 0]
        n_XZ = [0, 1, 0]
        n_XY = [0, 0, 1]

        # Project vector on XZ plane
        v_1_0_proj = v_1_0 - np.dot(v_1_0, n_XZ)
        print(v_1_0_proj)
        # Calculate HeadYaw module
        omega_HEY_module = np.pi - np.arccos((np.dot(v_1_0_proj, n_XY)) / (np.linalg.norm(v_1_0_proj) * np.linalg.norm(n_XY)))

        # Intermediate vector and angle to calculate positive or negative pich
        intermediate_angle = np.arccos(np.dot(v_1_0_proj, n_YZ) / (np.linalg.norm(v_1_0_proj) * np.linalg.norm(n_YZ)))

        # print("Module: %f" % (omega_HEY_module * 180/np.pi))
        # print("IA: %f" % (intermediate_angle * 180/np.pi))

        # Choose positive or negative Yaw angle
        if intermediate_angle > np.pi/2:
            HeadYaw = omega_HEY_module 
        else:
            HeadYaw = -omega_HEY_module  
        
        return HeadYaw


    ## function invert_right_left
    #
    # Invert left and right arm
    def invert_right_left(self, wp_dict):
        temp_dict = {}
        # print("1")
        # print(wp_dict)

        if '0' in wp_dict:
            temp_dict['0'] = wp_dict['0']
        if '1' in wp_dict:
            temp_dict['1'] = wp_dict['1']
        if '2' in wp_dict:
            temp_dict['5'] = wp_dict['2']
        if '3' in wp_dict:
            temp_dict['6'] = wp_dict['3']
        if '4' in wp_dict:
            temp_dict['7'] = wp_dict['4']

        if '5' in wp_dict:
            temp_dict['2'] = wp_dict['5']
        if '6' in wp_dict:
            temp_dict['3'] = wp_dict['6']
        if '7' in wp_dict:
            temp_dict['4'] = wp_dict['7']
        if '8' in wp_dict:
            temp_dict['8'] = wp_dict['8']

        # print(temp_dict)
        return temp_dict

    def get_angles(self):
        try:

            # LShoulderPitch and LShoulderRoll needed keypoints
            LS = ['1','5','6','8']

            # LElbowYaw and LElbowRoll needed keypoints
            LE = ['1','5','6','7']

            # RShoulderPitch and RShoulderRoll needed keypoints
            RS = ['1','2','3','8']

            # RElbowYaw and RElbowRoll needed keypoints
            RE = ['1','2','3','4']   

            # HipPitch needed keypoints
            HP = ['0', '8']

            # HeadYaw needed keypoints
            HEY = ['0', '1']

            # Init angles
            LShoulderPitch = LShoulderRoll = LElbowYaw = LElbowRoll = RShoulderPitch = RShoulderRoll = RElbowYaw = RElbowRoll = HipPitch = HeadYaw = None

            # Receive keypoints from socket
            wp_dict = self.sr.receive_keypoints()

            # Invert right arm with left arm
            wp_dict = self.invert_right_left(wp_dict) 

            # HipPitch angles 
            if all (body_part in wp_dict for body_part in HP):
                HipPitch = self.obtain_HipPitch_angles(wp_dict.get(HP[0]), wp_dict.get(HP[1]))
            
            # HeadYaw angles 
            if all (body_part in wp_dict for body_part in HEY):
                HeadYaw = self.obtain_HeadYaw_angles(wp_dict.get(HEY[0]), wp_dict.get(HEY[1]))
                # Print angles
                print("HeadYaw:")
                print((HeadYaw * 180 )/ np.pi)

            # LShoulder angles 
            if all (body_part in wp_dict for body_part in LS):        
                LShoulderPitch, LShoulderRoll = self.obtain_LShoulderPitchRoll_angles(wp_dict.get(LS[0]), wp_dict.get(LS[1]), wp_dict.get(LS[2]), wp_dict.get(LS[3]))

                # # # Print angles
                # print("LShoulderPitch:")
                # print((LShoulderPitch * 180 )/ np.pi)

                # print("LShoulderRoll:")
                # print((LShoulderRoll * 180)/ np.pi)

            # LElbow angles (Green arm on OpenPose)
            if all (body_part in wp_dict for body_part in LE):
                LElbowYaw, LElbowRoll = self.obtain_LElbowYawRoll_angle(wp_dict.get(LE[0]), wp_dict.get(LE[1]), wp_dict.get(LE[2]), wp_dict.get(LE[3]))

                # Print angles
                # print("LElbowYaw:")
                # print((LElbowYaw * 180 )/ np.pi)

                # print("LElbowRoll:")
                # print((LElbowRoll * 180)/ np.pi)

            # RShoulder angles
            if all (body_part in wp_dict for body_part in RS):        
                RShoulderPitch, RShoulderRoll = self.obtain_RShoulderPitchRoll_angle(wp_dict.get(RS[0]), wp_dict.get(RS[1]), wp_dict.get(RS[2]), wp_dict.get(RS[3]))

                # # Print angles
                # print("RShoulderPitch:")
                # print((RShoulderPitch * 180 )/ np.pi)

                # print("RShoulderRoll:")
                # print((RShoulderRoll * 180)/ np.pi)


            # # RElbow angles
            if all (body_part in wp_dict for body_part in RE):
                RElbowYaw, RElbowRoll = self.obtain_RElbowYawRoll_angle(wp_dict.get(RE[0]), wp_dict.get(RE[1]), wp_dict.get(RE[2]), wp_dict.get(RE[3]))
                
                # Print angles
                # print("RElbowYaw:")
                # print((RElbowYaw * 180 )/ np.pi)

                # print("RElbowRoll:")
                # print((RElbowRoll * 180)/ np.pi)
            
            return LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, HipPitch, HeadYaw
                
                
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            sys.exit(-1)
