import json
from PIL import ImageTk
from subprocess import CREATE_NO_WINDOW
import math
import time
import tkinter
import tkinter.messagebox
import tkinter.scrolledtext as scrolledtext
import customtkinter
import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from googleapiclient.discovery import build


my_api_key = "YOUR_API_KEY" #The API_KEY you acquired
my_cse_id = "YOUR_SEARCH_ENGINE_ID" #The search-engine-ID you created

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']


conn = sqlite3.connect('computer_data.db')
cursor = conn.cursor()


customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class RightClicker:
    def __init__(self, e):
        commands = ["Cut","Copy","Paste"]
        menu = tk.Menu(None, tearoff=0, takefocus=0)

        for txt in commands:
            menu.add_command(label=txt, command=lambda e=e,txt=txt:self.click_command(e,txt))

        menu.tk_popup(e.x_root + 40, e.y_root + 10, entry="0")

    def click_command(self, e, cmd):
        e.widget.event_generate(f'<<{cmd}>>')


class App(customtkinter.CTk):

    WIDTH = 1280
    HEIGHT = 800

    def __init__(self):
        super().__init__()

        self.title("ARNS | PartHunter")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # ============ frame_left ============

        # configure grid layout (1x11)
        self.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(5, weight=1)  # empty row as spacing
        self.frame_left.grid_rowconfigure(8, minsize=20)    # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="PartHunter",
                                              text_font=("Roboto Medium", 17))  # font name and size in px
        self.label_1.grid(row=2, column=0, pady=10, padx=10)


        def popup(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)  # Pop the menu up in the given coordinates
            finally:
                menu.grab_release()  # Release it once an option is selected

        def paste():
            clipboard = self.clipboard_get()  # Get the copied item from system clipboard
            self.entry.insert('end', clipboard)  # Insert the item into the entry widget

        def copy():
            inp = self.entry.get()  # Get the text inside entry widget
            self.clipboard_clear()  # Clear the tkinter clipboard
            self.clipboard_append(inp)  # Append to system clipboard


        self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                            width=120,
                                            placeholder_text="Please select a brand",text_font=("Arial", 17))
        self.entry.grid(row=8, column=0, columnspan=2, pady=20, padx=20, sticky="we")
        self.entry.bind('<Button-3>',popup)


        menu = tkinter.Menu(self, tearoff=0)  # Create a menu
        menu.add_command(label='Copy', command=copy)  # Create labels and commands
        menu.add_command(label='Paste', command=paste)


        self.button_1 = customtkinter.CTkOptionMenu(master=self.frame_left,values=[],
                                                     command=self.google_search_PN,text_font=("Arial", 14))
        self.button_1.grid(row=3, column=0, pady=10, padx=20)
        self.button_1.set('Google Search P/N')

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text=" Google Search S/N ",text_font=("Arial", 16),
                                                command=self.google_search_SN)
        self.button_2.grid(row=4, column=0, pady=30, padx=20)

        # self.button_1 = customtkinter.CTkOptionMenu(master=self.frame_left,values=[],
        #                                              command=lambda : self.google_search_SN(),text_font=("Arial", 14))
        # self.button_1.grid(row=4, column=0, pady=10, padx=20)
        # self.button_1.set('Google Search P/N')

        self.bg_image = ImageTk.PhotoImage(file='black background.png')

        self.image_label = tkinter.Label(master=self.frame_left, image=self.bg_image,bg='#2A2D2E')
        self.image_label.grid(row=1, column=0)


        # self.button_2 = customtkinter.CTkButton(master=self.frame_left,
        #                                         text="Google Search S/N",
        #                                         command=lambda : self.google_search_SN(P_N))
        # self.button_2.grid(row=4, column=0, pady=10, padx=20)

        self.label_mode = customtkinter.CTkLabel(master=self.frame_left, text="Appearance Mode:",text_font=("Arial", 17))
        self.label_mode.grid(row=9, column=0, pady=0, padx=20, sticky="w")

        self.optionmenu_1 = customtkinter.CTkOptionMenu(master=self.frame_left,
                                                        values=["Light", "Dark", "System"],text_font=("Arial", 17),
                                                        command=self.change_appearance_mode)
        self.optionmenu_1.grid(row=10, column=0, pady=10, padx=20, sticky="w")

        # ============ frame_right ============

        # configure grid layout (3x7)
        self.frame_right.rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_right.rowconfigure(7, weight=10)
        self.frame_right.columnconfigure((0, 1), weight=1)
        self.frame_right.columnconfigure(2, weight=0)

        self.frame_info = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_info.grid(row=0, column=0, columnspan=2, rowspan=4, pady=20, padx=20, sticky="nsew")

        # ============ frame_info ============

        # configure grid layout (1x1)
        self.frame_info.rowconfigure(0, weight=1)
        self.frame_info.columnconfigure(0, weight=1)
        # self.label_info_1 = customtkinter.CTkLabel(master=self.frame_info,
        #                                            text="SKU: OBD-D234\n" +
        #                                                 "User Price: 345ILS\n" +
        #                                                 "Dealer Price: 145ILS\n" +
        #                                                 "4 searches from google" ,
        #                                            height=250,
        #                                            corner_radius=6,  # <- custom corner radius
        #                                            fg_color=("white", "gray38"),  # <- custom tuple-color
        #                                            justify=tkinter.LEFT)
        self.label_info_1 = scrolledtext.ScrolledText(master=self.frame_info,font=("gray38", 15))
        self.label_info_1.tag_configure("welcome_message", font=("Times New Roman", 20, 'bold'))
        self.label_info_1.tag_configure("welcome_message_underline", font=("Times New Roman", 20, 'bold','underline'))

        # self.label_info_1.insert("1.0", "\t\t   Welcome to ARNS Part Hunter!",'welcome_message_underline')
        # self.label_info_1.insert(tkinter.END, "\n\n\t\t  To begin please use the search field.",'welcome_message')
        self.label_info_1.tag_configure("title", font=("Times New Roman", 20, 'bold'))
        # self.label_info_1.tag_configure("monospaces", font=("Lucida", 12))
        self.label_info_1.tag_configure("normal", font=("Arial", 15))
        self.label_info_1.tag_configure("bold_normal", font=("Arial", 15,'bold'))
        self.label_info_1.tag_configure("bold_normal_2", font=("Arial", 15,'bold', 'underline'))
        self.label_info_1.tag_configure("normal_fits_bold", font=("Arial", 15,'bold'))
        self.label_info_1.configure(state='disabled')
        self.label_info_1.grid(column=0, row=0, sticky="nwe", padx=15, pady=15)

        self.progressbar = customtkinter.CTkProgressBar(master=self.frame_info)
        self.progressbar.grid(row=1, column=0, sticky="ew", padx=15, pady=15)

        self.progress_number = customtkinter.CTkLabel(master=self.frame_info, text='0% Completed', text_font=("Arial", 15))
        self.progress_number.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        # ============ frame_right ============

        self.radio_var = tkinter.StringVar()

        self.label_radio_group = customtkinter.CTkLabel(master=self.frame_right, text="Choose an Item:",text_font=("Arial", 17, 'bold'))
        self.label_radio_group.grid(row=0, column=2, columnspan=1, pady=20, padx=10, sticky="")

        self.radio_button_1 = customtkinter.CTkRadioButton(master=self.frame_right,
                                                           variable=self.radio_var,
                                                           value="Battery",text="Battery",text_font=("Arial", 17))
        self.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")

        self.radio_button_2 = customtkinter.CTkRadioButton(master=self.frame_right,
                                                           variable=self.radio_var,
                                                           value="Adapter",text="Adapter",text_font=("Arial", 17))
        self.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")

        self.radio_button_3 = customtkinter.CTkRadioButton(master=self.frame_right,
                                                           variable=self.radio_var,
                                                           value="Screen", text="Screen",text_font=("Arial", 17))
        self.radio_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")



        # self.slider_2 = customtkinter.CTkSlider(master=self.frame_right,
        #                                         command=self.progressbar.set)
        # self.slider_2.grid(row=5, column=0, columnspan=2, pady=10, padx=20, sticky="we")


        self.combobox_1 = customtkinter.CTkOptionMenu(master=self.frame_right,
                                                    values=["HP", "Lenovo", "Asus", "Dell"], command=self.change,text_font=("Arial", 17))
        self.combobox_1.grid(row=6, column=2, columnspan=1, pady=10, padx=20, sticky="we")
        # self.combobox_1.configure(state = "readonly")

        # self.combobox_1.c
        # self.combobox_1.bind("<<ComboboxSelected>>", self.change)


        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Search",text_font=("Arial", 17),
                                                border_width=2,  # <- custom border_width
                                                fg_color=None,  # <- no fg_color
                                                command=lambda :self.button_event_search(event=None))
        self.button_5.grid(row=8, column=2, columnspan=1, pady=20, padx=20, sticky="we")
        self.bind('<Return>', self.button_event_search)
        # set default values
        self.optionmenu_1.set("Dark")
        self.combobox_1.set("Brand")
        self.radio_button_1.select()
        self.progressbar.set(0.01)
        self.iconbitmap('LOGO-Lonkedin.ico')

    # def button_event(self):
    #     print("Button pressed")

    def change(self, event):
        if self.combobox_1.get() == 'HP':
            self.entry.delete(0, tkinter.END)
            self.entry.configure(placeholder_text='Serial Number')
            self.focus()

        elif self.combobox_1.get() == 'Lenovo':
            self.entry.delete(0, tkinter.END)
            self.entry.configure(placeholder_text='Serial Number')
            self.focus()

        elif self.combobox_1.get() == 'Asus':
            self.entry.delete(0, tkinter.END)
            self.entry.configure(placeholder_text='Product Name')
            self.focus()

        elif self.combobox_1.get() == 'Dell':
            self.entry.delete(0, tkinter.END)
            self.entry.configure(placeholder_text='Service Tag')
            self.focus()

        # print('haha')

    def google_search_PN(self, event):

        S_N = self.button_1.get()
        chrome_options = Options()
        chrome_options.add_experimental_option("detach",True)
        # chrome_options.add_argument("--headless")
        if S_N == '':
            tkinter.messagebox.showinfo('Error','Please input a serial number first')
            return
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(f"https://www.google.com/search?q={S_N}")
        self.button_1.set('Google Search P/N')


    def google_search_SN(self):
        S_N = self.entry.get().strip()
        chrome_options = Options()
        chrome_options.add_experimental_option("detach",True)
        # chrome_options.add_argument("--headless")
        if S_N == '':
            tkinter.messagebox.showinfo('Error','Please input a serial number first')
            return
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(f"https://www.google.com/search?q={S_N}")


    def button_event_search(self,event):
        brand = self.combobox_1.get()
        part = self.radio_var.get().strip()
        global SN
        SN = self.entry.get().strip()
        if SN == '':
            tkinter.messagebox.showinfo('Error','Please input a serial number first')
            return

        self.progress_number.configure(text='20% Completed')
        self.progressbar.set(0)
        time.sleep(1)
        self.update()
        print('heh')
        self.progress_number.configure(text='50% Completed')
        self.progressbar.set(0.5)
        print(part)
        time.sleep(1)
        print('heh')
        self.update()

        chrome_options = Options()
        chrome_options.headless = False
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # chrome_options.headless = True
        print(brand)
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        if brand == 'Asus':
            chrome_options.headless = True
            print('headless done')


        # elif brand != 'HP':
        #     chrome_options.headless = True

        try:
            # chrome_service = ChromeService('chromedriver')
            # chrome_service.creationflags = CREATE_NO_WINDOW
            # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            # driver.maximize_window()

            # soup = BeautifulSoup(url.content, 'lxml')
            # print(soup.prettify())
            if brand == 'HP':
                keywords = ['ac ', 'adapter', 'watt', 'battery', 'batt', 'ah']
                token = 'MjAyMzEzNy1wYXJ0c3VyZmVyOlBTVVJGQCNQUk9E'

                def get_parts(serial):
                    url = f"https://pro-psurf-app.glb.inc.hp.com/partsurferapi/Search/GenericSearch/{serial}/country/US/usertype/EXT"

                    headers = {
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Authorization': f'Basic {token}',
                        'Connection': 'keep-alive',
                        'Origin': 'https://partsurfer.hp.com',
                        'Referer': 'https://partsurfer.hp.com/',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-site',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"macOS"'
                    }
                    result = []
                    response = requests.request("GET", url, headers=headers)
                    if response.status_code == 200:
                        res = json.loads(response.text)
                        if 'SerialNumberBOM' in res['Body']:
                            body = res['Body']
                            result = check_match(body)
                        elif 'SNRProductLists' in res['Body']:
                            # this is multi product
                            products = res['Body']['SNRProductLists']
                            for product in products:
                                product_id = product['product_Id']
                                if '#' in product_id:
                                    product_id = product_id.split('#')[0]
                                url = f"https://pro-psurf-app.glb.inc.hp.com/partsurferapi/SerialNumber/GetSerialNumber/{serial}/ProductNumber/{product_id}/country/US/usertype/EXT"
                                response = requests.request("GET", url, headers=headers)
                                if response.status_code == 200:
                                    res = json.loads(response.text)
                                    body = res['Body']
                                    result.extend(check_match(body))
                                else:
                                    print(f'Error response, {response}')
                        else:
                            print('No matches')
                    else:
                        print(f'Error response, {response}')

                    return result

                def check_match(body):
                    result = []
                    if 'SerialNumberBOM' in body:
                        product_name = body['SerialNumberBOM']['wwsnrsinput']['user_name']
                        parts = body['SerialNumberBOM']['unit_configuration']
                        for part in parts:
                            part_description = part['part_description']
                            for keyword in keywords:
                                if keyword in part_description.lower():
                                    part_number = part['part_number']
                                    result.append({'part_number': part_number, 'part_description': part_description,
                                                   'product_name': product_name})
                                    break

                    if 'ProductBOM' in body:
                        parts = body['ProductBOM']
                        for part in parts:
                            part_description = part['EnhancedDescription']
                            for keyword in keywords:
                                if keyword in part_description.lower():
                                    part_number = part['PartNumber']
                                    result.append({'part_number': part_number, 'part_description': part_description,
                                                   'product_name': product_name})
                                    break
                    return result

                # serv = ChromeService(ChromeDriverManager().install())
                # serv.creationflags = CREATE_NO_WINDOW
                #
                # driver = webdriver.Chrome(service=serv, options=chrome_options)
                #
                # driver.minimize_window()
                #
                # driver.get(f'https://partsurfer.hp.com/partsurfer?searchtext={SN}')
                # soup = BeautifulSoup(driver.page_source, 'lxml')
                # driver.quit()
                # print(soup.prettify())

                rows_data = []

                try:
                    # if 'Multiple Products associated for above Serial Number' in driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/div[1]').text:
                    #     tkinter.messagebox.showinfo("Select", "Please select a laptop from here. Will wait for 10 seconds now.")
                    #     print('waiting 15 seconds now')
                    #     time.sleep(15)
                    # # driver.minimize_window()
                    # lenOfPage = driver.execute_script(
                    #     "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                    # match = False
                    # while (match == False):
                    #     lastCount = lenOfPage
                    #     time.sleep(2)
                    #     lenOfPage = driver.execute_script(
                    #         "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                    #     if lastCount == lenOfPage:
                    #         match = True
                    #
                    #
                    # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "react-tabs")))
                    # time.sleep(3)
                    #
                    # print('Found')
                    #
                    # table_tempalte = driver.find_element(by=By.CSS_SELECTOR, value='div[class="react-bootstrap-table"]')
                    # tbody = table_tempalte.find_element(by=By.TAG_NAME, value='tbody')
                    #
                    # for rows in tbody.find_elements(by=By.TAG_NAME, value='tr'):
                    #     inner_rows = rows.find_elements(by=By.TAG_NAME, value='td')
                    #     parent_part_number = inner_rows[0].text.strip()
                    #     assembly_part_number = inner_rows[1].text.strip()
                    #     part_description = inner_rows[2].text.strip()
                    #     quantity = inner_rows[3].text.strip()
                    #
                    #     # print(parent_part_number)
                    #     # print(assembly_part_number)
                    #     # print(part_description)
                    #     # print(quantity)
                    #
                    #     rows_data.append([parent_part_number,assembly_part_number,part_description,quantity])

                        # print(inner_rows.text)
                        # print('')
                    hp_results = get_parts(SN)

                    global P_N
                    P_N = None
                    if part == 'Battery':

                        counter = 0

                        for battery in hp_results:
                            if 'BATT' in battery['part_description']:
                            # if 'Ah' in battery[2] or 'AH' in battery[2] or 'ah' in battery[2] or 'aH' in battery[2] or 'BATT' in battery[2]:

                                print('finally')
                                P_N = battery['part_number']
                                print(P_N)

                            elif 'Ah' in battery['part_description']:

                                if battery['part_description'][battery['part_description'].index('Ah')-1].isdigit():
                                    print('finally')
                                    P_N = battery['part_number']
                                    print(P_N)

                            elif 'AH' in battery['part_description']:

                                if battery['part_description'][battery['part_description'].index('AH')-1].isdigit():
                                    print('finally')
                                    P_N = battery['part_number']
                                    print(P_N)

                            elif 'aH' in battery['part_description']:

                                if battery['part_description'][battery['part_description'].index('aH')-1].isdigit() :
                                    print('finally')
                                    P_N = battery['part_number']
                                    print(P_N)

                            elif 'ah' in battery['part_description']:

                                if battery['part_description'][battery['part_description'].index('ah')-1].isdigit():
                                    print('finally')
                                    P_N = battery['part_number']
                                    print(P_N)

                        if P_N != None:
                            cursor.execute(f"""Select * from {brand} where [P/N] NOT NULL""")

                            data = cursor.fetchall()

                            part_numbers_in_database = []
                            # print(data)

                            results_data = ''
                            try:
                                results = google_search(f'{P_N}', my_api_key, my_cse_id, num=4)
                                count = 1
                                for result in results:
                                    print(result['title'])
                                    print(result['snippet'])
                                    results_data += f"{count}. {result['title']}\n{result['snippet']}\n---------------------------------------------------------------------------------------------------------------------------\n\n"
                                    count+=1
                            except:
                                results_data = 'Error occurred in Google Search.'
                            print(results_data)

                            self.label_info_1.configure(state='normal')
                            self.label_info_1.delete("1.0", tkinter.END)
                            for i in data:
                                # print(i)
                                if P_N in i[6]:
                                    self.label_info_1.insert("1.0", f"Found in inventory B\n", 'bold_normal')
                                    self.label_info_1.insert(tkinter.END,
                                                             f'Part Number: {P_N}\n', 'bold_normal')
                                    self.label_info_1.insert(tkinter.END, f"SKU: ", 'bold_normal')
                                    self.label_info_1.insert(tkinter.END,f"{i[0]}\n")
                                    self.label_info_1.insert(tkinter.END,f"User Price:", 'bold_normal')
                                    self.label_info_1.insert(tkinter.END,f"{i[4]} ILS\n")
                                    self.label_info_1.insert(tkinter.END,f"Dealer Price:", 'bold_normal')
                                    self.label_info_1.insert(tkinter.END,f"{i[5]} ILS\n\n")
                                    self.label_info_1.insert(tkinter.END,"Useful information:\n\n", 'bold_normal_2')
                                    self.label_info_1.insert(tkinter.END,f"{results_data}")
                                    self.label_info_1.configure(state='disabled')
                                    counter = 1

                            if counter == 0:
                                print('Part Number not in Database')
                                self.label_info_1.insert("1.0",
                                                         f'Part Number {P_N} not in Database\n\n','title')
                                self.label_info_1.insert(tkinter.END,
                                                         f'Useful information:\n\n','bold_normal_2')
                                self.label_info_1.insert(tkinter.END,
                                                         f'{results_data}')
                                self.label_info_1.configure(state='disabled')

                    elif part == 'Adapter':
                        counter = 0
                        for adapter in hp_results:
                            # print(adapter)
                            if 'Adapter' in adapter['part_description'] or 'adapter' in adapter['part_description'] or 'ADAPTER' in adapter['part_description'] or 'ADPTR' in adapter['part_description']:
                                print('finally')
                                P_N = adapter['part_number']
                                print(adapter['part_number'])
                        if P_N != None:
                            cursor.execute(f"""Select * from {brand} where [P/N] NOT NULL""")

                            data = cursor.fetchall()

                            part_numbers_in_database = []
                            # print(data)

                            results_data = ''
                            try:
                                results = google_search(f'{P_N}', my_api_key, my_cse_id, num=4)
                                count = 1
                                for result in results:
                                    print(result['title'])
                                    print(result['snippet'])
                                    results_data += f"{count}. {result['title']}\n{result['snippet']}\n---------------------------------------------------------------------------------------------------------------------------\n\n"
                                    count+=1
                            except:
                                results_data = "Error occurred in Google Search"
                            print(results_data)
                            self.label_info_1.configure(state='normal')

                            self.label_info_1.configure(state='normal')
                            self.label_info_1.delete("1.0", tkinter.END)
                            for i in data:
                                # print(i)
                                if P_N in i[6]:
                                    self.label_info_1.insert("1.0", f"Found in inventory A\n", 'bold_normal')
                                    self.label_info_1.insert(tkinter.END,
                                                             f'Part Number: {P_N}\n', 'bold_normal')
                                    self.label_info_1.insert(tkinter.END, f"SKU: ", 'bold_normal')
                                    self.label_info_1.insert(tkinter.END, f"{i[0]}\n")
                                    self.label_info_1.insert(tkinter.END, f"User Price:", 'bold_normal')
                                    self.label_info_1.insert(tkinter.END, f"{i[4]} ILS\n")
                                    self.label_info_1.insert(tkinter.END, f"Dealer Price:", 'bold_normal')
                                    self.label_info_1.insert(tkinter.END, f"{i[5]} ILS\n\n")
                                    self.label_info_1.insert(tkinter.END, "Useful information:\n\n", 'bold_normal_2')
                                    self.label_info_1.insert(tkinter.END, f"{results_data}")
                                    self.label_info_1.configure(state='disabled')
                                    counter = 1

                            if counter == 0:
                                print('Part Number not in Database')
                                self.label_info_1.insert("1.0",
                                                         f'Part Number {P_N} not in Database\n\n', 'title')
                                self.label_info_1.insert(tkinter.END,
                                                         f'Useful information:\n\n', 'bold_normal_2')
                                self.label_info_1.insert(tkinter.END,
                                                         f'{results_data}')
                                self.label_info_1.configure(state='disabled')

                    self.progress_number.configure(text='100% Completed')
                    self.progressbar.set(1)


                except Exception as e:
                    print(e)
                    self.label_info_1.configure(state='normal')
                    self.label_info_1.delete("1.0", tkinter.END)
                    self.label_info_1.insert("1.0",
                                             f'Wrong serial number or Website is not accessible right now.', 'normal_fits_bold')
                    print('Wrong Serial Number')
                    message = e.__class__.__name__
                    print(message)
                    self.progressbar.set(0)
                    self.progress_number.configure(text='0% Completed')

            elif brand == 'Dell':
                # try:
                #     rows_data = []
                #     try:
                #         driver.get(f'https://www.dell.com/support/home/en-pk/product-support/servicetag/{SN}/overview')
                #     except:
                #         driver.get('https://www.dell.com/support/home/en-pk?~ck=mn')
                #         time.sleep(10)
                #         search = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'inpEntrySelection')))
                #         # time.sleep(10)
                #         search.send_keys(SN)
                #         # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "popover fade bs-popover-top show"))).click()
                #         WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'btn-entry-select'))).click()
                #         # driver.find_element(by=By.ID, value='btn-entry-select').click()
                #         # time.sleep(3)
                #         print('first clicked')
                #         # WebDriverWait(driver, 32).until(EC.element_to_be_clickable((By.ID, 'btn-entry-select')))
                #         # search.send_keys('4CG55H2')
                #         time.sleep(35)
                #         WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'btn-entry-select'))).click()
                #         print('hehe')
                #
                #     time.sleep(4)
                #     WebDriverWait(driver, 35).until(EC.element_to_be_clickable((By.ID, 'quicklink-sysconfig'))).click()
                #     WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'systab_originalconfig')))
                #     panel_template = driver.find_element(by=By.CSS_SELECTOR, value='div[id="systab_originalconfig"]')
                #     # table_tempalte = driver.find_element(by=By.CSS_SELECTOR, value='div[class="react-bootstrap-table"]')
                #     try:
                #         WebDriverWait(driver, 13).until(EC.element_to_be_clickable((By.ID, 'expandAllLink'))).click()
                #         print('expanded')
                #     except:
                #         pass
                #     # print(panel_template.text)
                #     print('now')
                #     for row in panel_template.find_elements(by=By.CSS_SELECTOR, value='div[class="card mb-4"]'):
                #         table = row.find_element(by=By.CSS_SELECTOR, value='#OriginalConfigContent-table > tbody')
                #         # print(table.text)
                #         for rows in table.find_elements(by=By.TAG_NAME, value='tr'):
                #             # print(rows.text)
                #             inner_rows = rows.find_elements(by=By.TAG_NAME, value='td')
                #             part_number = inner_rows[0].text.strip()
                #             description = inner_rows[1].text.strip()
                #             quantity = inner_rows[2].text.strip()
                #
                #             rows_data.append([part_number, description, quantity])

                    # global P_N
                def dell_hashed_id():
                    cookies = {
                        'LithiumCookiesAccepted': '0',
                        '_cls_v': 'c801e774-f970-45e6-9ebb-82dbc95a2567',
                        '_cls_s': '7ea620a2-78c5-496f-ae8c-d013873ce59e:0',
                        'DellCEMSession': 'AD5D0942D48A330E86E822637A2CFB2D',
                        'eSupId': 'SID=aecf3c42-2f6d-44a7-b73d-382e0937c114&ld=20230405',
                        'cidlid': '%3A%3A',
                        's_cc': 'true',
                        '__privaci_cookie_consent_uuid': 'ec6a03a3-d321-44ad-8c67-406c130aa194:28',
                        '__privaci_cookie_consent_generated': 'ec6a03a3-d321-44ad-8c67-406c130aa194:28',
                        'dais-aspNsId': 'if2r1hk1crnudnkqookzavwg',
                        'dais-c': 'dUMQh/Jt5U9sjeFNLVj6nsKWenMh9DeAZQhdlgafh/9GUe0C0lH4xuk5CQdelRMI',
                        'rumCki': 'false',
                        'akGD': '"country":"PK", "region":""',
                        'dais-a': '1G9gtHP_vwUAygcOTWOwmhYO9ufXo4AZSE0b7YgYSNpm1vcRjOYl7rLtBlEOUOvEMK2TTKUZdGUl_4P859ZYpDnG5cM1',
                        'sessionTime': '2022%2C9%2C27%2C5%2C36%2C41%2C873',
                        's_vnum': '1698367001875%26vn%3D1',
                        'LiSESSIONID': '33D8094FFB22A311CDEF7926D4236290',
                        'VISITOR_BEACON': '~2LLAIXjxL055E0l7P~tpTr_yOAzsfffK3_M4drvtT2Of4tuvykT9ODWwxLLM5P8Upv50PF9IYrv4JLJADshwUCT5p7XifZPZ_uUKd1Vg..',
                        'LithiumVisitor': '~2NyUGeFAwOTfWd8h9~f73hS5mc9X8uZA10ZLxfcOFiGMlJ4HjbPI6Ne1BzFPDmP5-3a1-f_TaURyrdDrp6yjPRmUHXQ8JHh7uNI-zDEQ..',
                        'BRAND_MESSENGER_pageVisitsSinceLastMessage': '%5B%7B%22url%22%3A%22https%3A%2F%2Fwww.dell.com%2Fcommunity%2FLaptops-General-Read-Only%2FKeyboard-backlight-can-it-be-always-on%2Ftd-p%2F5086970%22%2C%22title%22%3A%22Keyboard%20backlight%20-%20can%20it%20be%20always%20on%3F%20-%20Dell%20Community%22%2C%22timestamp%22%3A1646625568460%7D%2C%7B%22url%22%3A%22https%3A%2F%2Fwww.dell.com%2Fcommunity%2FCustomer-Care%2FAccess-Denied-on-all-Dell-website-links-in-My-Products-and%2Ftd-p%2F8032442%22%2C%22title%22%3A%22Access%20Denied%20on%20all%20Dell%20website%20links%20in%20My%20Products%20and%20Servi...%22%2C%22timestamp%22%3A1666833218703%7D%5D',
                        'inputArticleNo': '000146587',
                        'v36': '8d69j12',
                        's_ips': '731',
                        'AKA_A2': 'A',
                        'bm_sz': 'CE4C6A5BE3828C309D5082A00ECFD602~YAAQTp4QApwuBTyEAQAAu/gFWRHEen3pdVvGCm+R70KgEeo9NxOCZe3bcUcv78fHRpnOmn5nfsr4vZujhJHSfi4bFWzwgkiGoVj5oc5zLmxBXmYMgwJHO0Soji6v7r80Fbch+YukUrkM2nNK/r1SiF9trXyDbBPmuIq0Kn7vBXJ2J+8mj9aZfnTSRTrfXwcsS4xcTTYkF5MTVRwLd20W3QnLc7QAaW0cbAUrP6sEqWRkh1bG8sFl3EiPvuIxJREo/cbD5MrFWL0TGX9LY8So92PW9U1jR3GphVk2ZskLoR3u~3486531~3556165',
                        'AMCV_4DD80861515CAB990A490D45%40AdobeOrg': '1585540135%7CMCIDTS%7C19305%7CMCMID%7C21407894613880770838451933319749296246%7CMCAID%7CNONE%7CvVersion%7C4.4.0',
                        'VOCAAS_SESSION_ID': 'C61479F946805722529CD767BE193F81',
                        'VOCAAS_STICKY_SESSION': 'C61479F946805722529CD767BE193F81',
                        's_vnc365': '1699476884178%26vn%3D22',
                        's_ivc': 'true',
                        '__privaci_cookie_no_action': 'no-action-consent',
                        'lwp': 'c=il&l=en&cs=ilbsdt1&s=bsd',
                        's_sq': '%5B%5BB%5D%5D',
                        'OLRProduct': 'OLRProduct=8D69J12|',
                        'bm_mi': '08740948E830EF433DBFA0F57088CF86~YAAQTp4QAvI4BTyEAQAAa4gIWRF+ExGzo535RiGIzcZTJ5KDtXnsaGxhOTPqKRdzisU1y/aBnbe+pWHvHGWn/q/vTrPi3y03RrwBkz9nq49i/eFnOlJ0OhqLJ8ntVSG3qwJOkTrkdB/F5MIKBOIzNZYlAwd9RielZEB9GsZ7hpvTkfcJFeWrXbdiwt67+vtgb+uQnszh4tPo4EGI+9/8o7YwoUPK4BgvK/UsdFztF5I3JiVnUtl1/ahw+zsD1C6AiuLxc1yzMepox1fiBZOyIGvsjk/JYY32qDr/mhKcchyqM2L6KoolLElZjxpjGr+8LTfpwBsN8E8l+Vf7IF8TCSNT+gnPIJCGT2JKkzjNl+l6lyVFYO2LBsrQGJ2VnQHGKeZQiR8cgufXiZVuy+glyONLhWhpC+IreuGIDEJBCwBoovnnCu0=~1',
                        'bm_sv': '66E1BB2CF0491E78C68756EF6C253A32~YAAQTp4QAig5BTyEAQAAXZIIWRHIY2n7RxvrqLIcOT+UgtY2nhp/Ami9n5BsU6D13vb5fegbNfttyKZbWXmh1etjacERWmeW8KQ2D/hoan7CGFor0FwSdFqs/QPDk66s5dq1WTBxy2/8aJ1qJrr9QqbUrcRS2XcCdPkKSUIBM1NczEXqIypYoaZZca+DclIaM/Gq3eBBnr1cdSwbJev/WQoh8mLU21WRFGF0QpC05GvV/IZdM0jiyrGxR6AzzLc=~1',
                        'ak_bmsc': '3473E63F774E3545D4F219AA4C0AC308~000000000000000000000000000000~YAAQTp4QAg8+BTyEAQAAuDsKWRH4DqQCSBffTCIOz04ieGto4t616zAX4Tw69QqQlk6nNZoytK1gv5qcgOVocd9cQY1EFOa7eaadSsMNrNGR2d5aXWnQhDDqukHgd44m7AjFSosJxmWMER7y32qhDb8tpU/k98g04LufZeDH1lH0yL1EHiwK+mPvsiUdv9Q6y2YQuPbfWI4g/vs04fhopHg5VeCdONOhOfdPAfZfbyvgTkISeP9/LhLTqTerldpx7puPj/2bK2R6RoLlsqdmGWCZy2E+A7KXUJqTm5hc6i/SJlZ++yBl7YBcA9un6MKtmkSryPYLFG99b/AC+LDjESH6qFw4KN5rod55JtjN8GFd1PpPz6P9ZTkUki/Xrahu1p2EBLxwJxl+rHrvFuThI6O8hxTDzrhlSf+Pz167EriiqhPhAUBWCn2m9sWO5iEWiP9UbChzn2Yt/ES92V3NYmDaP2Y1nDK+h6bEP8PALJOCc1UOWwmLUP33loD8F+hQbmNpKD2DBSGCOnB2dO0eE+sWzenZ1RJn',
                        's_c49': 'c%3Dil%26l%3Den%26s%3Dbsd%26cs%3Dilbsdt1%26servicetag%3D8d69j12',
                        'gpv_pn': 'il%7Cen%7Cbsd%7Cilbsdt1%7Cesupport-home%7Chome%7Cindex',
                        's_depth': '3',
                        '_abck': '84672596817D15E59528F27060C40DEF~0~YAAQTp4QAkM+BTyEAQAAwE0KWQj6tZYnjU7IB58SBD+feXLij5FBK8ISdq30UtJ6VXSNb/S4b9vKw0Z+hJM78pL5qYxe3KL5fHwYByiun8otPsX9NikFEfeHldZcsEnlOVyJcz3JJKQZZ9DcKj3OucNz6VoLs7S/PHijlLBtRFWvvtQMRJRta+tCEGPtHsiRQ+PUnllExILkVACb0SP8DuIafE/irY+GBy8BUvQV9IFC8Ty4cIsJEC/T198K0kQBP9tmSpbhcgEbJqqMuvehf33JPNkhJyZqmE8uPU27xvIBSLE3+Nn8YK1eTJmxFRdTHq54Mvc7m8v7syJcg104oWFIJiqrLTF7m5gxVCVhHCGh2UbtUpkiJgdMTsFCKGY6mcmk0nf8fNV3JN4VpCmYBnwbeSs20w==~-1~-1~-1',
                        's_tp': '4354',
                        's_ppv': 'il%257Cen%257Cbsd%257Cilbsdt1%257Cesupport-home%257Chome%257Cindex%2C17%2C17%2C731%2C1%2C5',
                        'akavpau_maintenance_vp': '1667942495~id=f2c705f978a7703968568d4d7d480b4b',
                    }

                    DELL_ENTITY = 'https://www.dell.com/support/search/en-il/entryselection/ValidateEntityJSON'
                    payload = {"Selection": SN, "appName": "mastheadSearch"}

                    headers = {
                        'authority': 'www.dell.com',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'accept-language': 'en-US,en;q=0.9,es;q=0.8',
                        'cache-control': 'max-age=0',
                        # Requests sorts cookies= alphabetically
                        'cookie': 'LithiumCookiesAccepted=0; _cls_v=c801e774-f970-45e6-9ebb-82dbc95a2567; _cls_s=7ea620a2-78c5-496f-ae8c-d013873ce59e:0; DellCEMSession=AD5D0942D48A330E86E822637A2CFB2D; eSupId=SID=aecf3c42-2f6d-44a7-b73d-382e0937c114&ld=20230405; cidlid=%3A%3A; s_cc=true; __privaci_cookie_consent_uuid=ec6a03a3-d321-44ad-8c67-406c130aa194:28; __privaci_cookie_consent_generated=ec6a03a3-d321-44ad-8c67-406c130aa194:28; dais-aspNsId=if2r1hk1crnudnkqookzavwg; dais-c=dUMQh/Jt5U9sjeFNLVj6nsKWenMh9DeAZQhdlgafh/9GUe0C0lH4xuk5CQdelRMI; rumCki=false; akGD="country":"PK", "region":""; dais-a=1G9gtHP_vwUAygcOTWOwmhYO9ufXo4AZSE0b7YgYSNpm1vcRjOYl7rLtBlEOUOvEMK2TTKUZdGUl_4P859ZYpDnG5cM1; sessionTime=2022%2C9%2C27%2C5%2C36%2C41%2C873; s_vnum=1698367001875%26vn%3D1; LiSESSIONID=33D8094FFB22A311CDEF7926D4236290; VISITOR_BEACON=~2LLAIXjxL055E0l7P~tpTr_yOAzsfffK3_M4drvtT2Of4tuvykT9ODWwxLLM5P8Upv50PF9IYrv4JLJADshwUCT5p7XifZPZ_uUKd1Vg..; LithiumVisitor=~2NyUGeFAwOTfWd8h9~f73hS5mc9X8uZA10ZLxfcOFiGMlJ4HjbPI6Ne1BzFPDmP5-3a1-f_TaURyrdDrp6yjPRmUHXQ8JHh7uNI-zDEQ..; BRAND_MESSENGER_pageVisitsSinceLastMessage=%5B%7B%22url%22%3A%22https%3A%2F%2Fwww.dell.com%2Fcommunity%2FLaptops-General-Read-Only%2FKeyboard-backlight-can-it-be-always-on%2Ftd-p%2F5086970%22%2C%22title%22%3A%22Keyboard%20backlight%20-%20can%20it%20be%20always%20on%3F%20-%20Dell%20Community%22%2C%22timestamp%22%3A1646625568460%7D%2C%7B%22url%22%3A%22https%3A%2F%2Fwww.dell.com%2Fcommunity%2FCustomer-Care%2FAccess-Denied-on-all-Dell-website-links-in-My-Products-and%2Ftd-p%2F8032442%22%2C%22title%22%3A%22Access%20Denied%20on%20all%20Dell%20website%20links%20in%20My%20Products%20and%20Servi...%22%2C%22timestamp%22%3A1666833218703%7D%5D; inputArticleNo=000146587; v36=8d69j12; s_ips=731; AKA_A2=A; bm_sz=CE4C6A5BE3828C309D5082A00ECFD602~YAAQTp4QApwuBTyEAQAAu/gFWRHEen3pdVvGCm+R70KgEeo9NxOCZe3bcUcv78fHRpnOmn5nfsr4vZujhJHSfi4bFWzwgkiGoVj5oc5zLmxBXmYMgwJHO0Soji6v7r80Fbch+YukUrkM2nNK/r1SiF9trXyDbBPmuIq0Kn7vBXJ2J+8mj9aZfnTSRTrfXwcsS4xcTTYkF5MTVRwLd20W3QnLc7QAaW0cbAUrP6sEqWRkh1bG8sFl3EiPvuIxJREo/cbD5MrFWL0TGX9LY8So92PW9U1jR3GphVk2ZskLoR3u~3486531~3556165; AMCV_4DD80861515CAB990A490D45%40AdobeOrg=1585540135%7CMCIDTS%7C19305%7CMCMID%7C21407894613880770838451933319749296246%7CMCAID%7CNONE%7CvVersion%7C4.4.0; VOCAAS_SESSION_ID=C61479F946805722529CD767BE193F81; VOCAAS_STICKY_SESSION=C61479F946805722529CD767BE193F81; s_vnc365=1699476884178%26vn%3D22; s_ivc=true; __privaci_cookie_no_action=no-action-consent; lwp=c=il&l=en&cs=ilbsdt1&s=bsd; s_sq=%5B%5BB%5D%5D; OLRProduct=OLRProduct=8D69J12|; bm_mi=08740948E830EF433DBFA0F57088CF86~YAAQTp4QAvI4BTyEAQAAa4gIWRF+ExGzo535RiGIzcZTJ5KDtXnsaGxhOTPqKRdzisU1y/aBnbe+pWHvHGWn/q/vTrPi3y03RrwBkz9nq49i/eFnOlJ0OhqLJ8ntVSG3qwJOkTrkdB/F5MIKBOIzNZYlAwd9RielZEB9GsZ7hpvTkfcJFeWrXbdiwt67+vtgb+uQnszh4tPo4EGI+9/8o7YwoUPK4BgvK/UsdFztF5I3JiVnUtl1/ahw+zsD1C6AiuLxc1yzMepox1fiBZOyIGvsjk/JYY32qDr/mhKcchyqM2L6KoolLElZjxpjGr+8LTfpwBsN8E8l+Vf7IF8TCSNT+gnPIJCGT2JKkzjNl+l6lyVFYO2LBsrQGJ2VnQHGKeZQiR8cgufXiZVuy+glyONLhWhpC+IreuGIDEJBCwBoovnnCu0=~1; bm_sv=66E1BB2CF0491E78C68756EF6C253A32~YAAQTp4QAig5BTyEAQAAXZIIWRHIY2n7RxvrqLIcOT+UgtY2nhp/Ami9n5BsU6D13vb5fegbNfttyKZbWXmh1etjacERWmeW8KQ2D/hoan7CGFor0FwSdFqs/QPDk66s5dq1WTBxy2/8aJ1qJrr9QqbUrcRS2XcCdPkKSUIBM1NczEXqIypYoaZZca+DclIaM/Gq3eBBnr1cdSwbJev/WQoh8mLU21WRFGF0QpC05GvV/IZdM0jiyrGxR6AzzLc=~1; ak_bmsc=3473E63F774E3545D4F219AA4C0AC308~000000000000000000000000000000~YAAQTp4QAg8+BTyEAQAAuDsKWRH4DqQCSBffTCIOz04ieGto4t616zAX4Tw69QqQlk6nNZoytK1gv5qcgOVocd9cQY1EFOa7eaadSsMNrNGR2d5aXWnQhDDqukHgd44m7AjFSosJxmWMER7y32qhDb8tpU/k98g04LufZeDH1lH0yL1EHiwK+mPvsiUdv9Q6y2YQuPbfWI4g/vs04fhopHg5VeCdONOhOfdPAfZfbyvgTkISeP9/LhLTqTerldpx7puPj/2bK2R6RoLlsqdmGWCZy2E+A7KXUJqTm5hc6i/SJlZ++yBl7YBcA9un6MKtmkSryPYLFG99b/AC+LDjESH6qFw4KN5rod55JtjN8GFd1PpPz6P9ZTkUki/Xrahu1p2EBLxwJxl+rHrvFuThI6O8hxTDzrhlSf+Pz167EriiqhPhAUBWCn2m9sWO5iEWiP9UbChzn2Yt/ES92V3NYmDaP2Y1nDK+h6bEP8PALJOCc1UOWwmLUP33loD8F+hQbmNpKD2DBSGCOnB2dO0eE+sWzenZ1RJn; s_c49=c%3Dil%26l%3Den%26s%3Dbsd%26cs%3Dilbsdt1%26servicetag%3D8d69j12; gpv_pn=il%7Cen%7Cbsd%7Cilbsdt1%7Cesupport-home%7Chome%7Cindex; s_depth=3; _abck=84672596817D15E59528F27060C40DEF~0~YAAQTp4QAkM+BTyEAQAAwE0KWQj6tZYnjU7IB58SBD+feXLij5FBK8ISdq30UtJ6VXSNb/S4b9vKw0Z+hJM78pL5qYxe3KL5fHwYByiun8otPsX9NikFEfeHldZcsEnlOVyJcz3JJKQZZ9DcKj3OucNz6VoLs7S/PHijlLBtRFWvvtQMRJRta+tCEGPtHsiRQ+PUnllExILkVACb0SP8DuIafE/irY+GBy8BUvQV9IFC8Ty4cIsJEC/T198K0kQBP9tmSpbhcgEbJqqMuvehf33JPNkhJyZqmE8uPU27xvIBSLE3+Nn8YK1eTJmxFRdTHq54Mvc7m8v7syJcg104oWFIJiqrLTF7m5gxVCVhHCGh2UbtUpkiJgdMTsFCKGY6mcmk0nf8fNV3JN4VpCmYBnwbeSs20w==~-1~-1~-1; s_tp=4354; s_ppv=il%257Cen%257Cbsd%257Cilbsdt1%257Cesupport-home%257Chome%257Cindex%2C17%2C17%2C731%2C1%2C5; akavpau_maintenance_vp=1667942495~id=f2c705f978a7703968568d4d7d480b4b',
                        'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'document',
                        'sec-fetch-mode': 'navigate',
                        'sec-fetch-site': 'none',
                        'sec-fetch-user': '?1',
                        'upgrade-insecure-requests': '1',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                    }

                    r = requests.post(DELL_ENTITY, headers=headers, json=payload, cookies=cookies)

                    r = requests.post(DELL_ENTITY, headers=headers, json=payload, cookies=cookies)

                    print(r)
                    dell_json = r.json()
                    # print(dell_json)
                    hashed_id = dell_json["LookupResults"][0]['TargetUrl'].split('/')[-2].split('-')[-1]

                    return hashed_id
                try:
                    hashed_id = dell_hashed_id()
                    print(hashed_id)
                    def dell_data(hashed_id):

                        DELL_BATTERY_OPTIONS = ['bty', 'btty', 'cell', 'whr', 'betty', 'battery', 'BTRY','Battery']

                        DELL_ADAPTER_OPTIONS = ['Adapter','ADPT']

                        url = f'https://www.dell.com/support/components/dashboard/en-il/Configuration/GetConfiguration?serviceTag={hashed_id}&showCurrentConfig=true&showOriginalConfig=True&_=1628927095967'

                        content = requests.get(url,
                                               headers={
                                                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
                                               },
                                               verify=False)

                        # data = content.text.replace('\n','')
                        data = content.content
                        # print(data)
                        soup = BeautifulSoup(data, 'html.parser')
                        rows_data = soup.find_all('table', id='OriginalConfigContent-table')

                        global P_N
                        P_N = None

                        self.label_info_1.configure(state='normal')
                        self.label_info_1.delete("1.0", tkinter.END)

                        found_counter = 0
                        new_PN_values = set()
                        for i in rows_data:
                            body = i.find('tbody')
                            trs = body.find_all('tr')
                            for j in trs:
                                temp_data = j.text.split('\n')
                                print(temp_data)
                                if part == 'Battery':
                                    counter = 0
                                    new_counter = 0
                                    if any(ext in temp_data[2] for ext in DELL_BATTERY_OPTIONS):
                                        new_counter+=1
                                        P_N = temp_data[1]
                                        new_PN_values.add(P_N)
                                        print('This is PN')
                                        cursor.execute(f"""Select * from {brand} where [P/N] NOT NULL""")

                                        data = cursor.fetchall()

                                        part_numbers_in_database = []
                                        # print(data)

                                        results_data = ''
                                        results = google_search(f'{P_N}', my_api_key, my_cse_id, num=4)
                                        count = 1
                                        for result in results:
                                            print(result['title'])
                                            print(result['snippet'])
                                            results_data += f"{count}. {result['title']}\n{result['snippet']}\n---------------------------------------------------------------------------------------------------------------------------\n\n"
                                            count += 1
                                        print(results_data)
                                        for i in data:
                                            # print(i)
                                            if P_N in i[6]:
                                                self.label_info_1.insert(tkinter.END, f"Found in inventory B\n", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END,
                                                                         f'Part Number: {P_N}\n', 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"SKU: ", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"{i[0]}\n")
                                                self.label_info_1.insert(tkinter.END, f"User Price:", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"{i[4]} ILS\n")
                                                self.label_info_1.insert(tkinter.END, f"Dealer Price:", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"{i[5]} ILS\n\n")
                                                self.label_info_1.insert(tkinter.END, "Useful information:\n\n",
                                                                         'bold_normal_2')
                                                self.label_info_1.insert(tkinter.END, f"{results_data}")
                                                counter = 1

                                                # new_PN_values.add(P_N)


                                        if counter == 0:
                                            print('Part Number not in Database')
                                            self.label_info_1.insert("1.0",
                                                                     f'Part Number {P_N} not in Database\n\n', 'title')
                                            self.label_info_1.insert(tkinter.END,
                                                                     f'Useful information:\n\n',
                                                                     'bold_normal_2')
                                            self.label_info_1.insert(tkinter.END,
                                                                     f'{results_data}')
                                        found_counter+=1

                                if part == 'Adapter':
                                    counter = 0
                                    if any(ext in temp_data[2] for ext in DELL_ADAPTER_OPTIONS):
                                        P_N = temp_data[1]
                                        cursor.execute(f"""Select * from {brand} where [P/N] NOT NULL""")

                                        data = cursor.fetchall()

                                        part_numbers_in_database = []
                                        # print(data)

                                        results_data = ''
                                        results = google_search(f'{P_N}', my_api_key, my_cse_id, num=4)
                                        count = 1
                                        for result in results:
                                            print(result['title'])
                                            print(result['snippet'])
                                            results_data += f"{count}. {result['title']}\n{result['snippet']}\n---------------------------------------------------------------------------------------------------------------------------\n\n"
                                            count += 1
                                        print(results_data)

                                        # self.label_info_1.configure(state='normal')
                                        # self.label_info_1.delete("1.0", tkinter.END)
                                        for i in data:
                                            # print(i)
                                            if P_N in i[6]:
                                                self.label_info_1.insert(tkinter.END, f"Found in inventory A\n", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END,
                                                                         f'Part Number: {P_N}\n', 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"SKU: ", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"{i[0]}\n")
                                                self.label_info_1.insert(tkinter.END, f"User Price:", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"{i[4]} ILS\n")
                                                self.label_info_1.insert(tkinter.END, f"Dealer Price:", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"{i[5]} ILS\n\n")
                                                self.label_info_1.insert(tkinter.END, "Useful information:\n\n",
                                                                         'bold_normal_2')
                                                self.label_info_1.insert(tkinter.END, f"{results_data}")
                                                self.label_info_1.insert(tkinter.END, f"\n\n------------------------------------------------------------------------------------------------------\n\n")

                                                counter = 1

                                        if counter == 0:
                                            print('Part Number not in Database')
                                            self.label_info_1.insert(tkinter.END,
                                                                     f'Part Number {P_N} not in Database\n\n', 'title')
                                            self.label_info_1.insert(tkinter.END,
                                                                     f'Useful information:\n\n',
                                                                     'bold_normal_2')
                                            self.label_info_1.insert(tkinter.END,
                                                                     f'{results_data}')
                                            # self.label_info_1.configure(state='disabled')

                                        found_counter += 1

                        # print('this is stuff',[self.label_info_1.get("1.0", tkinter.END).strip('\n')])
                        if part == 'Battery' and self.label_info_1.get("1.0",tkinter.END).strip('\n') == '':
                            print('what is up')
                            self.label_info_1.insert(tkinter.END,"This model doesn't seem to have a battery.","bold_normal")

                        if found_counter > 1:
                            self.label_info_1.insert("1.0", f"Found {found_counter} items\n\n", 'title')

                        self.label_info_1.configure(state='disabled')
                        self.button_1.configure(values=list(new_PN_values))

                        # table_data = re.findall("(<tr>.+<\/tr>)")

                    dell_data(hashed_id)

                    # P_N = None
                    # if part == 'Battery':
                    #
                    #     counter = 0
                    #
                    #     for battery in rows_data:
                    #         if 'Battery' in battery[1] or 'BATTERY' in battery[1] or 'BTRY' in battery[1]:
                    #             print('finally')
                    #             P_N = battery[0]
                    #             print(P_N)
                    #     if P_N != None:
                    #         cursor.execute(f"""Select * from {brand} where [P/N] NOT NULL""")
                    #
                    #         data = cursor.fetchall()
                    #
                    #         part_numbers_in_database = []
                    #         # print(data)
                    #
                    #         results_data = ''
                    #         results = google_search(f'{P_N}', my_api_key, my_cse_id, num=4)
                    #         count = 1
                    #         for result in results:
                    #             print(result['title'])
                    #             print(result['snippet'])
                    #             results_data += f"{count}. {result['title']}\n{result['snippet']}\n---------------------------------------------------------------------------------------------------------------------------\n\n"
                    #             count += 1
                    #         print(results_data)
                    #
                    #         self.label_info_1.configure(state='normal')
                    #         self.label_info_1.delete("1.0", tkinter.END)
                    #         for i in data:
                    #             # print(i)
                    #             if P_N in i[6]:
                    #                 self.label_info_1.insert("1.0", f"Found in inventory B\n", 'bold_normal')
                    #                 self.label_info_1.insert(tkinter.END, f"SKU: ", 'bold_normal')
                    #                 self.label_info_1.insert(tkinter.END, f"{i[0]}\n")
                    #                 self.label_info_1.insert(tkinter.END, f"User Price:", 'bold_normal')
                    #                 self.label_info_1.insert(tkinter.END, f"{i[4]} ILS\n")
                    #                 self.label_info_1.insert(tkinter.END, f"Dealer Price:", 'bold_normal')
                    #                 self.label_info_1.insert(tkinter.END, f"{i[5]} ILS\n\n")
                    #                 self.label_info_1.insert(tkinter.END, "4 searches from google:\n\n", 'bold_normal_2')
                    #                 self.label_info_1.insert(tkinter.END, f"{results_data}")
                    #                 self.label_info_1.configure(state='disabled')
                    #                 counter = 1
                    #
                    #         if counter == 0:
                    #             print('Part Number not in Database')
                    #             self.label_info_1.insert("1.0",
                    #                                      f'Part Number {P_N} not in Database\n\n', 'title')
                    #             self.label_info_1.insert(tkinter.END,
                    #                                      f'Here are 4 Searches from Google:\n\n', 'bold_normal_2')
                    #             self.label_info_1.insert(tkinter.END,
                    #                                      f'{results_data}')
                    #             self.label_info_1.configure(state='disabled')
                    #
                    # elif part == 'Adapter':
                    #     counter = 0
                    #     for adapter in rows_data:
                    #         # print(adapter)
                    #         if 'Adapter' in adapter[1] or 'ADPT' in adapter[1] or 'ADAPTER' in adapter[1]:
                    #             print('finally')
                    #             P_N = adapter[0]
                    #             print(P_N)
                    #     if P_N != None:
                    #         cursor.execute(f"""Select * from {brand} where [P/N] NOT NULL""")
                    #
                    #         data = cursor.fetchall()
                    #
                    #         part_numbers_in_database = []
                    #         # print(data)
                    #
                    #         results_data = ''
                    #         results = google_search(f'{P_N}', my_api_key, my_cse_id, num=4)
                    #         count = 1
                    #         for result in results:
                    #             print(result['title'])
                    #             print(result['snippet'])
                    #             results_data += f"{count}. {result['title']}\n{result['snippet']}\n---------------------------------------------------------------------------------------------------------------------------\n\n"
                    #             count += 1
                    #         print(results_data)
                    #         self.label_info_1.configure(state='normal')
                    #
                    #         self.label_info_1.configure(state='normal')
                    #         self.label_info_1.delete("1.0", tkinter.END)
                    #         for i in data:
                    #             # print(i)
                    #             if P_N in i[6]:
                    #                 self.label_info_1.insert("1.0", f"Found in inventory A\n", 'bold_normal')
                    #                 self.label_info_1.insert(tkinter.END, f"SKU: ", 'bold_normal')
                    #                 self.label_info_1.insert(tkinter.END, f"{i[0]}\n")
                    #                 self.label_info_1.insert(tkinter.END, f"User Price:", 'bold_normal')
                    #                 self.label_info_1.insert(tkinter.END, f"{i[4]} ILS\n")
                    #                 self.label_info_1.insert(tkinter.END, f"Dealer Price:", 'bold_normal')
                    #                 self.label_info_1.insert(tkinter.END, f"{i[5]} ILS\n\n")
                    #                 self.label_info_1.insert(tkinter.END, "4 searches from google:\n\n", 'bold_normal_2')
                    #                 self.label_info_1.insert(tkinter.END, f"{results_data}")
                    #                 self.label_info_1.configure(state='disabled')
                    #                 counter = 1
                    #
                    #         if counter == 0:
                    #             print('Part Number not in Database')
                    #             self.label_info_1.insert("1.0",
                    #                                      f'Part Number {P_N} not in Database\n\n', 'title')
                    #             self.label_info_1.insert(tkinter.END,
                    #                                      f'Here are 4 Searches from Google:\n\n', 'bold_normal_2')
                    #             self.label_info_1.insert(tkinter.END,
                    #                                      f'{results_data}')
                    #             self.label_info_1.configure(state='disabled')

                    self.progress_number.configure(text='100% Completed')
                    self.progressbar.set(1)

                except Exception as e:
                    print(e)
                    self.label_info_1.configure(state='normal')
                    self.label_info_1.delete("1.0", tkinter.END)
                    self.label_info_1.insert("1.0",
                                             f'Wrong Service Tag or Website is not accessible right now.', 'normal_fits_bold')
                    print('Wrong Service Tag')
                    self.progressbar.set(0)
                    self.progress_number.configure(text='0% Completed')

            elif brand == 'Lenovo':
                try:
                    SN = SN.replace('-','')

                    b = requests.get(f'https://support.lenovo.com/il/en/api/v4/mse/getproducts?productId={SN}')
                    if b.json() != []:
                        id_data = b.json()[0]['Id'].split('/')

                        parts_data = {'serialId': id_data[5], 'mtId': id_data[3], 'model': id_data[4]}

                        a = requests.post('https://pcsupport.lenovo.com/il/en/api/v4/upsellAggregation/parts/model',
                                          json=parts_data)
                        c = a.json()

                        print(c)

                        substitutes = 'No substitutes found'

                        # global P_N
                        P_N = None
                        print(c['data'])
                        self.label_info_1.configure(state='normal')
                        self.label_info_1.delete("1.0", tkinter.END)

                        found_counter = 0

                        new_PN_values = set()
                        for i in c['data']:
                            if part == 'Battery':
                                counter = 0


                                # for j in i['commodityVal']:
                                # print('hehe thi is j',j)
                                if i['commodityVal'] == 'Rechargeable Batteries , internal' or i['commodityVal'] == 'RECHARGEABLE BATTERIES':
                                    # print('noooooooooooooooooo')
                                    # if i['commodityVal'] == 'Rechargeable Batteries , internal':
                                    P_N = i['id']
                                    new_PN_values.add(P_N)
                                    print(P_N)
                                    print('PN above')
                                    if len(i['substitutes']) != 0:
                                        substitutes = ""
                                        for j in i['substitutes']:
                                            substitutes += f"\n{j['id']}"
                                            # print(j["id"])

                                    if P_N != None:
                                        cursor.execute(f"""Select * from {brand} where [P/N] NOT NULL""")

                                        data = cursor.fetchall()

                                        part_numbers_in_database = []
                                        # print(data)

                                        results_data = ''
                                        results = google_search(f'{P_N}', my_api_key, my_cse_id, num=4)
                                        count = 1
                                        for result in results:
                                            print(result['title'])
                                            print(result['snippet'])
                                            results_data += f"{count}. {result['title']}\n{result['snippet']}\n------------------------------------------------------------------------------------------------------\n\n"
                                            count += 1
                                        print(results_data)

                                        for i in data:
                                            # print(i)
                                            if P_N in i[6]:
                                                self.label_info_1.insert(tkinter.END, f"Found in inventory B\n",
                                                                         'bold_normal')
                                                self.label_info_1.insert(tkinter.END,
                                                                         f'Part Number: {P_N}\n', 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"SKU: ", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"{i[0]}\n")
                                                self.label_info_1.insert(tkinter.END, f"User Price:", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"{i[4]} ILS\n")
                                                self.label_info_1.insert(tkinter.END, f"Dealer Price:", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"{i[5]} ILS\n\n")
                                                self.label_info_1.insert(tkinter.END, "Useful information:\n\n",
                                                                         'bold_normal_2')
                                                self.label_info_1.insert(tkinter.END, f"{results_data}")
                                                self.label_info_1.insert(tkinter.END, f"\nAlternative part numbers:", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"\n{substitutes}")
                                                self.label_info_1.insert(tkinter.END, f"\n\n------------------------------------------------------------------------------------------------------\n\n")
                                                counter = 1

                                        if counter == 0:
                                            print('Part Number not in Database')
                                            self.label_info_1.insert("1.0",
                                                                     f'Part Number {P_N} not in Database\n\n', 'title')
                                            self.label_info_1.insert(tkinter.END,
                                                                     f'Useful information:\n\n',
                                                                     'bold_normal_2')
                                            self.label_info_1.insert(tkinter.END,
                                                                     f'{results_data}')
                                            self.label_info_1.insert(tkinter.END, f"\nAlternative part numbers:",
                                                                     'bold_normal')
                                            self.label_info_1.insert(tkinter.END, f"\n{substitutes}")

                                    found_counter+=1

                                # elif i['commodityVal'] == 'RECHARGEABLE BATTERIES':
                                #     P_N = i['id']
                                #     print(P_N)
                                #     print('PN above')
                                #     if len(i['substitutes']) != 0:
                                #         substitutes = ""
                                #         for j in i['substitutes']:
                                #             substitutes += f"\n{j['id']}"
                                #             # print(j["id"])
                                #
                                #     if P_N != None:
                                #         cursor.execute(f"""Select * from {brand} where [P/N] NOT NULL""")
                                #
                                #         data = cursor.fetchall()
                                #
                                #         part_numbers_in_database = []
                                #         # print(data)
                                #
                                #         results_data = ''
                                #         results = google_search(f'{P_N}', my_api_key, my_cse_id, num=4)
                                #         count = 1
                                #         for result in results:
                                #             print(result['title'])
                                #             print(result['snippet'])
                                #             results_data += f"{count}. {result['title']}\n{result['snippet']}\n---------------------------------------------------------------------------------------------------------------------------\n\n"
                                #             count += 1
                                #         print(results_data)
                                #
                                #         self.label_info_1.configure(state='normal')
                                #         self.label_info_1.delete("1.0", tkinter.END)
                                #         for i in data:
                                #             # print(i)
                                #             if P_N in i[6]:
                                #                 self.label_info_1.insert("1.0", f"Found in inventory B\n",
                                #                                          'bold_normal')
                                #                 self.label_info_1.insert(tkinter.END,
                                #                                          f'Part Number: {P_N}\n', 'bold_normal')
                                #                 self.label_info_1.insert(tkinter.END, f"SKU: ", 'bold_normal')
                                #                 self.label_info_1.insert(tkinter.END, f"{i[0]}\n")
                                #                 self.label_info_1.insert(tkinter.END, f"User Price:", 'bold_normal')
                                #                 self.label_info_1.insert(tkinter.END, f"{i[4]} ILS\n")
                                #                 self.label_info_1.insert(tkinter.END, f"Dealer Price:", 'bold_normal')
                                #                 self.label_info_1.insert(tkinter.END, f"{i[5]} ILS\n\n")
                                #                 self.label_info_1.insert(tkinter.END, "Useful information:\n\n",
                                #                                          'bold_normal_2')
                                #                 self.label_info_1.insert(tkinter.END, f"{results_data}")
                                #                 self.label_info_1.insert(tkinter.END, f"\nAlternative part numbers:", 'bold_normal')
                                #                 self.label_info_1.insert(tkinter.END, f"\n{substitutes}")
                                #                 self.label_info_1.configure(state='disabled')
                                #                 counter = 1
                                #
                                #         if counter == 0:
                                #             print('Part Number not in Database')
                                #             self.label_info_1.insert("1.0",
                                #                                      f'Part Number {P_N} not in Database\n\n', 'title')
                                #             self.label_info_1.insert(tkinter.END,
                                #                                      f'Useful information:\n\n',
                                #                                      'bold_normal_2')
                                #             self.label_info_1.insert(tkinter.END,
                                #                                      f'{results_data}')
                                #             self.label_info_1.insert(tkinter.END, f"\nAlternative part numbers:",
                                #                                      'bold_normal')
                                #             self.label_info_1.insert(tkinter.END, f"\n{substitutes}")
                                #
                                #             self.label_info_1.configure(state='disabled')

                            elif part == 'Adapter':
                                counter = 0

                                if i['commodityVal'] == 'AC ADAPTERS':
                                    P_N = i['id']
                                    print(P_N)
                                    print('PN above')

                                    if len(i['substitutes']) != 0:
                                        substitutes = ""
                                        for j in i['substitutes']:
                                            substitutes += f"\n{j['id']}"
                                            # print(j["id"])

                                    if P_N != None:
                                        cursor.execute(f"""Select * from {brand} where [P/N] NOT NULL""")

                                        data = cursor.fetchall()

                                        part_numbers_in_database = []
                                        # print(data)

                                        results_data = ''
                                        results = google_search(f'{P_N}', my_api_key, my_cse_id, num=4)
                                        count = 1
                                        for result in results:
                                            print(result['title'])
                                            print(result['snippet'])
                                            results_data += f"{count}. {result['title']}\n{result['snippet']}\n---------------------------------------------------------------------------------------------------------------------------\n\n"
                                            count += 1
                                        print(results_data)
                                        self.label_info_1.configure(state='normal')

                                        self.label_info_1.configure(state='normal')
                                        self.label_info_1.delete("1.0", tkinter.END)
                                        for i in data:
                                            # print(i)
                                            if P_N in i[6]:
                                                self.label_info_1.insert(tkinter.END, f"Found in inventory A\n",
                                                                         'bold_normal')
                                                self.label_info_1.insert(tkinter.END,
                                                                         f'Part Number: {P_N}\n', 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"SKU: ", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"{i[0]}\n")
                                                self.label_info_1.insert(tkinter.END, f"User Price:", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"{i[4]} ILS\n")
                                                self.label_info_1.insert(tkinter.END, f"Dealer Price:", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"{i[5]} ILS\n\n")
                                                self.label_info_1.insert(tkinter.END, "Useful information:\n\n",
                                                                         'bold_normal_2')
                                                self.label_info_1.insert(tkinter.END, f"{results_data}")
                                                self.label_info_1.insert(tkinter.END, f"\nAlternative part numbers:", 'bold_normal')
                                                self.label_info_1.insert(tkinter.END, f"{substitutes}")

                                                # self.label_info_1.configure(state='disabled')
                                                counter = 1

                                        if counter == 0:
                                            print('Part Number not in Database')
                                            self.label_info_1.insert("1.0",
                                                                     f'Part Number {P_N} not in Database\n\n', 'title')
                                            self.label_info_1.insert(tkinter.END,
                                                                     f'Useful information:\n\n',
                                                                     'bold_normal_2')
                                            self.label_info_1.insert(tkinter.END,
                                                                     f'{results_data}')
                                            self.label_info_1.insert(tkinter.END, f"\nAlternative part numbers:",
                                                                     'bold_normal')
                                            self.label_info_1.insert(tkinter.END, f"\n{substitutes}")

                                            self.label_info_1.configure(state='disabled')

                                    found_counter+=1

                        if found_counter > 1:
                            self.label_info_1.insert("1.0", f"Found {found_counter} items\n\n", 'title')

                        self.label_info_1.configure(state='disabled')
                        self.button_1.configure(values=list(new_PN_values))



                    else:
                        self.label_info_1.configure(state='normal')
                        self.label_info_1.delete("1.0", tkinter.END)
                        self.label_info_1.insert("1.0",
                                                 f'Wrong serial number or Website is not accessible right now.', 'normal_fits_bold')
                        print('Wrong Serial Number')
                        self.progressbar.set(0)
                        self.progress_number.configure(text='0% Completed')

                    # if part == 'Battery':
                    #     counter = 0
                    #     for battery in rows_data:
                    #         # if 'Rechargeable Batteries , internal' in battery[0] or 'BATTERY' in battery[0]:
                    #         if 'Rechargeable Batteries , internal' in battery[0]:
                    #             print('finally')
                    #             P_N = battery[1]
                    #             print(P_N)
                    #
                    #     # if P_N != None:
                    #     #     cursor.execute(f"""Select * from {brand} where [P/N] NOT NULL""")
                    #     #
                    #     #     data = cursor.fetchall()
                    #     #
                    #     #     part_numbers_in_database = []
                    #     #     # print(data)
                    #     #
                    #     #     results_data = ''
                    #     #     results = google_search(f'{P_N}', my_api_key, my_cse_id, num=4)
                    #     #     count = 1
                    #     #     for result in results:
                    #     #         print(result['title'])
                    #     #         print(result['snippet'])
                    #     #         results_data += f"{count}. {result['title']}\n{result['snippet']}\n---------------------------------------------------------------------------------------------------------------------------\n\n"
                    #     #         count += 1
                    #     #     print(results_data)
                    #     #
                    #     #     self.label_info_1.configure(state='normal')
                    #     #     self.label_info_1.delete("1.0", tkinter.END)
                    #     #     for i in data:
                    #     #         # print(i)
                    #     #         if P_N in i[6]:
                    #     #             self.label_info_1.insert("1.0", f"Found in inventory B\n", 'bold_normal')
                    #     #             self.label_info_1.insert(tkinter.END, f"SKU: ", 'bold_normal')
                    #     #             self.label_info_1.insert(tkinter.END, f"{i[0]}\n")
                    #     #             self.label_info_1.insert(tkinter.END, f"User Price:", 'bold_normal')
                    #     #             self.label_info_1.insert(tkinter.END, f"{i[4]} ILS\n")
                    #     #             self.label_info_1.insert(tkinter.END, f"Dealer Price:", 'bold_normal')
                    #     #             self.label_info_1.insert(tkinter.END, f"{i[5]} ILS\n\n")
                    #     #             self.label_info_1.insert(tkinter.END, "4 searches from google:\n\n", 'bold_normal_2')
                    #     #             self.label_info_1.insert(tkinter.END, f"{results_data}")
                    #     #             self.label_info_1.configure(state='disabled')
                    #     #             counter = 1
                    #     #
                    #     #     if counter == 0:
                    #     #         print('Part Number not in Database')
                    #     #         self.label_info_1.insert("1.0",
                    #     #                                  f'Part Number {P_N} not in Database\n\n', 'title')
                    #     #         self.label_info_1.insert(tkinter.END,
                    #     #                                  f'Here are 4 Searches from Google:\n\n', 'bold_normal_2')
                    #     #         self.label_info_1.insert(tkinter.END,
                    #     #                                  f'{results_data}')
                    #     #         self.label_info_1.configure(state='disabled')
                    #
                    #
                    # elif part == 'Adapter':
                    #     counter = 0
                    #     for adapter in rows_data:
                    #         # print(adapter)
                    #         if 'AC ADAPTERS' in adapter[0]:
                    #             # if 'AC ADAPTERS' in adapter[0] or 'ADPT' in adapter[1] or 'ADAPTER' in adapter[1]:
                    #             print('finally')
                    #             # tkinter.m
                    #             P_N = adapter[1]
                    #             print(P_N)
                    #     # if P_N != None:
                    #     #     cursor.execute(f"""Select * from {brand} where [P/N] NOT NULL""")
                    #     #
                    #     #     data = cursor.fetchall()
                    #     #
                    #     #     part_numbers_in_database = []
                    #     #     # print(data)
                    #     #
                    #     #     results_data = ''
                    #     #     results = google_search(f'{P_N}', my_api_key, my_cse_id, num=4)
                    #     #     count = 1
                    #     #     for result in results:
                    #     #         print(result['title'])
                    #     #         print(result['snippet'])
                    #     #         results_data += f"{count}. {result['title']}\n{result['snippet']}\n---------------------------------------------------------------------------------------------------------------------------\n\n"
                    #     #         count += 1
                    #     #     print(results_data)
                    #     #     self.label_info_1.configure(state='normal')
                    #     #
                    #     #     self.label_info_1.configure(state='normal')
                    #     #     self.label_info_1.delete("1.0", tkinter.END)
                    #     #     for i in data:
                    #     #         # print(i)
                    #     #         if P_N in i[6]:
                    #     #             self.label_info_1.insert("1.0", f"Found in inventory A\n", 'bold_normal')
                    #     #             self.label_info_1.insert(tkinter.END, f"SKU: ", 'bold_normal')
                    #     #             self.label_info_1.insert(tkinter.END, f"{i[0]}\n")
                    #     #             self.label_info_1.insert(tkinter.END, f"User Price:", 'bold_normal')
                    #     #             self.label_info_1.insert(tkinter.END, f"{i[4]} ILS\n")
                    #     #             self.label_info_1.insert(tkinter.END, f"Dealer Price:", 'bold_normal')
                    #     #             self.label_info_1.insert(tkinter.END, f"{i[5]} ILS\n\n")
                    #     #             self.label_info_1.insert(tkinter.END, "4 searches from google:\n\n", 'bold_normal_2')
                    #     #             self.label_info_1.insert(tkinter.END, f"{results_data}")
                    #     #             self.label_info_1.configure(state='disabled')
                    #     #             counter = 1
                    #     #
                    #     #     if counter == 0:
                    #     #         print('Part Number not in Database')
                    #     #         self.label_info_1.insert("1.0",
                    #     #                                  f'Part Number {P_N} not in Database\n\n', 'title')
                    #     #         self.label_info_1.insert(tkinter.END,
                    #     #                                  f'Here are 4 Searches from Google:\n\n', 'bold_normal_2')
                    #     #         self.label_info_1.insert(tkinter.END,
                    #     #                                  f'{results_data}')
                    #     #         self.label_info_1.configure(state='disabled')

                    self.progress_number.configure(text='100% Completed')
                    self.progressbar.set(1)

                except Exception as e:
                    print(e)
                    self.label_info_1.configure(state='normal')
                    self.label_info_1.delete("1.0", tkinter.END)
                    self.label_info_1.insert("1.0",
                                             f'Wrong serial number or Website is not accessible right now.', 'normal_fits_bold')
                    print('Wrong Serial Number')
                    self.progressbar.set(0)
                    self.progress_number.configure(text='0% Completed')

            elif brand == 'Asus':
                # global P_N
                serv = ChromeService(ChromeDriverManager().install())
                serv.creationflags = CREATE_NO_WINDOW

                driver = webdriver.Chrome(service=serv, options=chrome_options)

                driver.minimize_window()

                rows_data = []

                new_PN_values = set()

                if part == 'Battery':
                    counter = 0
                    try:
                        # driver.get('https://www.asusparts.eu/en/search?q=X421EA&ProductCategory=AC%20Adapter')
                        driver.get(f'https://www.asusparts.eu/en/search?q={SN}&ProductCategory=Battery')

                        time.sleep(5)

                        # driver.find_element(by=By.XPATH, value='//*[@id="facetedSearchCompact"]/div[3]/ul/li[1]/ul/li[1]/label/span').click()
                        template = driver.find_element(by=By.CLASS_NAME, value='product-list')
                        # print(template.text)
                        links_lst = []
                        for row in template.find_elements(by=By.CSS_SELECTOR,
                                                          value='li[class="product-list__item js-product-list__item"]'):
                            links = row.find_element(by=By.TAG_NAME, value='a').get_attribute('href')
                            links_lst.append(links.strip())
                            # print('\n\n')

                        if len(links_lst) >= 3:
                            links_lst = [links_lst[0], links_lst[1], links_lst[2]]

                        self.label_info_1.configure(state='normal')
                        self.label_info_1.delete("1.0", tkinter.END)
                        count_number = 1

                        found_counter = 0

                        for link in links_lst:

                            driver.get(link)

                            product_detail = driver.find_element(by=By.CSS_SELECTOR, value='div[class="product-detail"]')
                            ul = product_detail.find_element(by=By.TAG_NAME, value='ul')
                            items = ul.find_elements(by=By.TAG_NAME, value='li')
                            P_N = items[0].text.split(':')[1].strip()
                            print(P_N)
                            new_PN_values.add(P_N)

                            lenOfPage = driver.execute_script(
                                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                            match = False
                            while (match == False):
                                lastCount = lenOfPage
                                time.sleep(3)
                                lenOfPage = driver.execute_script(
                                    "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                                if lastCount == lenOfPage:
                                    match = True

                            fits_to_text = ''

                            try:
                                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/main/div/div/div/div/div[2]/div/div/div/section/nav/label[2]'))).click()
                                fits_to = driver.find_element(by=By.CSS_SELECTOR, value='section[class="tab__content-container"]')
                                # print(fits_to.text)
                                fits_to_il = fits_to.find_elements(by=By.TAG_NAME, value='li')
                                for i in fits_to_il:
                                    if i.text.strip() != '':
                                        fits_to_text += f'{i.text.strip()}\n'
                            except:
                                fits_to_text = ''

                            # print(fits_to_text)

                            time.sleep(2)

                            if P_N != None:
                                cursor.execute(f"""Select * from {brand} where [P/N] NOT NULL""")

                                data = cursor.fetchall()

                                part_numbers_in_database = []
                                # print(data)

                                results_data = ''
                                results = google_search(f'{P_N}', my_api_key, my_cse_id, num=4)
                                count = 1
                                for result in results:
                                    print(result['title'])
                                    print(result['snippet'])
                                    results_data += f"{count}. {result['title']}\n{result['snippet']}\n---------------------------------------------------------------------------------------------------------------------------\n\n"
                                    count += 1
                                print(results_data)

                                # self.label_info_1.configure(state='normal')
                                # self.label_info_1.delete("1.0", tkinter.END)
                                for i in data:
                                    # print(i)
                                    if P_N in i[6]:
                                        # self.label_info_1.insert(tkinter.END,f'{count_number}. Part Number {P_N} Found in Database\n\n','title')
                                        self.label_info_1.insert(tkinter.END, f"Found in inventory B\n", 'bold_normal')
                                        self.label_info_1.insert(tkinter.END,
                                                                 f'Part Number: {P_N}\n', 'bold_normal')
                                        self.label_info_1.insert(tkinter.END, f"SKU: ", 'bold_normal')
                                        self.label_info_1.insert(tkinter.END, f"{i[0]}\n")
                                        self.label_info_1.insert(tkinter.END, f"User Price:", 'bold_normal')
                                        self.label_info_1.insert(tkinter.END, f"{i[4]} ILS\n")
                                        self.label_info_1.insert(tkinter.END, f"Dealer Price:", 'bold_normal')
                                        self.label_info_1.insert(tkinter.END, f"{i[5]} ILS\n\n")
                                        if fits_to_text != '':
                                            self.label_info_1.insert(tkinter.END,
                                                                     f'It fits to:',
                                                                     'normal_fits_bold')
                                            self.label_info_1.insert(tkinter.END,
                                                                     f'\n{fits_to_text}\n',
                                                                     'normal')
                                        self.label_info_1.insert(tkinter.END, "Useful information:\n\n", 'bold_normal_2')
                                        self.label_info_1.insert(tkinter.END, f"{results_data}")
                                        # self.label_info_1.configure(state='disabled')
                                        counter = 1

                                if counter == 0:
                                    print('Part Number not in Database')
                                    self.label_info_1.insert(tkinter.END,
                                                             f'{count_number}. Part Number {P_N} not in Database\n\n', 'title')
                                    if fits_to_text != '':
                                        self.label_info_1.insert(tkinter.END,
                                                                 f'It fits to:',
                                                                 'normal_fits_bold')
                                        self.label_info_1.insert(tkinter.END,
                                                                 f'\n{fits_to_text}\n',
                                                                 'normal')
                                    self.label_info_1.insert(tkinter.END,
                                                             f'Useful information:\n\n', 'bold_normal_2')
                                    self.label_info_1.insert(tkinter.END,
                                                             f'{results_data}')
                                    # self.label_info_1.configure(state='disabled')
                            count_number+=1

                            found_counter+=1

                        if found_counter > 1:
                            self.label_info_1.insert("1.0", f"Found {found_counter} items\n\n", 'title')

                        self.label_info_1.configure(state='disabled')
                        self.button_1.configure(values=list(new_PN_values))



                    except Exception as e:

                        self.label_info_1.configure(state='normal')

                        self.label_info_1.delete("1.0", tkinter.END)

                        self.label_info_1.insert("1.0",

                                                 f'Wrong product name or Website is not accessible right now.', 'normal_fits_bold')

                        print('Wrong product number')
                        self.progressbar.set(0)
                        self.progress_number.configure(text='0% Completed')

                        # print('incorrect ')

                    # for battery in rows_data:
                    #     # if 'Rechargeable Batteries , internal' in battery[0] or 'BATTERY' in battery[0]:
                    #     if 'Rechargeable Batteries , internal' in battery[0]:
                    #         print('finally')
                    #         P_N = battery[1]
                    #         print(P_N)
                    # if P_N != None:
                    #     cursor.execute(f"""Select * from {brand} where [P/N] NOT NULL""")
                    #
                    #     data = cursor.fetchall()
                    #
                    #     part_numbers_in_database = []
                    #     # print(data)
                    #
                    #     results_data = ''
                    #     results = google_search(f'{P_N}', my_api_key, my_cse_id, num=4)
                    #     count = 1
                    #     for result in results:
                    #         print(result['title'])
                    #         print(result['snippet'])
                    #         results_data += f"{count}. {result['title']}\n{result['snippet']}\n\n"
                    #         count += 1
                    #     print(results_data)
                    #
                    #     self.label_info_1.configure(state='normal')
                    #     self.label_info_1.delete("1.0", tkinter.END)
                    #     for i in data:
                    #         # print(i)
                    #         if P_N in i[6]:
                    #             self.label_info_1.insert("1.0", f"SKU: {i[0]}\n" +
                    #                                      f"User Price: {i[5]} ILS\n" +
                    #                                      f"Dealer Price: {i[6]} ILS\n" +
                    #                                      "4 searches from google\n\n" +
                    #                                      f"{results_data}")
                    #             self.label_info_1.configure(state='disabled')
                    #         else:
                    #             print('Part Number not in Database')
                    #             print(i[6])
                    #             self.label_info_1.insert("1.0",
                    #                                      f'Part Number not in Database\n\nHere are 4 Searches from Google:\n\n{results_data}')
                    #             self.label_info_1.configure(state='disabled')

                elif part == 'Adapter':
                    counter = 0
                    try:
                        driver.get(f'https://www.asusparts.eu/en/search?q={SN}&ProductCategory=AC%20Adapter')
                        # driver.get('https://www.asusparts.eu/en/search?q=X421EA&ProductCategory=Battery')

                        time.sleep(5)

                        # driver.find_element(by=By.XPATH, value='//*[@id="facetedSearchCompact"]/div[3]/ul/li[1]/ul/li[1]/label/span').click()
                        template = driver.find_element(by=By.CLASS_NAME, value='product-list')
                        # print(template.text)
                        links_lst = []
                        for row in template.find_elements(by=By.CSS_SELECTOR,
                                                          value='li[class="product-list__item js-product-list__item"]'):
                            links = row.find_element(by=By.TAG_NAME, value='a').get_attribute('href')
                            links_lst.append(links.strip())
                            # print('\n\n')

                        if len(links_lst) >= 3:
                            links_lst = [links_lst[0], links_lst[1], links_lst[2]]

                        self.label_info_1.configure(state='normal')
                        self.label_info_1.delete("1.0", tkinter.END)

                        count_number = 1

                        found_counter = 0

                        for link in links_lst:

                            driver.get(link)

                            product_detail = driver.find_element(by=By.CSS_SELECTOR, value='div[class="product-detail"]')
                            ul = product_detail.find_element(by=By.TAG_NAME, value='ul')
                            items = ul.find_elements(by=By.TAG_NAME, value='li')
                            P_N = items[0].text.split(':')[1].strip()
                            print(P_N)
                            new_PN_values.add(P_N)

                            lenOfPage = driver.execute_script(
                                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                            match = False
                            while (match == False):
                                lastCount = lenOfPage
                                time.sleep(3)
                                lenOfPage = driver.execute_script(
                                    "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                                if lastCount == lenOfPage:
                                    match = True

                            fits_to_text = ''

                            try:
                                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                                            '/html/body/main/div/div/div/div/div[2]/div/div/div/section/nav/label[2]'))).click()
                                fits_to = driver.find_element(by=By.CSS_SELECTOR,
                                                              value='section[class="tab__content-container"]')
                                # print(fits_to.text)
                                fits_to_il = fits_to.find_elements(by=By.TAG_NAME, value='li')
                                for i in fits_to_il:
                                    if i.text.strip() != '':
                                        fits_to_text += f'{i.text.strip()}\n'
                            except Exception as e:
                                print(e)
                                fits_to_text = ''

                            time.sleep(2)

                            if P_N != None:
                                cursor.execute(f"""Select * from {brand} where [P/N] NOT NULL""")

                                data = cursor.fetchall()

                                part_numbers_in_database = []
                                # print(data)

                                results_data = ''
                                results = google_search(f'{P_N}', my_api_key, my_cse_id, num=4)
                                count = 1
                                for result in results:
                                    print(result['title'])
                                    print(result['snippet'])
                                    results_data += f"{count}. {result['title']}\n{result['snippet']}\n---------------------------------------------------------------------------------------------------------------------------\n\n"
                                    count += 1
                                print(results_data)

                                # self.label_info_1.configure(state='normal')
                                # self.label_info_1.delete("1.0", tkinter.END)
                                for i in data:
                                    # print(i)
                                    if P_N in i[6]:
                                        # self.label_info_1.insert(tkinter.END,
                                        #                          # f'{count_number}. Part Number {P_N} Found in Database\n\n',
                                        #                          'title')
                                        self.label_info_1.insert(tkinter.END, f"Found in inventory A\n", 'bold_normal')
                                        self.label_info_1.insert(tkinter.END,
                                                                 f'Part Number: {P_N}\n', 'bold_normal')
                                        self.label_info_1.insert(tkinter.END, f"SKU: ", 'bold_normal')
                                        self.label_info_1.insert(tkinter.END, f"{i[0]}\n")
                                        self.label_info_1.insert(tkinter.END, f"User Price:", 'bold_normal')
                                        self.label_info_1.insert(tkinter.END, f"{i[4]} ILS\n")
                                        self.label_info_1.insert(tkinter.END, f"Dealer Price:", 'bold_normal')
                                        self.label_info_1.insert(tkinter.END, f"{i[5]} ILS\n\n")
                                        if fits_to_text != '':
                                            self.label_info_1.insert(tkinter.END,
                                                                     f'It fits to:',
                                                                     'normal_fits_bold')
                                            self.label_info_1.insert(tkinter.END,
                                                                     f'\n{fits_to_text}\n\n',
                                                                     'normal')
                                        self.label_info_1.insert(tkinter.END, "Useful information:\n\n", 'bold_normal_2')
                                        self.label_info_1.insert(tkinter.END, f"{results_data}")
                                        # self.label_info_1.configure(state='disabled')
                                        counter = 1

                                if counter == 0:
                                    print('Part Number not in Database')
                                    self.label_info_1.insert(tkinter.END,
                                                             f'{count_number}. Part Number {P_N} not in Database\n\n', 'title')
                                    if fits_to_text != '':
                                        self.label_info_1.insert(tkinter.END,
                                                                 f'It fits to:',
                                                                 'normal_fits_bold')
                                        self.label_info_1.insert(tkinter.END,
                                                                 f'\n{fits_to_text}\n\n',
                                                                 'normal')
                                    self.label_info_1.insert(tkinter.END,
                                                             f'Useful information:\n\n', 'bold_normal_2')
                                    self.label_info_1.insert(tkinter.END,
                                                             f'{results_data}')
                                count_number += 1

                                found_counter+=1

                        if found_counter > 1:
                            self.label_info_1.insert("1.0", f"Found {found_counter} items\n\n", 'title')

                        self.label_info_1.configure(state='disabled')
                        self.button_1.configure(values=list(new_PN_values))



                    except Exception as e:
                        self.label_info_1.configure(state='normal')
                        self.label_info_1.delete("1.0", tkinter.END)
                        self.label_info_1.insert("1.0",
                                                 f'Wrong product name or Website is not accessible right now.', 'normal_fits_bold')
                        print('Wrong product number')
                        # print('incorrect ')

                        self.progress_number.configure(text='0% Completed')
                        self.progressbar.set(0.01)

                self.progress_number.configure(text='100% Completed')
                self.progressbar.set(1)
        except:
            self.label_info_1.configure(state='normal')
            self.label_info_1.delete("1.0", tkinter.END)
            self.label_info_1.insert("1.0",
                                     f'Internet Connection Problem.\n\nPlease connect to Internet.','normal_fits_bold')
            print('No internet connection')
            self.progressbar.set(0.01)
            self.progress_number.configure(text='0% Completed')

        # print(rows_data)

    def change_appearance_mode(self, new_appearance_mode):
        if new_appearance_mode == "Dark":
            self.bg_image = ImageTk.PhotoImage(file='black background.png')
            self.image_label.configure(image=self.bg_image, bg='#2A2D2E')
        elif new_appearance_mode == "Light":
            self.bg_image = ImageTk.PhotoImage(file='white background.png')
            self.image_label.configure(image=self.bg_image, bg='#D1D5D8')


        customtkinter.set_appearance_mode(new_appearance_mode)


    def on_closing(self, event=0):
        self.destroy()


if __name__ == "__main__":
    app = App()
    # app.after(2000, print('a'))
    app.mainloop()
