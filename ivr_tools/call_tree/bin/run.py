#!/usr/bin/env python3
import re

import sys
sys.path.append("/Users/kurisuto/Desktop/tech_scratch/ivrguy_TOOLS/20201226_new_effort")

from ivr_tools.call_fetcher.nuance_ndm_call_fetcher import NuanceNDMCallFetcher
from ivr_tools.call_parser.nuance_ndm_call_parser import NuanceNDMCallParser
from tssfr.tssfr_repairer import TSSFRRepairer

class TSSFRCallFetcher(NuanceNDMCallFetcher):
    TSSFR = re.compile("TSSFR")
    def _filter_call_identifier(self, call_identifier):
        if not re.search(self.TSSFR, call_identifier):
            return False
        return True



class TSSFRCallParser(NuanceNDMCallParser):

    def event_knwTrnN(self, event):
        pass
    def event_CALL_INFO(self, event):
        pass
    def event_CRN(self, event):
        pass
    def event_SESSION(self, event):
        pass
    def event_STATE(self, event):
        pass
    def event_dateColl(self, event):
        pass
    def event_earlyLat(self, event):
        pass
    def event_equipCd(self, event):
        pass
    def event_scenario(self, event):
        pass
    def event_skipQstn(self, event):
        pass
    def event_FARE(self, event):
        pass
    def event_PNR(self, event):
        pass
    def event_crdtCard(self, event):
        pass
    def event_defltDt(self, event):
        pass
    def event_old_TS(self, event):
        pass
    def event_roundTrp(self, event):
        pass
    def event_shortTrp(self, event):
        pass
    def event_slctItin(self, event):
        pass
    def event_srvDsrpt(self, event):
        pass
    def event_stnStffd(self, event):
        pass
    def event_want2pay(self, event):
        pass
    def event_custom(self, event):
        pass




    
    
client_dir = '/Users/kurisuto/Desktop/major_categories/data/from_others/logs/2020/amtrak/VRULogs'

# client_dir = '/Users/kurisuto/Desktop/major_categories/data/from_others/logs/2020/amtrak/VRULogs/20200401/TSSFR/2020/04April/01/13'



def main():
    fetcher = TSSFRCallFetcher(client_dir)
    repairer = TSSFRRepairer()

    for call_identifier, call_record in fetcher.get_next_call():
        try:
            # print(call_identifier)
            call_record = repairer.repair_call(call_record)

            if call_record is None:
                continue

            parser = TSSFRCallParser()
            call_history = parser.parse_call(call_record)


            call_history.dump()
            exit()

        except StopIteration:
            exit()
            
#        except Exception:
#            print(call_identifier)
        
    

if __name__ == "__main__":
    main()




    
    # id = '/Users/kurisuto/Desktop/major_categories/data/from_others/logs/2020/amtrak/VRULogs/20200402/AGR/2020/04April/02/22/APP-21-13-0a2c69a0_00000e5c_5e86c7c9_1de1_0031-LOG'
    # print(call_record)
    # exit()
    

        
        # print(call_identifier)
        
        # call = reader.log_to_call(log_text)
        # call.dump()
        # print("-" * 80)        
        # print(call)

#        lines = call_record.split("\n")
        
#        print(lines[0])

