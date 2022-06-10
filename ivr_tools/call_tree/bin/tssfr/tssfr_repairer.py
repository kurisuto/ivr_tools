#!/usr/bin/env python3
#!/usr/bin/env python3
import re

class TSSFRRepairer:

    def __init__(self):
        pass

    
    def repair_call(self, call_record):
        lines = call_record.split("\n")
        new_lines = []

        if not re.search("EVNT=SWIclst", lines[0]):
            return None
        
        for line in lines:
            new_line = line
            
            new_line = re.sub("EVNT=modulend\|\|", "EVNT=modulend|", new_line)
            new_line = re.sub("EVNT=custom\|NO_STN_CODE_PROMPT:REF", "EVNT=custom|NO_STN_CODE_PROMPT=REF", new_line)
            new_lines.append(new_line)
            
        new_call_record = "\n".join(new_lines)

        return new_call_record
            
