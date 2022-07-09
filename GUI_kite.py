from tkinter import *
import logging
from kiteconnect import KiteConnect
import time
# from threading import *
from tkinter import messagebox
import webbrowser
from tkinter import simpledialog
import threading
from datetime import datetime

# import math

nQuantity = 1000
ticksize = 0.05
g_Symbol = "NIFTY2271416200"

# def roundup(x,ticksize):
#     return math.ceil(x/ticksize)*ticksize
# def rounddown(x,ticksize):
#     return math.floor(x/ticksize)*ticksize
def roundtick(x):
    global ticksize
    ticksize = 0.05
    fprice = (round(x / ticksize))* ticksize
    print("Input = ", x)
    print("Output = ", fprice)

    print("Input2 = ", fprice)
    fprice = round(fprice, 2)
    print("Output2 = ", fprice)

    return fprice


def login():
    global kite

    from tkinter import messagebox as mb
    acc_tkn = ''
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.ERROR)

    key = "8gy36satr8s036hp"  # change
    secret = "xb1c9toj54oek0jn1hy6who6c3820qhg"  # change

    kite = KiteConnect(api_key=key)

    res = mb.askquestion('Generator', 'Do you want to generate access token')
    if res == 'yes':

        url = kite.login_url()

        # getting path
        chrome_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

        # First registers the new browser
        webbrowser.register('chrome', None,
                            webbrowser.BackgroundBrowser(chrome_path))
        # then call the get method to select the code
        # for new browser and call open method
        # described above
        webbrowser.get('chrome').open(url)
        # print("Login here :", kite.login_url())

        req_tkn = simpledialog.askstring(title="Login Token",
                                         prompt="Enter Login Token:")

        # req_tkn = input("Enter request token here : ")

        gen_ssn = kite.generate_session(request_token=req_tkn, api_secret=secret)

        acc_tkn = gen_ssn['access_token']

        print(acc_tkn)

        with open("access_token.txt", 'w') as at:
            # at.write(str(datetime.date()))
            # at.write("\n")
            at.write(acc_tkn)
        at.close()
    else:
        acc_tkn = open("access_token.txt", "r").read()

    kite.set_access_token(access_token=acc_tkn)
    print('Log-in successful')

def getAvgPrice(order_id):

    global kite
    global fTarget

    fAvgPrice = 0.0

    try:
        orderdetails = kite.order_history(order_id=order_id)


        for index in range(len(orderdetails)):
            if orderdetails[index]['status'] == 'COMPLETE':
                print("Average Price = ", orderdetails[index]['average_price'])
                # print(orderdetails[index]['average_price'])
                fAvgPrice = float(orderdetails[index]['average_price'])

    except Exception as e:
        print('10 Exception Occurred order_history')
        logging.info("order_history failed: {}".format(str(e)))

    return fAvgPrice

def enterOrder():
    global kite
    global order_id
    global order_id_SL

    global symbol

    global txt_NOption
    global rbCE
    global rbPE
    global txt_Quantity
    global txt_SL
    global txt_Target
    global txt_Entry
    global fTarget

    global nQuantity
    global bisCE
    global bisPE

    if bisCE == False and bisPE == False:
        messagebox.showerror("showerror", "Select CE or PE")
        return

    symbol = ""
    # nQuantity = 500
    fSL = 0.0
    fTarget = 0.0
    fTargetPoint = 0.0
    fEntry = 0.0

    symbol = txt_NOption.get()

    # Right now 100 quantity is fixed.
    if len(txt_Quantity.get()) > 0:
        nQuantity = int(txt_Quantity.get())
        if nQuantity > 1800:
            nQuantity = 1800

    if len(txt_Entry.get()) > 0:
        fEntry = float(txt_Entry.get())

    if len(txt_SL.get()) > 0:
        fSL = float(txt_SL.get())

    if len(txt_Target.get()) > 0:
        fTargetPoint = float(txt_Target.get())
        if fTargetPoint > 50:  # ToDo need to remove hardcoding
            fTargetPoint = 2

    if bisCE == True:
        symbol += "CE"

    if bisPE == True:
        symbol += "PE"

    print('Enter Order')
    # Place an order
    try:
        if fEntry == 0.0:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                        tradingsymbol=symbol,
                                        exchange=kite.EXCHANGE_NFO,
                                        transaction_type=kite.TRANSACTION_TYPE_BUY,
                                        order_type=kite.ORDER_TYPE_MARKET,
                                        quantity=nQuantity,
                                        product=kite.PRODUCT_NRML,
                                        validity=kite.VALIDITY_DAY)
        else:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                        tradingsymbol=symbol,
                                        exchange=kite.EXCHANGE_NFO,
                                        transaction_type=kite.TRANSACTION_TYPE_BUY,
                                        quantity=nQuantity,
                                        order_type=kite.ORDER_TYPE_LIMIT,
                                        product=kite.PRODUCT_NRML,
                                        validity=kite.VALIDITY_DAY,
                                        price=fEntry)

        logging.info("Order placed. ID is: {}".format(order_id))
        print('Order Placed')
    except Exception as e:
        print('1 Exception Occurred in main order')
        logging.info("Order placement failed: {}".format(str(e)))
        return

    time.sleep(1)
    # get order History to figure out SL
    # orderdetails = kite.order_history(order_id=order_id)
    # fAvgPrice = 0.0
    #
    # for index in range(len(orderdetails)):
    #     if orderdetails[index]['status'] == 'COMPLETE':
    #         print("Average Price = ", orderdetails[index]['average_price'])
    #         #print(orderdetails[index]['average_price'])
    #         fAvgPrice = float(orderdetails[index]['average_price'])
    #         fTarget = roundtick((fAvgPrice + fTargetPoint))  # round(fAvgPrice + fTargetPoint)
    #         setTradedPrice(roundtick(fAvgPrice))

        # for key in orderdetails[index]:
        #    print(orderdetails[index][key])

    fAvgPrice = 0.0

    while(1):
        fAvgPrice = getAvgPrice(order_id)
        if (fAvgPrice == 0.0):
            print('11 failed to get order average price.')
        else:
            break

    fTarget = roundtick((fAvgPrice + fTargetPoint))  # round(fAvgPrice + fTargetPoint)
    setTradedPrice(roundtick(fAvgPrice))

    if fSL == 0.0:
        fSL = fAvgPrice - 11
        fSL = roundtick(fSL)
    else:
        fSL = fAvgPrice - fSL
        fSL = roundtick(fSL)
        # Update SL to entry
        # now place SL order
    try:
        order_id_SL = kite.place_order(variety=kite.VARIETY_REGULAR,
                                       tradingsymbol=symbol,
                                       exchange=kite.EXCHANGE_NFO,
                                       transaction_type=kite.TRANSACTION_TYPE_SELL,
                                       quantity=nQuantity,
                                       order_type=kite.ORDER_TYPE_SL,
                                       product=kite.PRODUCT_NRML,
                                       validity=kite.VALIDITY_DAY,
                                       price=fSL,
                                       trigger_price=fSL + 1)
        print('SL Order Placed')
    except Exception as e:
        print('2 Exception Occurred in SL order %s \n' % str(fSL))
        logging.info("SL Order placement failed: {}".format(str(e)))

    # disableEntry()


def TargetHitexitOrder():
    global symbol
    global txt_ExitQuantity
    global txt_Exit
    global bisCE
    global bisPE
    global fTarget
    global nQuantity

    symbol = ""
    symbol = txt_NOption.get()

    if bisCE == True:
        symbol += "CE"

    if bisPE == True:
        symbol += "PE"

    # nQuantity = 500

    print('Exit Order')
    global kite
    global order_id_SL

    # Place exit target order here & cancel SL order as well
    try:
        kite.cancel_order(variety=kite.VARIETY_REGULAR, order_id=order_id_SL)
        print('SL Order cancelled')

    except Exception as e:
        print('3 Exception Occurred in cancel order')
        logging.info("Cancel SL Order failed: {}".format(str(e)))
        return

    try:
        if fTarget == 0.0:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                        tradingsymbol=symbol,
                                        exchange=kite.EXCHANGE_NFO,
                                        transaction_type=kite.TRANSACTION_TYPE_SELL,
                                        quantity=nQuantity,
                                        order_type=kite.ORDER_TYPE_MARKET,
                                        product=kite.PRODUCT_NRML,
                                        validity=kite.VALIDITY_DAY)
        else:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                        tradingsymbol=symbol,
                                        exchange=kite.EXCHANGE_NFO,
                                        transaction_type=kite.TRANSACTION_TYPE_SELL,
                                        quantity=nQuantity,
                                        order_type=kite.ORDER_TYPE_LIMIT,
                                        product=kite.PRODUCT_NRML,
                                        validity=kite.VALIDITY_DAY,
                                        price=fTarget)

        logging.info("Order placed. ID is: {}".format(order_id))
        print('Target Placed')
    except Exception as e:
        print('4 Exception Occurred in Target Order')
        logging.info("Target Order placement failed: {}".format(str(e)))

    setTradedPrice(0.0)
    fTarget = 0.0


def exitOrder():
    global symbol
    global txt_ExitQuantity
    global txt_Exit
    global bisCE
    global bisPE
    global fTarget
    global nQuantity

    symbol = ""
    symbol = txt_NOption.get()

    if bisCE == True:
        symbol += "CE"

    if bisPE == True:
        symbol += "PE"

    # nQuantity = 500
    fExit = 0.0
    if len(txt_Exit.get()) > 0:
        fExit = float(txt_Exit.get())

    if len(txt_ExitQuantity.get()) > 0:
        nTQtity = int(txt_ExitQuantity.get())
        if nQuantity > nTQtity:
            nQuantity = nTQtity

    print('Exit Order')
    global kite
    global order_id_SL

    # Place exit target order here & cancel SL order as well
    try:
        kite.cancel_order(variety=kite.VARIETY_REGULAR, order_id=order_id_SL)
        print('SL Order cancelled')

    except Exception as e:
        print('5 Exception Occurred in cancel order')
        logging.info("Cancel SL Order failed: {}".format(str(e)))
        return

    try:
        if fExit == 0.0:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                        tradingsymbol=symbol,
                                        exchange=kite.EXCHANGE_NFO,
                                        transaction_type=kite.TRANSACTION_TYPE_SELL,
                                        quantity=nQuantity,
                                        order_type=kite.ORDER_TYPE_MARKET,
                                        product=kite.PRODUCT_NRML,
                                        validity=kite.VALIDITY_DAY)
        else:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                        tradingsymbol=symbol,
                                        exchange=kite.EXCHANGE_NFO,
                                        transaction_type=kite.TRANSACTION_TYPE_SELL,
                                        quantity=nQuantity,
                                        order_type=kite.ORDER_TYPE_LIMIT,
                                        product=kite.PRODUCT_NRML,
                                        validity=kite.VALIDITY_DAY,
                                        price=fExit)

        logging.info("Order placed. ID is: {}".format(order_id))
        print('Target Placed')
    except Exception as e:
        print('6 Exception Occurred in Target Order')
        logging.info("Target Order placement failed: {}".format(str(e)))

    fTarget = 0.0
    setTradedPrice(0.0)


def setTradedPrice(fTradedPrice):
    global lbl_avgPrice
    lbl_avgPrice.config(text=str(fTradedPrice))


def selCE():
    global bisCE
    global bisPE

    bisCE = True
    bisPE = False


def selPE():
    global bisCE
    global bisPE

    bisCE = False
    bisPE = True


def startthreading():
    global txt_LTP
    global t1
    global exit_event
    exit_event = threading.Event()
    # Call work function
    t1 = threading.Thread(target=getLTP)
    t1.daemon = True
    t1.start()


def getLTP():
    global kite
    global txt_LTP
    global symbol
    global bisCE
    global bisPE
    global txt_NOption
    global txt_MTM
    global lbl_Time

    global fTarget

    global stop_LTP_threads

    ltp = 0.0

    while (1):
        try:
            symbol = txt_NOption.get()

            ltpsymbol = "NFO:" + symbol

            if bisCE == True:
                ltpsymbol += "CE"

            if bisPE == True:
                ltpsymbol += "PE"

            if bisCE == False and bisPE == False:
                ltpsymbol += "CE"

            try:
                optionltp = kite.ltp([ltpsymbol])
                ltp = optionltp[ltpsymbol]['last_price']
                txt_LTP.delete(0, END)
                txt_LTP.insert(0, str(ltp))
            except Exception as e:
                txt_LTP.delete(0, END)
                print('7 Exception Occurred in LTP order')
                # logging.info("LTP failed: {}".format(str(e)))

            if fTarget > 0.0:
                if ltp >= fTarget:
                    print("Target Hit place exit orders")
                    TargetHitexitOrder()
                    fTarget = 0.0
        except Exception as e:
            txt_LTP.delete(0, END)
            print('7.1 Exception Occurred in LTP thread')

        # fTotalMTM = 0.0
        # fTotalMTM = getMTM()
        # txt_MTM.delete(0, END)
        # txt_MTM.insert(0, str(roundtick(fTotalMTM)))

        now = datetime.now()

        #current_time = now.strftime("%H:%M:%S")
        current_time = datetime.today().strftime("%I:%M:%S  %p")
        lbl_Time.config(text=current_time)

        if stop_LTP_threads:
            return

        time.sleep(.2)


def on_closing():
    global stop_LTP_threads
    global root
    global t1
    global exit_event

    stop_LTP_threads = True
    root.destroy()


def clearAll():
    print("Clear All")
    global kite
    global order_id_SL
    # Place exit target order here & cancel SL order as well
    try:
        kite.cancel_order(variety=kite.VARIETY_REGULAR, order_id=order_id_SL)
        print('SL Order cancelled')

    except Exception as e:
        print('8 Exception Occurred in cancel order')
        logging.info("Cancel SL Order failed: {}".format(str(e)))
        return


def disableEntry():
    global rbCE
    global rbPE
    global txt_NOption
    global txt_Quantity
    global btn_Enter
    global txt_Entry

    btn_Enter["state"] = "disabled"
    rbCE["state"] = "disabled"
    rbPE["state"] = "disabled"
    txt_NOption["state"] = "disabled"
    txt_Quantity["state"] = "disabled"


def enableEntry():
    global rbCE
    global rbPE
    global txt_NOption
    global txt_Quantity
    global btn_Enter
    global txt_Entry

    btn_Enter["state"] = "normal"
    rbCE["state"] = "normal"
    rbPE["state"] = "normal"
    txt_NOption["state"] = "normal"
    txt_Quantity["state"] = "normal"


def getMTM():
    global kite

    nTotalQuantity = 0
    fTotalAvgPrice = 0.0
    fBuyvalue = 0.0
    fSellValue = 0.0
    nBuyQuantity = 0
    nSellQuantity = 0
    fCurMTM = 0.0
    fMTM = 0.0
    strCurrentSymbol = ""

    try:
        allorders = kite.orders()
    except Exception as e:
        txt_LTP.delete(0, END)
        print('9 Exception Occurred in MTM list of orders')
        logging.info("LTP failed: {}".format(str(e)))
        return
    with open("orders.txt", 'w') as ord:
        for item in allorders:
            # write each item on a new line
            if item['status'] == 'COMPLETE':
                if item['transaction_type'] == 'BUY':
                    if strCurrentSymbol == "":
                        strCurrentSymbol = item['tradingsymbol']
                        fBuyvalue = item['average_price']
                        nBuyQuantity = item['quantity']
                        # ord.write("%s\n" % item)
                        nTotalQuantity += nBuyQuantity
                        fTotalAvgPrice = fBuyvalue
                    else:
                        if strCurrentSymbol == item['tradingsymbol']:
                            fBuyvalue = item['average_price']
                            nBuyQuantity = item['quantity']

                            # ord.write("%s\n" % item)
                            fTotalAvgPrice = ((fTotalAvgPrice * nTotalQuantity) + (fBuyvalue * nBuyQuantity)) / (
                                    nTotalQuantity + nBuyQuantity)
                            nTotalQuantity += nBuyQuantity

                if item['transaction_type'] == 'SELL':
                    if strCurrentSymbol == item['tradingsymbol']:
                        fSellValue = item['average_price']
                        nSellQuantity = item['quantity']
                        # caluculate MTM
                        fCurMTM = (fSellValue - fBuyvalue) * (nSellQuantity)
                        fMTM += fCurMTM
                        ord.write("%s\t" % str(roundtick(fCurMTM)))
                        ord.write("%s\n" % str(roundtick(fMTM)))
                        nTotalQuantity -= nSellQuantity

                        if nTotalQuantity == 0:
                            strCurrentSymbol = ""
                            fBuyvalue = 0.0
                            fSellValue = 0.0
                            nBuyQuantity = 0
                            nSellQuantity = 0
                            fCurMTM = 0.0
                            fTotalAvgPrice = 0.0

    ord.close()

    return fMTM


def startUI():
    global txt_LTP
    global txt_MTM
    global kite

    global txt_NOption
    global rbCE
    global rbPE
    global txt_Quantity
    global txt_SL
    global txt_Target
    global txt_ExitQuantity
    global txt_Exit
    global txt_Entry
    global lbl_Time

    global fTarget
    global fTargetPoint

    global btn_Enter

    global stop_LTP_threads
    global root

    global bisCE
    global bisPE

    global lbl_avgPrice
    stop_LTP_threads = False

    bisCE = False
    bisPE = False
    fTarget = 0.0
    fTargetPoint = 0.0

    login()

    # create root window
    root = Tk()

    # root window title and dimension
    root.title("Kite Scalping")

    # Set geometry (widthxheight)
    root.geometry('500x350')

    lbl_NOption = Label(root, text="Nifty Option Chain")
    lbl_NOption.place(x=10, y=30, width=100, height=25)
    txt_NOption = Entry(root)
    txt_NOption.place(x=120, y=30, width=100, height=25)

    symbol = g_Symbol       #"NIFTY22JUN15800"
    txt_NOption.insert(0, symbol)

    var = IntVar()
    rbCE = Radiobutton(root, text="CE", variable=var, value=1, command=selCE)
    rbCE.place(x=250, y=30, width=30, height=25)

    rbPE = Radiobutton(root, text="PE", variable=var, value=2, command=selPE)
    rbPE.place(x=300, y=30, width=30, height=25)

    lbl_Time = Label(root, text="", borderwidth=1, relief="solid")
    lbl_Time.place(x=375, y=30, width=100, height=25)

    lbl_Quantity = Label(root, text="Quantity")
    lbl_Quantity.place(x=10, y=70, width=100, height=25)
    txt_Quantity = Entry(root)
    txt_Quantity.place(x=10, y=100, width=100, height=25)
    txt_Quantity.insert("end", str(nQuantity))
    #txt_Quantity.configure(state='readonly')

    lbl_Entry = Label(root, text="Entry")
    lbl_Entry.place(x=120, y=70, width=50, height=25)
    txt_Entry = Entry(root)
    txt_Entry.place(x=120, y=100, width=50, height=25)

    lbl_SL = Label(root, text="SL")
    lbl_SL.place(x=180, y=70, width=50, height=25)
    txt_SL = Entry(root)
    txt_SL.place(x=180, y=100, width=50, height=25)

    lbl_Target = Label(root, text="Target Points")
    lbl_Target.place(x=240, y=70, width=75, height=25)
    txt_Target = Entry(root)
    txt_Target.place(x=240, y=100, width=50, height=25)
    txt_Target.insert("end", "5")

    btn_Enter = Button(root, text="Enter Order", fg="red", command=enterOrder)
    btn_Enter.place(x=300, y=100, width=100, height=35)

    lbl_avgPrice = Label(root, text="000.00", borderwidth=1, relief="solid")
    lbl_avgPrice.place(x=420, y=100, width=75, height=25)

    lbl_LTP = Label(root, text="LTP")
    lbl_LTP.place(x=10, y=150, width=100, height=25)

    txt_LTP = Entry(root)
    txt_LTP.place(x=120, y=150, width=100, height=25)

    lbl_MTM = Label(root, text="MTM")
    lbl_MTM.place(x=200, y=150, width=100, height=25)

    txt_MTM = Entry(root)
    txt_MTM.place(x=300, y=150, width=100, height=25)
    # txt_MTM.configure(state='readonly')

    lbl_ExitQuantity = Label(root, text="Exit Quantity")
    lbl_ExitQuantity.place(x=10, y=200, width=100, height=25)
    txt_ExitQuantity = Entry(root)
    txt_ExitQuantity.place(x=10, y=230, width=100, height=25)
    txt_ExitQuantity.insert("end", str(nQuantity))
    #txt_ExitQuantity.configure(state='readonly')

    lbl_Exit = Label(root, text="Exit Price")
    lbl_Exit.place(x=150, y=200, width=50, height=25)
    txt_Exit = Entry(root)
    txt_Exit.place(x=150, y=230, width=50, height=25)

    btn_Exit = Button(root, text="Exit Order", fg="red", command=exitOrder)
    btn_Exit.place(x=230, y=220, width=100, height=35)

    btn_Exit = Button(root, text="Clear All", fg="red", command=clearAll)
    btn_Exit.place(x=10, y=275, width=100, height=35)

    mtm = 0.0
    startthreading()

    # all widgets will be here
    # Execute Tkinter
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
