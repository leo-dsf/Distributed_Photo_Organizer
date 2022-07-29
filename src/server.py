import socket
import threading
import os
import imagehash
from PIL import Image
from src.p2p import p2p


class Server:
    def __init__(self, nodeid = None):
        """Constructor"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', 10000))
        sock.listen(1)
        print("Listening on port 10000.")

        # get execution path
        self.image_folder = (os.path.dirname(os.path.abspath(__file__))).removesuffix("src") + "node" + str(nodeid) + "/"
        self.connections = []
        self.peers = []
        self.images = {}
        self.REQ_MSG = "REQUEST_IMAGE"

        self.read_images()
        #self.print_images() # print all images in the node

        # accept connections
        while True:
            c, a = sock.accept()
            cThread = threading.Thread(target=self.handler, args=(c,a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            p2p.connections.append(c)
            #print(p2p.connections)
            self.peers.append(a[0])
            p2p.peers.append(a[0])
            print('Connected to:', a)
            self.send_peers()

    # recv image
    def handler(self, c, a):
        while True:
            data = c.recv(2048)
            if data[0:1] == b'\x14':
                self.forward_img(data[1:], c)
                data = bytes("trying", "utf-8")
            elif data.decode("utf-8").split(" ")[0] == self.REQ_MSG:
                print("Image requested.")
                self.send_img(data.decode("utf-8").split(" ")[1], c)
            else:
                print(data.decode("utf-8"))  
            for connection in self.connections:
                connection.send(data)
            if not data:
                self.connections.remove(c)
                self.peers.remove(a[0])
                c.close()
                self.send_peers()
                break

    # forward image
    def forward_img(self, data, c):
        total_data = data
        while data:
            #print(len(data))
            data = c.recv(2048)
            total_data += data
            # break when there is no more data
            if len(data) != 2048:
                #print(len(data))
                break
        print("Sending image...")
        connection = self.connections[-1]
        connection.sendall(b'\x14' + total_data)
    
    # send peers
    def send_peers(self):
        p = ""
        for peer in self.peers:
            p=p+peer+","
        for connection in self.connections:
            connection.send(b'\x11' + bytes(p, "utf-8"))

    # create a dictionary of hash images and images names
    def read_images(self):
        for filename in os.listdir(self.image_folder):
            if filename.endswith(".png") or filename.endswith(".jpg") or \
            filename.endswith(".jpeg") or filename.endswith(".bmp") or \
            filename.endswith(".gif") or '.jpg' in filename or  filename.endswith(".svg"): 
                img_hash = imagehash.average_hash(Image.open(self.image_folder+filename))
                if str(img_hash) not in self.images:
                    self.images[str(img_hash)] = filename
                else:
                    print("Duplicate image found: " + filename)
                    os.remove(self.image_folder + filename)
                    print("Deleted.")
                    
    # send hashes
    def send_hashes(self):
        ha = ""
        for hash in self.images:
            ha=ha+str(hash)+":"+str(self.images[hash])+","
        for connection in self.connections:
            connection.sendall(b'\x12' + bytes(ha, "utf-8"))

    # send image
    def send_img(self, img_name, connection):
        # get image from img_name   
        # send img_hash to connection
        # check image for dict value instead of key
        if str(img_name) in self.images.values():
            # get key from value
            for key in self.images:
                if self.images[key] == str(img_name):
                    img_hash = key
                    break
            #connection.send(bytes(img_hash, "utf-8"))
            connection.send(b'\x13' + bytes(self.images[img_hash], "utf-8"))
            file = open(self.image_folder + self.images[img_hash], "rb")
            size = os.path.getsize(self.image_folder + self.images[img_hash])
            data = file.read(size)
            #connection.sendall(b'\x14')
            connection.sendall(b'\x14' + data)
            print("Image sent from daemon.")
            file.close()
        else:  
            #send no image found message
            connection.send("No image found on daemon.".encode("utf-8"))

    # print images 
    def print_images(self):
        # print all key from self.images
        c = 0 # counter
        for img_hash in self.images:
            print("Image " + "[" + str(c) + "]")
            print("-- Image Name: " + self.images[img_hash])
            print("-- Hash Code: " + img_hash)
            print("\n")
            c += 1