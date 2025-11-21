import ctypes as ct
import time
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import pyllt as llt
import csv
from datetime import datetime

scanner_type = ct.c_int(0)

exposure_time = 100 # microseconds
idle_time = 3900 # microseconds
timestamp = (ct.c_ubyte*16)()
available_resolutions = (ct.c_uint*4)()
available_interfaces = (ct.c_uint*6)()
lost_profiles = ct.c_int()
shutter_opened = ct.c_double(0.0)
shutter_closed = ct.c_double(0.0)
profile_count = ct.c_uint(0)

null_ptr_short = ct.POINTER(ct.c_ushort)()
null_ptr_int = ct.POINTER(ct.c_uint)()

hLLT = llt.create_llt_device(llt.TInterfaceType.INTF_TYPE_ETHERNET)

ret = llt.get_device_interfaces_fast(hLLT, available_interfaces, len(available_interfaces))
if ret < 1:
    raise ValueError("Error getting interfaces : " + str(ret))

ret = llt.set_device_interface(hLLT, available_interfaces[0], 0)
if ret < 1:
    raise ValueError("Error setting device interface: " + str(ret))

ret = llt.connect(hLLT)
if ret < 1:
    raise ConnectionError("Error connect: " + str(ret))

ret = llt.get_resolutions(hLLT, available_resolutions, len(available_resolutions))
if ret < 1:
    raise ValueError("Error getting resolutions : " + str(ret))

resolution = available_resolutions[0]
ret = llt.set_resolution(hLLT, resolution)
if ret < 1:
    raise ValueError("Error getting resolutions : " + str(ret))

profile_buffer = (ct.c_ubyte*(resolution*64))()
x = (ct.c_double * resolution)()
z = (ct.c_double * resolution)()
intensities = (ct.c_ushort * resolution)()

ret = llt.get_llt_type(hLLT, ct.byref(scanner_type))
if ret < 1:
    raise ValueError("Error scanner type: " + str(ret))

ret = llt.set_profile_config(hLLT, llt.TProfileConfig.PROFILE)
if ret < 1:
    raise ValueError("Error setting profile config: " + str(ret))

ret = llt.set_feature(hLLT, llt.FEATURE_FUNCTION_TRIGGER, llt.TRIG_INTERNAL)
if ret < 1:
    raise ValueError("Error setting trigger: " + str(ret))

ret = llt.set_feature(hLLT, llt.FEATURE_FUNCTION_EXPOSURE_TIME, exposure_time)
if ret < 1:
    raise ValueError("Error setting exposure time: " + str(ret))

ret = llt.set_feature(hLLT, llt.FEATURE_FUNCTION_IDLE_TIME, idle_time)
if ret < 1:
    raise ValueError("Error idle time: " + str(ret))

time.sleep(0.12)

ret = llt.transfer_profiles(hLLT, llt.TTransferProfileType.NORMAL_TRANSFER, 1)
if ret < 1:
    raise ValueError("Error starting transfer profiles: " + str(ret))

timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"profile_data_testv2_{timestamp_str}.csv"
csv_file = open(csv_filename, 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Profile_Number', 'Point_Index', 'X', 'Z', 'Intensity'])

print(f"Saving data to: {csv_filename}")

fig = plt.figure(facecolor='white', figsize=(10, 8))
ax1 = plt.subplot(211)
ax1.grid()
ax1.set_xlabel('x')
ax1.set_ylabel('z')
ax1.set_xlim(-60, 60)
ax1.set_ylim(25, 350)
line1, = ax1.plot([], [], 'g.', label="z", markersize=2)

ax2 = plt.subplot(212)
ax2.grid()
ax2.set_xlabel('x')
ax2.set_ylabel('intensities')
ax2.set_xlim(-60, 60)
ax2.set_ylim(0, 1200)
line2, = ax2.plot([], [], 'r.', label="intensities", markersize=1)

ax1.legend()
ax2.legend()

profile_counter = [0]

def update(frame):
    ret = llt.get_actual_profile(hLLT, profile_buffer, len(profile_buffer), llt.TProfileConfig.PROFILE,
                                ct.byref(lost_profiles))
    
    if ret == len(profile_buffer):
        ret = llt.convert_profile_2_values(hLLT, profile_buffer, resolution, llt.TProfileConfig.PROFILE, 
                                        scanner_type, 0, 1, null_ptr_short, intensities, null_ptr_short, 
                                        x, z, null_ptr_int, null_ptr_int)
        
        if ret & llt.CONVERT_X and ret & llt.CONVERT_Z and ret & llt.CONVERT_MAXIMUM:
            line1.set_data(x, z)
            line2.set_data(x, intensities)
            
            profile_counter[0] += 1
            ax1.set_title(f'Profile {profile_counter[0]} - Z coordinates')
            ax2.set_title(f'Profile {profile_counter[0]} - Intensities')
            
            for i in range(resolution):
                csv_writer.writerow([profile_counter[0], i, x[i], z[i], intensities[i]])
            
            if profile_counter[0] % 10 == 0:
                csv_file.flush()
                print(f"Saved profile {profile_counter[0]}")
    
    return line1, line2

try:
    print("Starting real-time acquisition. Close the plot window to stop...")
    ani = FuncAnimation(fig, update, interval=10, blit=True, cache_frame_data=False)
    plt.tight_layout()
    plt.show()
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    csv_file.close()
    ret = llt.transfer_profiles(hLLT, llt.TTransferProfileType.NORMAL_TRANSFER, 0)
    ret = llt.disconnect(hLLT)
    ret = llt.del_device(hLLT)
    print(f"Disconnected and cleaned up")
    print(f"Total profiles saved: {profile_counter[0]}")
    print(f"Data saved to: {csv_filename}")

