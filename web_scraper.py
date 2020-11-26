import argparse, requests, threading, socket
from bs4 import BeautifulSoup
HOST = "127.0.0.1"
PORT = 5555
MAX_BYTES = 2048




class Client:
    
    def __init__(self,host,port):
        self.host=host
        self.port=port
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def start(self,link):
        self.sock.connect((self.host,self.port))
        encoded_link = link.encode()
        self.sock.send(encoded_link)
        image_c, leaf = (self.sock.recv(MAX_BYTES)).decode().split()
        print(f"Number of images: {image_c} Number of leaf paragraphs: {leaf}")
        self.sock.close()



class Server:
    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def process(self,sc,sockname):
        link = sc.recv(MAX_BYTES).decode()
        page = requests.get(link)
        
        print(f"[+] Scraping  {link} started ....")
        soupp = BeautifulSoup(page.text,"html.parser")

        image_c = self.image(soupp)
        p_count = self.p_leafs(soupp)

        msg = f"{image_c} {p_count}"

        sc.send(msg.encode())

        print("\n[+] The process finished..")

    def image(self,soupp):
        c = len(soupp.find_all("img"))
        return c

    def p_leafs(self, soupp):
        count = 0
        p_s = soupp.find_all('p')
        for p in p_s:
            if not p.find_all("p"):
                count += 1
        return count


    def start(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen()

        print("[+] The server listens at:", self.sock.getsockname())

        while True:
            sc, sockname = self.sock.accept()
            print('\n[+] The connection is received from', sockname)
            thread = threading.Thread(target=self.process, args=(sc,sockname))
            thread.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Web Scraper")
    choices = {"server": Server, "client": Client}
    parser.add_argument('role', choices = choices, help = "server or client")
    parser.add_argument("-p",metavar="PAGE", type=str, help="Web URL")
    args = parser.parse_args()

    Class = choices[args.role]
    
    if args.role == "client":
        cl_obj = Class(HOST,PORT)
        cl_obj.start(args.p if "http://" in args.p or "https://" in args.p else f"https://{args.p}")
    
    elif args.role == "server":
         s_obj = Class(HOST,PORT)
         s_obj.start()

