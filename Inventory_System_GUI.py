from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
# from PyQt5 import QtSql
# from PyQt5.QtSql import QSqlDatabase,QSqlQuery

from time import sleep
import sys, os

import pymysql

from os import path

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

from PyQt5.uic import loadUiType

# 如果第一個不行，使用第二種方式: path.dirname('__file__') 會取得當下環境的絕對路徑
FORM_CLASS,_=loadUiType(resource_path("main.ui"))
# FORM_CLASS,_=loadUiType(path.join(path.dirname('__file__'), "main.ui"))

import sqlite3

# 主程式，連接PyQt並與main.ui互動
class Main(QMainWindow, FORM_CLASS):
    def __init__(self,parent=None):
        super(Main,self).__init__(parent)
        self.setupUi(self)
        self.Handel_Buttons()
        
        
    def Handel_Buttons(self): # 按鈕按下去後，連接到後面寫的function
        self.refresh_btn.clicked.connect(self.GET_DATA)
        self.search_btn.clicked.connect(self.SEARCH)
        self.query_btn.clicked.connect(self.SQL_SEARCH_TABLE)
        self.search_btn_3.clicked.connect(self.DISPLAY_INFO)
        self.update_btn.clicked.connect(self.UPDATE)
        self.delete_btn.clicked.connect(self.DELETE)
        self.insert_btn.clicked.connect(self.INSERT)

        self.search_btn_2.clicked.connect(self.GET_DATA_FROM_MYSQL)

        self.table_list.currentIndexChanged.connect(self.auto_refresh) # 偵測只要目前的Index改變(選單選了其他表)，則自動更新table
        self.table_list_3.currentIndexChanged.connect(self.auto_refresh)

    
    def auto_refresh(self):
        self.GET_DATA()
    
    
    def GET_DATA(self): # 將使用者選擇的Table表單印在ui的Table widget上
        db = sqlite3.connect(resource_path("inventoryDB.db")) # 連接Sqlite3 database
        cursor = db.cursor() # 透過指標與database互動

        table = self.table_list.currentText() # 取得Table選單資訊(字串)，存進變數

        command=''' SELECT * from '''+str(table) # 建立SQL語法

        result = cursor.execute(command) # 執行SQL語法，對database進行操作

        names = [description[0] for description in cursor.description] # result只是存table的內容(tuple)，這邊用cursor.description來抓table的欄位(attribute)

        self.table.setColumnCount(len(names)) # 設欄位數量
        self.table.setHorizontalHeaderLabels(names) # 設各個欄位名稱(default是按index依序給)
        self.table.setRowCount(0)

        # 將table的內容(tuple)顯示在PyQt的Table widget上
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))


        cursor3 = db.cursor()

        table3 = self.table_list_3.currentText()
        
        command_3 =''' SELECT * from '''+str(table3)
        
        result3 = cursor3.execute(command_3)

        names = [description[0] for description in cursor.description]

        self.table_3.setColumnCount(len(names))
        self.table_3.setHorizontalHeaderLabels(names)
        self.table_3.setRowCount(0)
        
        for row_number, row_data in enumerate(result3):
            self.table_3.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table_3.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        
    
    def SEARCH(self):
        db=sqlite3.connect(resource_path("inventoryDB.db"))
        cursor=db.cursor()

        query = str(self.query_list.currentText())
        if query == "存貨量最多的產品":
            command = ''' SELECT PNUM, WNUM, MAX(P_CURRENT_STOCK) FROM PRODUCT_INVENTORY '''
            result = cursor.execute(command)
        elif query == "存貨量最少的產品":
            command = ''' SELECT PNUM, WNUM, MIN(P_CURRENT_STOCK) FROM PRODUCT_INVENTORY '''
            result = cursor.execute(command)
        elif query == "低於安全存貨的產品":
            command = ''' SELECT PNUMBER, PNAME, P_SAFETY_STOCK FROM PRODUCT, PRODUCT_INVENTORY WHERE PRODUCT.PNUMBER = PRODUCT_INVENTORY.PNUM AND PRODUCT_INVENTORY.P_CURRENT_STOCK < PRODUCT.P_SAFETY_STOCK '''
            result = cursor.execute(command)
        elif query == "低於安全存貨的原料":
            command = ''' SELECT MNUMBER, MNAME, M_SAFETY_STOCK FROM RAW_MATERIAL, MATERIAL_INVENTORY WHERE RAW_MATERIAL.MNUMBER = MATERIAL_INVENTORY.MNUM AND MATERIAL_INVENTORY.M_CURRENT_STOCK < RAW_MATERIAL.M_SAFETY_STOCK '''
            result = cursor.execute(command)
        elif query == "需要的原料低於目前存貨的產品":
            command = ''' SELECT PNUMBER, PNAME, P_SAFETY_STOCK FROM PRODUCT WHERE PNUMBER IN (SELECT PNO FROM BOM, MATERIAL_INVENTORY WHERE MNO=MNUM AND M_CURRENT_STOCK < NEED_AMOUNT) '''
            result = cursor.execute(command)
        elif query == "需要的原料沒有低於目前存貨的產品":
            command = ''' SELECT PNUMBER, PNAME, P_SAFETY_STOCK FROM PRODUCT WHERE PNUMBER NOT IN (SELECT PNO FROM BOM, MATERIAL_INVENTORY WHERE MNO=MNUM AND M_CURRENT_STOCK < NEED_AMOUNT) '''
            result = cursor.execute(command)
        elif query == "若任一原料存量過500，顯示有貨的倉庫":
            command = ''' SELECT DISTINCT WNUMBER, WLOCATION, MGRSSN FROM MATERIAL_INVENTORY AS M, WAREHOUSE AS W WHERE M.WNUM=W.WNUMBER AND EXISTS (SELECT * FROM MATERIAL_INVENTORY WHERE M_CURRENT_STOCK > 500) '''
            result = cursor.execute(command)
        elif query == "若原料存量都沒過500，顯示有貨的倉庫":
            command = ''' SELECT DISTINCT WNUMBER, WLOCATION, MGRSSN FROM MATERIAL_INVENTORY AS M, WAREHOUSE AS W WHERE M.WNUM=W.WNUMBER AND NOT EXISTS (SELECT * FROM MATERIAL_INVENTORY WHERE M_CURRENT_STOCK > 500) '''
            result = cursor.execute(command)
        elif query == "找出目前有幾筆木板的訂單":
            command = ''' SELECT COUNT(PONUMBER) FROM PURCHASE_ORDER WHERE ITEM_NAME="木板" '''
            result = cursor.execute(command)
        elif query == "WH04號倉庫目前的總存量(產品+物料)":
            command = ''' SELECT SUM(TOTAL_INVENTORY) FROM ( SELECT SUM(M_CURRENT_STOCK) TOTAL_INVENTORY FROM MATERIAL_INVENTORY WHERE WNUM = "WH04" UNION ALL SELECT SUM(P_CURRENT_STOCK) TOTAL_INVENTORY FROM PRODUCT_INVENTORY WHERE WNUM = "WH04") '''
            result = cursor.execute(command)
        elif query == "所有產品目前的平均存量":
            command = ''' SELECT AVG(P_CURRENT_STOCK) FROM PRODUCT_INVENTORY '''
            result = cursor.execute(command)
        elif query == "將至少存有2樣以上產品的倉庫資訊列出來":
            command = ''' SELECT WNUMBER, WLOCATION, MGRSSN FROM WAREHOUSE AS W, PRODUCT_INVENTORY AS P WHERE W.WNUMBER = P.WNUM GROUP BY P.WNUM HAVING COUNT(*)>2 '''
            result = cursor.execute(command)
        
        self.table.setRowCount(0) 
        
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    
    def SQL_SEARCH_TABLE(self):
        db=sqlite3.connect(resource_path("inventoryDB.db"))
        cursor=db.cursor()

        user_input = self.query_text.toPlainText()

        command = '''  ''' + str(user_input)
        result = cursor.execute(command)

        db.commit() # Remember to commit the transaction after executing, commit means this transaction were finished.

        self.textBrowser_result.clear()
        
        self.table.setRowCount(0)
        
        for row_number, row_data in enumerate(result):
            self.textBrowser_result.append(str(row_data)) # 將result資料一筆一筆加進去
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    
    def DISPLAY_INFO(self):
        db=sqlite3.connect(resource_path("inventoryDB.db"))
        cursor=db.cursor()
        cursor2=db.cursor()

        table = self.table_list_3.currentText() # 取得目前選單選的訊息
        id_info =self.id_info.text() # 取得使用者輸入訊息

        if table == 'PRODUCT':

            name_info_command= ''' SELECT PNAME FROM PRODUCT WHERE PNUMBER='''+str(id_info)
            safety_stock_command= ''' SELECT P_SAFETY_STOCK FROM PRODUCT WHERE PNUMBER='''+str(id_info)
        
            name_info=cursor.execute(name_info_command)
            safety_stock=cursor2.execute(safety_stock_command)
            
            self.name_info.setText(str(name_info.fetchone()[0]))
            self.safety_stock.setText(str(safety_stock.fetchone()[0]))

        elif table == 'RAW_MATERIAL':

            name_info_command= ''' SELECT MNAME FROM RAW_MATERIAL WHERE MNUMBER="'''+ str(id_info) + '''"'''
            safety_stock_command= ''' SELECT M_SAFETY_STOCK FROM RAW_MATERIAL WHERE MNUMBER="'''+ str(id_info) + '''"'''
        
            name_info=cursor.execute(name_info_command)
            safety_stock=cursor2.execute(safety_stock_command)
            
            self.name_info.setText(str(name_info.fetchone()[0])) # 設定QLineEdit要顯示的訊息
            self.safety_stock.setText(str(safety_stock.fetchone()[0])) # fetchone() 抓取單筆資料，fetchall()抓取整串資料


    def UPDATE(self):
        db=sqlite3.connect("inventoryDB.db")
        cursor=db.cursor()

        table = self.table_list_3.currentText()

        if table == 'PRODUCT':

            id_info_ = self.id_info.text()
            name_info_ = self.name_info.text()
            safety_stock_ = self.safety_stock.text()

            row = (name_info_, safety_stock_, id_info_)

            command = ''' UPDATE PRODUCT SET PNAME=?,P_SAFETY_STOCK=? WHERE PNUMBER=?'''

            cursor.execute(command,row)
            
            db.commit()

        elif table == 'RAW_MATERIAL':

            id_info_ = self.id_info.text()
            name_info_ = self.name_info.text()
            safety_stock_ = self.safety_stock.text()

            row = (name_info_, safety_stock_, id_info_)

            command = ''' UPDATE RAW_MATERIAL SET MNAME=?,M_SAFETY_STOCK=? WHERE MNUMBER=?'''

            cursor.execute(command,row)
            
            db.commit()


    def DELETE(self):
        db=sqlite3.connect("inventoryDB.db")
        cursor=db.cursor()

        table = self.table_list_3.currentText()

        if table == 'PRODUCT':

            id_info_ = self.id_info.text()
            
            command= ''' DELETE FROM PRODUCT WHERE PNUMBER=? '''
            
            cursor.execute(command, [id_info_])
            
            db.commit()

        elif table == 'RAW_MATERIAL':

            id_info_ = self.id_info.text()
            
            command= ''' DELETE FROM RAW_MATERIAL WHERE MNUMBER=? '''
            
            cursor.execute(command, [id_info_]) # 這邊要使用()或[]將資料型態轉成Tuple，不然會被當成input sequence執行，就會報錯

            db.commit()

        
    def INSERT(self):

        db=sqlite3.connect("inventoryDB.db")
        cursor=db.cursor()

        table = self.table_list_3.currentText()

        if table == 'PRODUCT':

            id_info_ = int(self.id_info.text())
            name_info_ = self.name_info.text()
            safety_stock_ = self.safety_stock.text()
        
            row=(id_info_,name_info_,safety_stock_)
            
            command=''' INSERT INTO PRODUCT (PNUMBER,PNAME,P_SAFETY_STOCK) VALUES (?,?,?)'''
                    
            cursor.execute(command,row)
            
            db.commit()

        elif table == 'RAW_MATERIAL':

            id_info_ = self.id_info.text()
            name_info_ = self.name_info.text()
            safety_stock_ = self.safety_stock.text()
        
            row=(id_info_,name_info_,safety_stock_)
            
            command=''' INSERT INTO RAW_MATERIAL (MNUMBER,MNAME,M_SAFETY_STOCK) VALUES (?,?,?)'''
                    
            cursor.execute(command,row)
            
            db.commit()

    def GET_DATA_FROM_MYSQL(self):
        db_settings = {
            "host": "140.116.155.147",
            "port": "",
            "user": "2022manufacture",
            "password": "",
            "db": "2022manufacture",
            "charset": "utf8"
        }

        try:
            conn = pymysql.connect(**db_settings)
        except Exception as ex:
            print(ex)
        
        cursor = conn.cursor()

        command=''' SELECT * from 2022manufacture_product_order '''

        cursor.execute(command)

        # 取得查詢結果
        results = cursor.fetchall() # results的資料型態為tuple

        # 迭代並處理每一行
        # for row in results:
        #     print(row)

        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(("訂單編號", "客戶名子", "商品名稱", "數量", "金額", "下單時間"))
        self.table.setRowCount(0)

        for row_number, row_data in enumerate(results):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))



def main():
    
    app=QApplication(sys.argv)
    window=Main()
    window.table_list.setCurrentIndex(0) # 一進去直接顯示目前選單的table
    window.table_list_3.setCurrentIndex(0)
    window.GET_DATA()
    # window.refresh_btn.setVisible(0) # 將刷新按鈕設為隱藏
    window.show()

    app.exec_()
    

if __name__=='__main__':
    main()    