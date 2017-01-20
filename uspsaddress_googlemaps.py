import csv
import googlemaps
import time # for sleep()
from pygeocoder import Geocoder
from urllib import urlopen
import thread
import json
from noisegen import noisegen
import random
import usaddress
import itertools
"""
from uspsaddress_googlemaps import uspsaddress_googlemaps
usadd = uspsaddress_googlemaps()
usadd.eval_googlemaps()
"""

class uspsaddress_googlemaps(object):
    isverbose = True

    ng = noisegen()
    error_rate = 0.1

    googlemaps_sleep = 0.1
    geocoder_us_sleep = 0
    data_science_toolkit_sleep = 0

    gmaps = googlemaps.Client(key='AIzaSyBOit9CjPZ7KB_sDtKYxz6UN7qr-RRxZ1k')

    time_stamp = time.time()

    log_file = open("uspsaddress"+str(time_stamp)+".log", "w") if isverbose==True else []

    usps_headers = ['street_num', 'street_pre_dir', 'street_name', 'street_suffix', 'street_post_dir',
                    'unit_type', 'unit_num', 'city', 'state_abbrev', 'zip', 'zip4']

    usps_po_box_headers = ['street_pre_dir', 'street_name', 'street_num', 'street_suffix',  \
                           'street_post_dir', 'unit_type', 'unit_num', 'city', 'state_abbrev', \
                           'zip', 'zip4']

    googlemaps_headers = ['street_number', 'route', 'locality', 'neighborhood', \
                          'administrative_area_level_1', 'postal_code',  'postal_code_suffix']

    headers_googlemaps2usps = {'postal_code':'zip', 'postal_code_suffix':'zip4',
                               'locality':'city', 'neighborhood':'city',
                               'administrative_area_level_1':'state_abbrev', \
                               'street_number':'street_num', 'subpremise':'unit_num'}

    geocoder_us_headers = ['city', 'zip', 'state', 'number', 'long', 'prefix', 'street', 'lat', 'type']

    headers_geocoder_us2usps = {'city':'city', 'zip':'zip', 'state':'state_abbrev', 'number':'street_num',
                                'prefix':'street_pre_dir', 'street':'street_name',  'type':'street_suffix'}

    headers_usaddress2usps = {'ZipCode':'zip', 'ZipPlus4':'zip4','PlaceName':'city',
                                 'StreetNamePreDirectional':'street_pre_dir', 'StateName':'state_abbrev',
                                 'StreetNamePostDirectional': 'street_post_dir',
                                 'USPSBoxID':'street_num', 'AddressNumber':'street_num',
                                 'USPSBoxType':'street_name', 'StreetName':'street_name',
                                 'StreetNamePostType':'street_suffix',
                                 'OccupancyType':'unit_type','OccupancyIdentifier':'unit_num'}

    def __init__(self):
        """
        Constructor

        >>> from uspsaddress import uspsaddress
        >>> usadd = uspsaddress()
        """
        if self.isverbose:
            print >> self.log_file, "In 'uspsaddress_googlemaps' class"


    def print_record(self, row):
        """

        >>> from uspsaddress_googlemap import uspsaddress_googlemap
        >>> usadd = uspsaddress_googlemap()
        >>> s = usadd.print_record({'street_num': "55", 'street_pre_dir': "N"})
        street_num : 55
        street_pre_dir : N
        <BLANKLINE>
        """
        if self.isverbose==False:
            return

        s = ""
        for k,v in row.iteritems():
            if len(v) > 0:
                try:
                    if isinstance(v, (list)) and len(v) > 1:
                        v = list(itertools.chain(*v)) # flatten list of lists into 1 list. # Ref: http://tinyurl.com/2uveqgr
                        v = list(itertools.chain(*v))
                        v = list(itertools.chain(*v))
                        v = list(itertools.chain(*v))
                        v = list(itertools.chain(*v))
                        v2 = u' '.join((elmt for elmt in v)).encode('utf-8')
                    else:
                        v2 = v
                    s = u' '.join((s, k,":", v2, "\n")).encode('utf-8').strip()
                    #s += (  str(k) + " : " + str(v) + "\n" )
                except ValueError:
                    print  "Not sure how to handle..."

        return s


    def map_googlemaps_result(self, result):
        """
        >>> 1 + 1
        2

        """
        row2 = {}
        for h in self.usps_headers:
            row2[h] = ""

        if len(result) == 0:
            return {}

        for i in range(len(result[0]['address_components'])):
            header2 = result[0]['address_components'][i]['types'][0]
            if not header2 == None:
                header2 = header2.strip()
            value2 = result[0]['address_components'][i]['short_name']
            if not value2 == None:
                value2 = value2.strip()
            if self.isverbose:
                if isinstance(value2, type(None)):
                    value2 = ""
                print >> self.log_file, u' '.join((header2,":", value2)).encode('utf-8').strip()

            if not(header2 in ['route', 'country']):
                if not header2 in self.headers_googlemaps2usps.keys():
                    print >> self.log_file, "WARN: ", header2, " not in headers_googlemaps2usps"
                    continue

                usps_header = self.headers_googlemaps2usps[header2]
                row2[usps_header] = value2
            elif header2 == 'route' and len(value2)>0:
                s = value2.split()
                s_len = len(s)
                idx = s_len - 1
                if (s_len > 2) and (s[0].upper() in ["N", "S", "E", "W", "NORTH", "SOUTH","EAST","WEST"]):
                    row2['street_pre_dir'] = s[0][0]
                    row2['street_name'] = " ".join(s[1:idx])
                else:
                    row2['street_name'] = " ".join(s[0:idx])

                row2['street_suffix'] = s[idx]
                if s[idx].upper() == "ROAD":
                    row2['street_suffix'] = "RD"
                elif s[idx].upper() == "LANE":
                    row2['street_suffix'] = "LN"
                elif s[idx].upper() in ["AVE","AV"]:
                    row2['street_suffix'] = "AVE"
                elif s[idx].upper() in ["TRAIL"]:
                    row2['street_suffix'] = "TRL"
                elif s[idx].upper() in ["ACRES"]:
                    row2['street_name'] += s[idx]
            """elif header2 == 'locality':
                if len(row2['city']) > 0:  # non empty value
                    print >> self.log_file, "===WARN: ", row2['city']
                    continue
            """

        print >> self.log_file, "\nMapped result:\n", row2, "\n"
        s = self.print_record(row2)
        if self.isverbose:
            print >> self.log_file, s
        return row2

    def map_geocoder_us_result(self, result):
        """
        >>> 1 + 1
        2

        """
        row2 = {}
        for h in self.usps_headers:
            row2[h] = ""

        for header2, value2 in result.iteritems():
            if self.isverbose:
                print >> self.log_file, header2, ":", value2

            if not(header2 in ['']):
                if not header2 in self.headers_geocoder_us2usps.keys():
                    print >> self.log_file, "WARN: ", header2, " not in headers_geocoder_us2usps"
                    continue

                usps_header = self.headers_geocoder_us2usps[header2]
                row2[usps_header] = value2

                if header2 == "type":
                    if value2.upper() == "PKY":
                        row2[usps_header] = "PKWY"

        print >> self.log_file, "\nMapped result:\n", row2, "\n"
        s = self.print_record(row2)
        if self.isverbose:
            print >> self.log_file, s
        return row2


    def map_usaddress_result(self, result):
        # self.map_usaddress_record(result)
        row2 = {}
        for h in self.usps_headers:
            row2[h] = ""

        for elmt in result:
            header2 = elmt[1]
            value2 = elmt[0]
            if not(header2 in ['PlaceName', 'USPSBoxType', 'StreetName','OccupancyIdentifier']):
                if not header2 in self.headers_usaddress2usps.keys():
                    print >> self.log_file, "ERROR: ", header2, " not in headers_usaddress2usps"
                    #TODO Follow up on fields such as 'AddressNumberSuffix'
                    continue

                usps_header = self.headers_usaddress2usps[header2]
                row2[usps_header] = value2
            elif header2 == 'PlaceName':
                    row2['city'] += (" " + value2)
                    row2['city'] = row2['city'].strip()
            elif header2 in ['USPSBoxType', 'StreetName']:
                row2['street_name'] += (" " + value2)
                row2['street_name'] = row2['street_name'].strip()
            elif header2 in ['OccupancyIdentifier']:
                if row2['unit_num'] == "":
                    row2['unit_num'] = value2
                else:
                    row2['unit_num'] = [row2['unit_num'], value2]

        print >> self.log_file, "Mapped result:\n", row2, "\n"
        s = self.print_record(row2)
        if self.isverbose:
            print >> self.log_file, s
        return row2


    def compare2records(self, row1, row2, wrong_counts, right_counts):
        right_count = 0.0
        wrong_count = 0.0
        count = 0

        if len(row2) == 0:
            row2 ={}
            for k,v in row1.iteritems():
                row2[k] = ""

        for (h,v) in row1.iteritems():
            count += 1

            if not isinstance(row2[h], list):
                #print row2[h], len(row2[h])
                if v.upper() == row2[h].upper():
                    val = 1.0
                    right_counts[h] += val
                    right_count += val
                else:
                    if self.isverbose:
                        if isinstance(v,(list)) and len(v) > 1:
                            v2 = u' '.join((elmt for elmt in v if len(v) > 1 )).encode('utf-8').strip()
                        else:
                            v2 = v
                        print >> self.log_file, u' '.join(("Mismatched field: ", h, ". Values: usps : ",  v2 , ", parsed : ", row2[h])).encode('utf-8').strip()
                        #"Mismatched field: ", h, ". Values: usps : ", v, ", parsed : ", row2[h]
                    wrong_counts[h] += 1
            else:
                for elmt in row2[h]:
                    if v.upper() == elmt:
                        val = (1.0/len(row2[h]))
                        right_counts[h] += val
                        right_count += val
                        continue
                    else:
                        if self.isverbose:
                            try:
                                if isinstance(v,(list)) and len(v) > 1:
                                    v = list(itertools.chain(*v))
                                    v = list(itertools.chain(*v))
                                    v2 = u' '.join((elmt for elmt in v if len(v) > 1 )).encode('utf-8').strip()
                                else:
                                    v2 = v
                                if isinstance(row2[h],(list)) and len(row2[h]) > 1:
                                    rw2 = list(itertools.chain(*row2[h]))
                                    rw2 = list(itertools.chain(*rw2))
                                    rw2 = list(itertools.chain(*rw2))
                                    rw2 = list(itertools.chain(*rw2))
                                    rw2 = list(itertools.chain(*rw2))
                                    r2 = u' '.join((elmt for elmt in rw2 if len(rw2) > 1 )).encode('utf-8').strip()
                                else:
                                    r2 = row2[h]
                            except ValueError:
                                print >> self.log_file, "Not sur ehow to handle"
                            print >> self.log_file,  u' '.join(("Mismatched field: ", h, ". Values: usps : ",   v2, ", parsed : ", r2)).encode('utf-8').strip()

                wrong_counts[h] += (1.0 - (1.0/len(row2[h])))

        wrong_count = count - right_count

        if self.isverbose:
             print >> self.log_file, "\nRight and wrong counts:", right_count, wrong_count
             if (right_count + wrong_count) > 0:
                 accuracy = right_count * 1.0/ (right_count+wrong_count)
                 print >> self.log_file, "\nAccuracy:", accuracy
                 if accuracy < 1.0:
                     print >> self.log_file, "***REVIEW***"

        return right_count, wrong_count, wrong_counts


    def usps_csv_row2_dict_and_address_line(self, row, exclude_fields=[]):
        row1 = {}
        address_line = ""

        if row['street_name'].upper() == "PO BOX":
            for h in self.usps_po_box_headers:
                if len(row[h].strip()) > 0 and not (h  in exclude_fields):
                    address_line += (row[h] + " ")
                    row1[h] = row[h]
        else:
            for h in self.usps_headers:
                if len(row[h].strip()) > 0 and not (h  in exclude_fields):
                    address_line += (row[h] + " ")
                    row1[h] = row[h]

        if self.isverbose:
            s = self.print_record(row1)
            print >> self.log_file, s, "\nInput address line:", address_line,"\n"

        return address_line, row1


    def googlemaps_parse_address_line(self, address_line="", wrong_counts={}, method=1):
        ifsuccess = False
        result = {}
        if address_line=="":
            wrong_counts['no_input'] += 1
            return ifsuccess, result, wrong_counts

        try:
            if method == 1:
                result =  self.gmaps.geocode(address_line)
            elif method == 2:
                result = Geocoder.geocode(address_line)
                result = result.raw;
            elif method == 3:
                url = 'http://maps.googleapis.com/maps/api/geocode/json?sensor=false&address=' \
                      + address_line.strip().replace(' ','+')
                if self.isverbose: print >> self.log_file, url
                con = urlopen(url)
                data = con.read()
                con.close()
                #print data
                status_result = json.loads(data)
                #status = status_result['status']
                result = status_result['results']

            ifsuccess = True
            time.sleep(self.googlemaps_sleep)
        except:
            print >> self.log_file, "ERROR: timeout"
            wrong_counts['timeout'] += 1
            return ifsuccess, result, wrong_counts

        if len(result) == 0:
            if not 'no_parsed_result' in wrong_counts.keys():
                wrong_counts['no_parsed_result'] = 0
            wrong_counts['no_parsed_result'] += 1
            msg = " ".join(["ERROR: len(result) == 0:\t", address_line, "\n"])
            print >> self.log_file, msg

        if self.isverbose:
            print >> self.log_file, "Parsed result:\n",result,"\n"

        return ifsuccess, result, wrong_counts


    def geocoder_us_parse_address_line(self, address_line="", wrong_counts={}):
        ifsuccess = False
        result = {}
        if address_line=="":
            wrong_counts['no_input'] += 1
            return ifsuccess, result, wrong_counts

        try:
            #url = 'http://rpc.geocoder.us/service/namedcsv?address=' + \
            url = 'http://206.220.230.164/service/namedcsv?address=' + \
                    address_line.strip().replace(' ','+') + "&parse_address=1"
            con = urlopen(url)
            data = con.read()
            con.close()

            parts = data.split(',')
            for i in range(len(parts)):
                k_v = parts[i].split('=')
                if (len(k_v)>1) and (len(k_v[1]) > 0):
                    newline_pos = k_v[0].find('\n')
                    if newline_pos > -1:
                        key = k_v[0][newline_pos+1:].strip()
                    else:
                        key = k_v[0].strip()

                    value = k_v[1].strip()
                    result[key] = value

            if self.isverbose: print >> self.log_file, url, "\n"
            #print result

            if 'error' in result.keys():
                if result['error'] == "2: couldn't find this address! sorry":
                    wrong_counts['notfound'] += 1
                    ifsuccess = True
                else:
                    print >> self.log_file, "ERROR: ", result['error'], 'to be added to wrong_counts'
                    if not 'error' in wrong_counts.keys():
                        wrong_counts['error'] = 0
                    wrong_counts['error'] += 1
                    ifsuccess = False
            else:
                ifsuccess = True

            time.sleep(self.geocoder_us_sleep)
        except:
            print >> self.log_file, "ERROR: timeout"
            wrong_counts['timeout'] += 1
            return ifsuccess, result, wrong_counts

        if len(result) == 0:
            if not 'no_parsed_result' in wrong_counts.keys():
                wrong_counts['no_parsed_result'] = 0
            wrong_counts['no_parsed_result'] += 1
            msg = " ".join(["ERROR: len(result) == 0:\t", address_line, "\n"])
            print >> self.log_file, msg

        if self.isverbose:
            print >> self.log_file, "Parsed result:\n",result,"\n"

        return ifsuccess, result, wrong_counts

    def data_science_toolkit_parse_address_line(self, address_line="", wrong_counts={}):
        ifsuccess = False
        result = {}
        if address_line=="":
            wrong_counts['no_input'] += 1
            return ifsuccess, result, wrong_counts

        try:
            url = 'http://www.datasciencetoolkit.org/maps/api/geocode/json?sensor=false&address=' \
                  + address_line.strip().replace(' ','+')
            con = urlopen(url)
            data = con.read()
            con.close()
            status_result =  json.loads(data) # decode JSON
            status = status_result['status']
            result = status_result['results']
            if self.isverbose:  print >> self.log_file, url, "\n"
            #print result

            if not status == "OK":
                ifsuccess = False
                if not 'notfound' in wrong_counts.keys():
                    wrong_counts['notfound'] = 0
                wrong_counts['notfound'] += 1
            else:
                ifsuccess = True

            time.sleep(self.data_science_toolkit_sleep)
        except:
            print >> self.log_file, "ERROR: timeout"
            wrong_counts['timeout'] += 1
            return ifsuccess, result, wrong_counts

        if len(result) == 0:
            wrong_counts['notfound'] += 1
            msg = " ".join(["ERROR: len(result) == 0:\t", address_line, "\n"])
            print >> self.log_file, msg

        if self.isverbose:
            print >> self.log_file, "Parsed result:\n",result,"\n"

        return ifsuccess, result, wrong_counts


    def update_counts(self, total_right_count, total_wrong_count, right_count, wrong_count, id):
        total_wrong_count += wrong_count
        total_right_count += right_count
        total_counts = total_right_count + total_wrong_count
        accuracy = total_right_count * 1.0 / (max(1,total_right_count + total_wrong_count))
        s = "****" + ", ".join([str(id), str(right_count), str(wrong_count), \
                                str(total_right_count), str(total_wrong_count), str(accuracy)])
        if self.isverbose:
            print >> self.log_file,  s
        print s

        return total_right_count, total_wrong_count


    def initalize_counts_dict(self):
        wrong_counts = {}
        for h in self.usps_headers:
            wrong_counts[h] = 0
        wrong_counts['timeout'] = 0
        wrong_counts['no_input'] = 0
        wrong_counts['notfound'] = 0
        #print wrong_counts
        return wrong_counts


    def print_counts(self, wrong_counts, right_counts):
        wrong_counts_str = "".join(["\nwrong counts: \n", str(wrong_counts)])
        print >> self.log_file, wrong_counts_str
        print wrong_counts_str

        right_counts_str = "".join(["\nright counts: \n", str(right_counts)])
        print >> self.log_file, right_counts_str
        print right_counts_str


    def print_total_counts(self, total_right_count, total_wrong_count):
        s = "****" + ", ".join([str(total_right_count), str(total_wrong_count), \
                                str(total_right_count * 1.0 / (
                                max(1.0, total_wrong_count + total_right_count)))])
        if self.isverbose:
            print >> self.log_file, s
            print s

    def perturb_address_line(self, address_line):
        r = random.random()
        if r <= self.error_rate:
            k = random.randint(0, 3) + 1  # in [1,4]
            if self.isverbose: print >> self.log_file, "k = %s" % (k)
            for k_ind in xrange(k):
                t = random.randint(0, 5) + 1  # in [1,6]
                old_address_line = address_line
                address_line = self.ng.call_method(t, address_line, 1)
                if self.isverbose:  print >> self.log_file, \
                    "t = %s,  %s    =>     %s" % (t, old_address_line, address_line)

            if self.isverbose: print >> self.log_file, " "
        return address_line

    def eval_googlemaps(self, n=20000, method=1, g=0):
        """
        162 PENDEXTER AVE CHICOPEE MA 01013 2126
        216 E HILL RD BRIMFIELD MA 01010 9799

        >>> from uspsaddress_googlemaps import uspsaddress_googlemaps
        >>> usadd = uspsaddress_googlemaps()
        >>> usadd.eval_googlemaps(1)
        ****1, 6.0, 0.0, 6.0, 0.0, 1.0
        wrong counts:
        {'city': 0, 'unit_num': 0, 'no_input': 0, 'street_post_dir': 0, 'zip': 0, 'street_name': 0, 'street_pre_dir': 0, 'street_suffix': 0, 'unit_type': 0, 'state_abbrev': 0, 'timeout': 0, 'street_num': 0, 'zip4': 0}

        """

        inputfile = "../../Data/samplefordatalinkage.csv"
        #inputfile =  "../../Data/test.csv"
        wrong_counts = self.initalize_counts_dict()
        right_counts = self.initalize_counts_dict()
        total_wrong_count = 0
        total_right_count = 0
        row_count = 0

        if self.isverbose:
            print >> self.log_file, "In eval_googlemaps: n = ", str(n), "method = ", method
            if g>0: print >> self.log_file, "error rate = ", self.error_rate

        with open(inputfile, "rb") as f:
            reader = csv.DictReader(f);
            for row in reader:
                row_count += 1
                if row_count <= n:
                    if self.isverbose:
                        print >> self.log_file, \
                            "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", row_count
                else:
                    break

                total_right_count, total_wrong_count, wrong_counts, row2, ifscuccess = self.eval_googlemaps_row(f, g, method,
                   right_counts, row, row_count, total_right_count, total_wrong_count, wrong_counts)

        print "\n\n=================================================GoogleMap n = %s, g = %s, error_rate = %s" % (n,g,self.error_rate)
        print >> self.log_file, "\n\n=================================================GoogleMap n = %s, g = %s, error_rate = %s" % (n,g,self.error_rate)
        self.print_counts(wrong_counts, right_counts)
        self.print_total_counts(total_right_count, total_wrong_count)

        f.close()
        self.log_file.close()


    def eval_googlemaps_row(self, f, g, method, right_counts, row, row_count, total_right_count, total_wrong_count,
                            wrong_counts):
        address_line, row1 = self.usps_csv_row2_dict_and_address_line(row)
        # introduce noise and errors
        old_address_line = address_line
        if g == 1:
            address_line = self.perturb_address_line(address_line)
        ifsuccess, result, wrong_counts = \
            self.googlemaps_parse_address_line(address_line, wrong_counts, method)
        row2 = {}
        if ifsuccess:
            row2 = self.map_googlemaps_result(result)
            right_count, wrong_count, wrong_counts = \
                self.compare2records(row1, row2, wrong_counts, right_counts)
            total_right_count, total_wrong_count = \
                self.update_counts(total_right_count, total_wrong_count,
                                   right_count, wrong_count, row_count)
        if not ifsuccess:
            if wrong_counts['timeout'] > 10000:
                self.print_counts(wrong_counts, right_counts)
                self.print_total_counts(total_right_count, total_wrong_count)
                f.close()
                # return
            # else:
            # continue

        return total_right_count, total_wrong_count, wrong_counts, row2, ifsuccess


    def eval_geocoder_us(self, n=20000, g=0):
        """
        162 PENDEXTER AVE CHICOPEE MA 01013 2126
        216 E HILL RD BRIMFIELD MA 01010 9799


        >>> from uspsaddress_googlemaps import uspsaddress_googlemaps
        >>> usadd = eval_geocoder_us()
        >>> usadd.eval_geocoder_us(1)
        ****1, 6.0, 0.0, 6.0, 0.0, 1.0
        wrong counts:
        {'city': 0, 'unit_num': 0, 'no_input': 0, 'street_post_dir': 0, 'zip': 0, 'street_name': 0, 'street_pre_dir':
         0, 'street_suffix': 0, 'unit_type': 0, 'state_abbrev': 0, 'timeout': 0, 'street_num': 0, 'zip4': 0}

        """
        inputfile = "../../Data/samplefordatalinkage.csv"
        #inputfile =  "../../Data/test.csv"
        wrong_counts = self.initalize_counts_dict()
        right_counts = self.initalize_counts_dict()
        total_wrong_count = 0
        total_right_count = 0
        row_count = 0

        if self.isverbose:
            print >> self.log_file, "In eval_geocoder_us: n = ", str(n)
            if g>0: print >> self.log_file, "error rate = ", self.error_rate

        with open(inputfile, "rb") as f:
            reader = csv.DictReader(f);
            for row in reader:
                row_count += 1
                if row_count <= n:
                    if self.isverbose:
                        print >> self.log_file, \
                            "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", row_count
                else:
                    break

                total_right_count, total_wrong_count, wrong_counts, row2, ifsuccess = \
                    self.eval_geocoder_us_row(f, g, right_counts, row, row_count, \
                         total_right_count, total_wrong_count, wrong_counts)


        print "\n\n=================================================GeoCoder n = %s, g = %s, error_rate = %s" % (n,g,self.error_rate)
        print >> self.log_file, "\n\n=================================================GeoCoder n = %s, g = %s, error_rate = %s" % (n,g,self.error_rate)
        self.print_counts(wrong_counts, right_counts)
        self.print_total_counts(total_right_count, total_wrong_count)

        f.close()
        self.log_file.close()

    def eval_geocoder_us_row(self, f, g, right_counts, row, row_count, total_right_count, total_wrong_count,
                            wrong_counts):
        # exclude zip4 or the service will not work
        address_line, row1 = self.usps_csv_row2_dict_and_address_line(row, ['zip4'])
        # introduce noise and errors
        old_address_line = address_line
        if g == 1:
            address_line = self.perturb_address_line(address_line)
        ifsuccess, result, wrong_counts = \
            self.geocoder_us_parse_address_line(address_line, wrong_counts)
        row2 = {}
        if ifsuccess:
            row2 = self.map_geocoder_us_result(result)
            right_count, wrong_count, wrong_counts = \
                self.compare2records(row1, row2, wrong_counts, right_counts)
            total_right_count, total_wrong_count = \
                self.update_counts(total_right_count, total_wrong_count,
                                   right_count, wrong_count, row_count)
        if not ifsuccess:
            if wrong_counts['timeout'] > 2:
                self.print_counts(wrong_counts, right_counts)
                self.print_total_counts(total_right_count, total_wrong_count)
                f.close()
                # return
            # else:
                # continue
        return total_right_count, total_wrong_count, wrong_counts, row2, ifsuccess


    def eval_data_science_toolkit(self, n=20000, g=0):
        """
        162 PENDEXTER AVE CHICOPEE MA 01013 2126
        216 E HILL RD BRIMFIELD MA 01010 9799


        >>> from uspsaddress_googlemaps import uspsaddress_googlemaps
        >>> usadd = uspsaddress_googlemaps()
        >>> usadd.eval_data_science_toolkit(1)
        ****1, 6.0, 0.0, 6.0, 0.0, 1.0
        wrong counts:
        {'city': 0, 'unit_num': 0, 'no_input': 0, 'street_post_dir': 0, 'zip': 0, 'street_name': 0, 'street_pre_dir': 0, 'street_suffix': 0, 'unit_type': 0, 'state_abbrev': 0, 'timeout': 0, 'street_num': 0, 'zip4': 0}

        """
        inputfile = "../../Data/samplefordatalinkage.csv"
        #inputfile =  "../../Data/test.csv"
        wrong_counts = self.initalize_counts_dict()
        right_counts = self.initalize_counts_dict()
        total_wrong_count = 0
        total_right_count = 0
        row_count = 0

        if self.isverbose:
            print >> self.log_file, "In eval_data_science_toolkit: n = ", str(n)
            if g>0: print >> self.log_file, "error rate = ", self.error_rate

        with open(inputfile, "rb") as f:
            reader = csv.DictReader(f);
            for row in reader:
                row_count += 1
                if row_count <= n:
                    if self.isverbose:
                        print >> self.log_file, \
                            "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", row_count
                else:
                    break

                total_right_count, total_wrong_count, wrong_counts, row2, ifsuccess = \
                    self.eval_data_sceince_toolkit_row(f, g, right_counts, row, row_count,\
                             total_right_count, total_wrong_count, wrong_counts)

        print "\n\n=================================================Data Science Toolkit n = %s, g = %s, error_rate = %s" % (n,g,self.error_rate)
        print >> self.log_file, "\n\n=================================================Data Science Toolkit n = %s, g = %s, error_rate = %s" % (n,g,self.error_rate)
        self.print_counts(wrong_counts, right_counts)
        self.print_total_counts(total_right_count, total_wrong_count)

        f.close()
        self.log_file.close()

    def eval_data_sceince_toolkit_row(self, f, g, right_counts, row, row_count, total_right_count, total_wrong_count,
                                      wrong_counts):
        address_line, row1 = self.usps_csv_row2_dict_and_address_line(row, ['zip4'])
        # introduce noise and errors
        old_address_line = address_line
        if g == 1:
            address_line = self.perturb_address_line(address_line)
        ifsuccess, result, wrong_counts = \
            self.data_science_toolkit_parse_address_line(address_line, wrong_counts)
        row2 = {}
        if ifsuccess:
            row2 = self.map_googlemaps_result(result)
            right_count, wrong_count, wrong_counts = \
                self.compare2records(row1, row2, wrong_counts, right_counts)
            total_right_count, total_wrong_count = \
                self.update_counts(total_right_count, total_wrong_count,
                                   right_count, wrong_count, row_count)
        if not ifsuccess:
            if wrong_counts['timeout'] > 200:
                self.print_counts(wrong_counts, right_counts)
                self.print_total_counts(total_right_count, total_wrong_count)
                f.close()
                # return
            # else:
                # continue

        return total_right_count, total_wrong_count, wrong_counts, row2, ifsuccess

    def usaddress_parse_address_line(self, address_line="", wrong_counts={}):
        ifsuccess = False
        result = {}
        if address_line=="":
            wrong_counts['no_input'] += 1
            return ifsuccess, result, wrong_counts

        try:
            result = usaddress.parse(address_line)
            ifsuccess = True
            time.sleep(self.usaddress_sleep)
        except:
            print >> self.log_file, "ERROR: usaddress timeout"
            wrong_counts['timeout'] += 1
            return ifsuccess, result, wrong_counts

        if len(result) == 0:
            msg = " ".join(["ERROR: len(geocode_result) == 0", address_line, "\n"])
            print >> self.log_file, msg

        if self.isverbose:
            print >> self.log_file, "Parsed result:\n",result,"\n"

        return ifsuccess, result, wrong_counts


    def eval_usaddress(self, n=20000, g=0):
        """
        162 PENDEXTER AVE CHICOPEE MA 01013 2126
        216 E HILL RD BRIMFIELD MA 01010 9799


        >>> from uspsaddress import uspsaddress
        >>> usadd = uspsaddress()
        >>> usadd.eval_usaddress(1)
        ****1, 6.0, 0.0, 6.0, 0.0, 1.0
        wrong counts:
        {'city': 0, 'unit_num': 0, 'no_input': 0, 'street_post_dir': 0, 'zip': 0, 'street_name': 0, 'street_pre_dir': 0, 'street_suffix': 0, 'unit_type': 0, 'state_abbrev': 0, 'timeout': 0, 'street_num': 0, 'zip4': 0}

        """

        inputfile = "../../Data/samplefordatalinkage.csv"
        #inputfile =  "../../Data/test.csv"
        wrong_counts = self.initalize_counts_dict()
        right_counts = self.initalize_counts_dict()
        total_wrong_count = 0
        total_right_count = 0
        row_count = 0

        if self.isverbose:
            print >> self.log_file, "In eval_usaddress: n = ", str(n)
            if g>0: print >> self.log_file, "error rate = ", self.error_rate

        with open(inputfile, "rb") as f:
            reader = csv.DictReader(f);
            for row in reader:
                row_count += 1
                if row_count <= n:
                    if self.isverbose:
                        print >> self.log_file, \
                            "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", row_count
                else:
                    break

                total_right_count, total_wrong_count, wrong_counts, row2, ifsuccess = \
                    self.eval_usaddress_row(g, right_counts, row, row_count, total_right_count,
                               total_wrong_count, wrong_counts)

        print "\n\n=================================================US address n = %s, g = %s, error_rate = %s" % (n,g,self.error_rate)
        print >> self.log_file, "\n\n=================================================US address n = %s, g = %s, error_rate = %s" % (n,g,self.error_rate)
        self.print_counts(wrong_counts, right_counts)
        self.print_total_counts(total_right_count, total_wrong_count)

        f.close()
        self.log_file.close()

    def eval_usaddress_row(self, g, right_counts, row, row_count, total_right_count, total_wrong_count, wrong_counts):
        address_line, row1 = self.usps_csv_row2_dict_and_address_line(row)
        # introduce noise and errors
        old_address_line = address_line
        if g == 1:
            address_line = self.perturb_address_line(address_line)
        ifsuccess, result, wrong_counts = \
            self.usaddress_parse_address_line(address_line, wrong_counts)
        row2 = {}
        if ifsuccess:
            row2 = self.map_usaddress_result(result)

            right_count, wrong_count, wrong_counts = \
                self.compare2records(row1, row2, wrong_counts, right_counts)
            total_right_count, total_wrong_count = \
                self.update_counts(total_right_count, total_wrong_count,
                                   right_count, wrong_count, row_count)

            # if not ifsuccess:
            #     continue
        return total_right_count, total_wrong_count, wrong_counts, row2, ifsuccess


if __name__=='__main__':
    # python uspsaddress.py -v
    # Or:
    # python uspsaddress.py
    import doctest, uspsaddress_googlemaps
    doctest.testmod(uspsaddress_googlemaps)





