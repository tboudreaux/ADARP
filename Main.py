from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import string
from tabulate import tabulate
import numpy as np


class DataMine:

    def __init__(self):
        self.arcsec = False
        self.arcmin = True
        self.degree = False
        inputs = self.initnput()
        if type(inputs['ra']) is list:
            self.mags = []
            self.devs = []
            numtargets = len(inputs['ra'])
            for i in range(numtargets):
                self.targetdata = self.websearch(inputs['ra'][i], inputs['dec'][i], inputs['rad'], inputs['vmag'][i])
                self.devs.append(self.stdev())
                self.mags.append(inputs['vmag'][i])
        else:
            self.targetdata = self.websearch(inputs['ra'], inputs['dec'], inputs['rad'], inputs['vmag'])
            self.devs = self.stdev()
            self.mags = inputs['vmag']
        if type(self.mags) is list:
            outname = raw_input('Please Enter the desired output file name: ')
            if '.' in outname:
                outfile = open(outname, 'w')
                for i in range(len(self.mags)):
                    writestring = str(self.mags[i]) + '\t' + str(self.devs[i])
                    print >>outfile, writestring
                outfile.close()
            else:
                outname += '.csv'
                outfile = open(outname, 'w')
                for i in range(len(self.mags)):
                    writestring = str(self.mags[i]) + '\t' + str(self.devs[i])
                    print >>outfile, writestring
                outfile.close()
        else:
            outname = raw_input('Please Enter the desired output file name: ')
            if '.' in outname:
                outfile = open(outname, 'w')
                writestring = str(self.mags) + '\t' + str(self.devs)
                print >>outfile, writestring
                outfile.close()
            else:
                outname += '.csv'
                outfile = open(outname, 'w')
                writestring = str(self.mags) + '\t' + str(self.devs)
                print >>outfile, writestring
                outfile.close()

    def initnput(self):
        cont = False

        while cont is False:
            UserRad = raw_input("Please Enter Radius in degrees: ")
            if "arcsec" in UserRad or "as" in UserRad:
                self.arcsec = True
                self.arcmin = False
                self.degree = False
                cont = True
            elif "arcmin" in UserRad or "am" in UserRad:
                cont = True
            elif "degree" in UserRad or "d" in UserRad:
                self.degree = True
                self.arcmin = False
                self.arcsec = False
                cont = True
            else:
                print "Please spesify units for radius, arcmin, arcsec, or degree "
        cont = False
        while cont is False:
            UseFile = raw_input('Would you like to use a target file[Y/n]: ')
            if UseFile == 'Y' or UseFile == 'y':
                ApproxMag = []
                filepath = raw_input('Please enter path to file: ')
                targetfile = open(filepath, 'rb')
                targetfile = targetfile.readlines()
                targetfile = [x.rsplit() for x in targetfile]
                names = [x[0] for x in targetfile]
                ra = [x[1] for x in targetfile]
                dec = [x[2] for x in targetfile]
                UMag = [x[4] for x in targetfile]
                BMag = [x[5] for x in targetfile]
                VMag = [x[6] for x in targetfile]
                for i in range(len(VMag)):
                    if VMag[i] is '-' and BMag[i] is not '-':
                        ApproxMag.append(BMag[i])
                    elif VMag[i] is '-' and BMag[i] is '-' and UMag[i] is not '-':
                        ApproxMag.append(UMag[i])
                    elif VMag[i] is '-' and BMag[i] is '-' and UMag[i] is '-':
                        ApproxMag.append(10)
                cont = True
            elif UseFile == 'N' or UseFile == 'n':
                ra = raw_input("Please Enter the RA of the target: ")
                dec = raw_input("Please Enter the Declination of the target: ")
                ApproxMag = raw_input("Please Enter the Approximate V-mag: ")
                cont = True
            else:
                print 'Please enter either Y or n!'
                cont = False
        transtable = string.maketrans('','')
        nodigs = transtable.translate(transtable, string.digits)
        UserRad = UserRad.translate(transtable, nodigs)
        return {'ra': ra, 'dec': dec, 'rad': UserRad, 'vmag': ApproxMag}

    def websearch(self, ra, dec, rad, vmag):
        DebugMode = False
        if DebugMode is not True:
            dates = []
            exp1 = []
            exp2 = []
            exp3 = []
            exp4 = []
            exp5 = []
            err1 = []
            err2 = []
            err3 = []
            err4 = []
            err5 = []
            coords = ra + ' ' + dec
            print coords
            driver = webdriver.Firefox()
            driver.get("http://www.astrouw.edu.pl/asas/?page=acvs")
            if self.arcmin is True:
                driver.find_element_by_id("id_umin").click()
            elif self.arcsec is True:
                driver.find_element_by_id("id_usec").click()
            elif self.degree is True:
                driver.find_element_by_id("id_udeg").click()
            else:
                print "An unkown error has occured, please re run the program, thank you"
            driver.find_element_by_id("id_qall").click()
            coords = driver.find_element_by_id("id_main")
            coords.send_keys(coords)
            Radius = driver.find_element_by_id("id_rad")
            Radius.send_keys(Keys.BACK_SPACE)
            Radius.send_keys(str(rad))
            try:
                coords.send_keys(Keys.RETURN)
                pagetext = driver.find_element_by_xpath("//div[@id='dmain']/h1").text
                pagetext = pagetext.rsplit()
                if pagetext[-2] == 'no':
                    driver.quit()
                    return "//NRO" # No Returned Objects
                elif pagetext[-2].isdigit() is True:
                    number = int(pagetext[-2])
                    ids = [None] * number
                    mags = [None] * number
                    numobs = [None] * number
                else:
                    driver.quit()
                    print "An unkown error has occurred, please re run the program, thank you"
                    return "//EIT" # Error in Title
                targetdata = np.empty(number)

                table = driver.find_element_by_xpath("//table[1]").text
                table = table.rsplit()
                for i in range(number):
                    ids[i] = [table[19+10*i]]
                    mags[i] = [table[24+10*i]]
                index = min(range(len(mags)), key=lambda i: abs(mags[i]-vmag))
                iduse = ids[index]
                driver.get("http://www.astrouw.edu.pl/cgi-asas/asas_cgi_get_data?"+iduse+",asas3")
                data = driver.find_element_by_xpath("//pre").text
                data = data.split("\n")
                data = [x for x in data if not x.startswith('#')]
                numobs = len(data)
                for j in range(numobs):
                    data[i] = data[i].rsplit()
                driver.quit()
                for j in range(numobs):
                    dates.append(data[i][0])
                    exp1.append(data[i][1])
                    exp2.append(data[i][2])
                    exp3.append(data[i][3])
                    exp4.append(data[i][4])
                    exp5.append(data[i][5])
                    err1.append(data[i][6])
                    err2.append(data[i][7])
                    err3.append(data[i][8])
                    err4.append(data[i][9])
                    err5.append(data[i][10])
                dates = np.asarray(dates, dtype='f')
                exp1 = np.asarray(exp1, dtype='f')
                exp2 = np.asarray(exp2, dtype='f')
                exp3 = np.asarray(exp3, dtype='f')
                exp4 = np.asarray(exp4, dtype='f')
                exp5 = np.asarray(exp5, dtype='f')
                err1 = np.asarray(err1, dtype='f')
                err2 = np.asarray(err2, dtype='f')
                err3 = np.asarray(err3, dtype='f')
                err4 = np.asarray(err4, dtype='f')
                err5 = np.asarray(err5, dtype='f')
                targetdata = np.stack((dates, exp1, exp2, exp3, exp4, exp5, err1, err2, err3, err4, err5))
                return targetdata
            except NoSuchElementException:
                driver.quit()
                print 'An Unknown Error has occurred, the server is possibly down, try going to the website in a ' \
                      'browser and manually search for a star, if that works then just re run.'
                exit()
        else:
            dates = np.array([1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009])
            exp1 = np.array([11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 12])
            exp2 = np.array([11.11, 11.23, 11.29, 11.37, 11.51, 11.6, 11.78, 11.8, 11.91, 11.9])
            exp3 = np.array([11.12, 11.2, 11.31, 11.37, 11.5, 11.62, 11.79, 11.81, 11.91, 12.1])
            exp4 = np.array([11.11, 11.23, 11.29, 11.37, 11.51, 11.6, 11.78, 11.8, 11.91, 11.9])
            exp5 = np.array([11, 11, 11, 11, 11, 11, 11, 11, 11, 11])
            err1 = np.array([0.1, 0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.3, 0.1, 0.1])
            err2 = np.array([0.1, 0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.3, 0.1, 0.1])
            err3 = np.array([0.1, 0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.3, 0.1, 0.1])
            err4 = np.array([0.1, 0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.3, 0.1, 0.1])
            err5 = np.array([0.1, 0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.3, 0.1, 0.1])
            targetdata = np.stack((dates, exp1, exp2, exp3, exp4, exp5, err1, err2, err3, err4, err5))
            return targetdata

    def stdev(self):
        print tabulate(self.targetdata)
        epndev = np.empty(len(self.targetdata[0]))
        for i in range(len(self.targetdata[0])):
            epn = np.empty(5)
            for j in range(5):
                epn[j] = self.targetdata[j+1][0]
            epndev[i] = np.std(epn)
        avgepndev = sum(epndev)/len(epndev)
        return avgepndev

if __name__ == "__main__":
    DataMine()
    print "Code Complete"
