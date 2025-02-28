import json
from datetime import datetime

from pcraft.LibraryContext import *
from pcraft.TemplateBuilder import template_get_event

class PcraftLogWriter(LibraryContext):
    def __init__(self):
        super().__init__()

    def run(self, event, config, templates):
        frame_time = datetime.fromtimestamp(event["time"])
        event["variables"]["$eventID"] = self.gen_uuid(event, "$eventID")

        consistent_id = self.get_consistent_id(event["variables"]["$eventID"], 12)        
        event["variables"]["$recipientAccountId"] = consistent_id
        event["variables"]["$userIdentity_accountId"] = consistent_id
        event["variables"]["$userIdentity_arn"] = "arn:aws:iam::%s:root" % consistent_id
        event["variables"]["$userIdentity_principalId"] = consistent_id
        
        if "$portrange" in event["variables"]:
            portfrom, portto = event["variables"]["$portrange"].split("-")
            event["variables"]["$requestParameters_portRange"] = "{\"from\": %s, \"to\": %s}" % (portfrom, portto)
        else:
            event["variables"]["$requestParameters_portRange"] = "{}"

        logevent = template_get_event(templates, event["variables"]["$event_id"], event["variables"])
        logevent = frame_time.strftime(logevent)
        
        yield bytes(event, "utf8")
