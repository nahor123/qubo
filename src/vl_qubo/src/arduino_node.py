#!/usr/bin/env python

#sgillen - this program serves as a node that offers the arduino up to the rest of the ros system.


# the packets send to the arduino should be in the following format: p<data>!
# p tells the arduino which command to execute, the data that follows will depend on which command this is
# in general the , character is used as a delimiter, and the ! is used to mark the end of the message

# commands so far
# t,x0,x1,x2,x3,x4,x5,x6,x7!    - this sets all 8 thruster values
# d!                            - this requests the most recent depth value from the arduino (TODO)

import serial, time, sys, select
import rospy

num_thrusters = 8

##command variables (should we make this module a class??)
roll_cmd  = 0
pitch_cmd = 0
yaw_cmd   = 0
depth_cmd = 0
surge_cmd = 0
sway_cmd  = 0



#reads a command from stdin
def read_cmd_stdin():
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
      line = sys.stdin.readline()
      line = line.rstrip()
      if line:
        num_bytes = ser.write(line)
        print  "bytes sent =", num_bytes  


#sends an array of ints to the thrusters using the agreed upon protocol
#the actual over the wire value is t,x1,x2,x3,x4,x5,x6,x7,x8!
def send_thruster_cmds(thruster_cmds):
    cmd_str = "t"
    for cmd in thruster_cmds:
        cmd_str += (",")
        cmd_str += (str(cmd))

    cmd_str += ("!")
    ser.write(cmd_str)
    ##TODO parse return value


##------------------------------------------------------------------------------
# callbacks
def roll_callback(data):
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    roll_cmd = data
    
def pitch_callback(data):
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    pitch_cmd = data
    
def yaw_callback(data):
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    yaw_cmd = data
    
def depth_callback(data):
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    depth_cmd = data
    
def surge_callback(data):
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    surge_cmd = data 
    
def sway_callback(data):
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    sway_cmd = data
    

##------------------------------------------------------------------------------
# main
if __name__ == '__main__':


    #!!! this also restarts the arduino! (apparently)
    ser = serial.Serial('/dev/cu.usbmodem1421',115200, timeout=0,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
    time.sleep(3)
    

    #I can't think of a situation where we want to change the namespace but I guess you never know
    qubo_namespace = "/qubo/"
    
    rospy.init_node('arduino_node', anonymous=False)

    depth_pub = rospy.Publisher(qubo_namespace + 'depth', Int64, queue_size = 10)

    #rospy spins all these up in their own thread, no need to call spin()
    rospy.Subscriber(qubo_namespace + "roll_cmd"  , Int, roll_callback)
    rospy.Subscriber(qubo_namespace + "pitch_cmd" , Int, pitch_callback)
    rospy.Subscriber(qubo_namespace + "yaw_cmd"   , Int, yaw_callback)
    rospy.Subscriber(qubo_namespace + "depth_cmd" , Int, depth_callback)
    rospy.Subscriber(qubo_namespace + "surge_cmd" , Int, surge_callback)
    rospy.Subscriber(qubo_namespace + "sway_cmd"  , Int, sway_callback)

    thruster_commands = [0]*num_thrusters

    rate = rospy.Rate(100) #100Hz
    
    while not rospy.is_shutdown():

        
        depth = get_depth() #TODO
        depth_pub.publish(depth)
        
    
        #thruster layout found here https://docs.google.com/presentation/d/1mApi5nQUcGGsAsevM-5AlKPS6-FG0kfG9tn8nH2BauY/edit#slide=id.g1d529f9e65_0_3
    
        #surge, yaw, sway thrusters
        thruster_commands[0] += (surge_command - yaw_command - sway_command)
        thruster_commands[1] += (surge_command + yaw_command + sway_command)
        thruster_commands[2] += (surge_command + yaw_command - sway_command)
        thruster_commands[3] += (surge_command - yaw_command + sway_command)
	
        #depth, pitch, roll thrusters
        thruster_commands[4] += (depth_command + pitch_command + roll_command)
        thruster_commands[5] += (depth_command + pitch_command - roll_command)
        thruster_commands[6] += (depth_command - pitch_command - roll_command)
        thruster_commands[7] += (depth_command - pitch_command + roll_command)

        
    
        rate.sleep()
    