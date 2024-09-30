import serial
import time
import threading

PORT = 'COM10'
BAUD_RATE = 2400
DATA = "Finance Minister Arun Jaitley Tuesday hit out at former RBI governor Raghuram Rajan for predicting that the next banking crisis would be triggered by MSME lending, saying postmortem is easier than taking action when it was required. Rajan, who had as the chief economist at IMF warned of impending financial crisis of 2008, in a note to a parliamentary committee warned against ambitious credit targets and loan waivers, saying that they could be the sources of next banking crisis. Government should focus on sources of the next crisis, not just the last one. In particular, government should refrain from setting ambitious credit targets or waiving loans. Credit targets are sometimes achieved by abandoning appropriate due diligence, creating the environment for future NPAs, Rajan said in the note. Both MUDRA loans as well as the Kisan Credit Card, while popular, have to be examined more closely for potential credit risk. Rajan, who was RBI governor for three years till September 2016, is currently."

def calculate_crc(message):
    crc_val = 0
    res = message.encode('utf-8') #for converting data into bytes 
    for byte in res:
        crc^=byte                   #XOR operation(CRC-logic)
    return crc_val    

def display_speed(interval, total_bytes, direction, stop_event):
    last_bytes=0
    while not stop_event.is_set():
        time.sleep(interval)
        speed = (total_bytes[0] - last_bytes) / interval if interval > 0 else 0
        print(f"{direction} Speed: {speed:.2f} bytes/second", end='\r')
        last_bytes = total_bytes[0]
def send_data():
    with serial.Serial(PORT, BAUD_RATE, timeout=1) as ser:
        total_sent_bytes = [0]
        total_received_bytes = [0]
        stop_event_send = threading.Event()
        stop_event_recv = threading.Event()
        start_send_time = time.time()
        
        speed_thread = threading.Thread(target=display_speed, args=(1, total_sent_bytes, "Send", stop_event_send))
        speed_thread.daemon = True
        speed_thread.start()

        ser.write((DATA + '\n').encode())
        total_sent_bytes[0] += len(DATA) + 1
        print(f"Sent: {DATA}")

        confirmation = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"MCU: {confirmation}")

        end_send_time = time.time()
        stop_event_send.set()
        speed_thread.join()

        elapsed_time = end_send_time - start_send_time
        send_speed = total_sent_bytes[0] / elapsed_time if elapsed_time>0 else 0
        print(f"\nFinal Send Speed: {send_speed:.2f} bytes/second")

        time.sleep(2)

        
        start_recv_time = time.time()
        speed_thread_recv = threading.Thread(target=display_speed, args=(1, total_received_bytes, "Receive", stop_event_recv))
        speed_thread_recv.daemon = True
        speed_thread_recv.start()

        ser.write(b'READ\n')

        time.sleep(0.06)

        received_data = ser.readline().decode().strip()
        total_received_bytes[0] += len(received_data)
        calculated_crc = None  # Ensure calculated_crc is defined
        received_crc_val = None

        if received_data:
            print(f"Received: {received_data}")

            divide = received_data.rsplit("\n", 1)
            if len(divide) == 2:
                received_message, received_crc_val = divide
                received_crc_val = int(received_crc_val)  

                calculated_crc = calculate_crc(received_message)

            if (calculated_crc == received_crc_val):
                print("Checksum valid")
            else:
                print("Checksum invalid")
        else:
            print("No data received from MCU.")
            

        end_recv_time = time.time()
        stop_event_recv.set()
        speed_thread_recv.join()

        recv_speed = 0

        if len(received_data) > 0:
            print(f"Received: {received_data}")
            recv_elapsed_time = end_recv_time - start_recv_time
            recv_speed = total_received_bytes[0]/ (recv_elapsed_time) if recv_elapsed_time>0 else 0
            print(f"Final Receive Speed: {recv_speed:.2f} bytes/second")
        else:
            print("No data received from MCU.")

          
           

if __name__ == "__main__":
    send_data()
