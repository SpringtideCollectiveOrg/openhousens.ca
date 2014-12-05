#****************************************************************
#
# Twitter autoupdates
#
# This requires the twitter API. Install it using pip:
# pip install twitter
#
#****************************************************************
import time
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Bill
from twitter import *

#
# Twitter tokens
#
token          = ""
token_key      = ""
con_secret     = ""
con_secret_key = ""

try:
    twitter = Twitter(auth=OAuth(token, token_key, con_secret, con_secret_key))
except () as e:
    print "FATAL ERROR!!!: Twitter can't be used. Exception: "+str(e)
    exit()

#
# Function to abbreviate bill titles so they will fit within the 140 character Twitter limit
#
def BillTitleAbbreviate(str,maxlen):
    strout = str.replace("An Act to ","[..]").replace("An Act ","[..]").replace("(amended)","").replace("\n"," ").replace("  "," ")
    if len(strout) > maxlen:
        strout = strout[:maxlen-3]+"..."
    return strout

#
# Listens for when bills are saved in the database.
#
@receiver(post_save,sender=Bill)
def TwitOnBillSaved(sender, instance, **kwards):
    
    #
    # Comment/uncomment stuff below to tweet out different updates
    #
    if instance.status=='RA':
        twitfmt = "Bill \"\" receives Royal Assent"
#    elif instance.status=='3rd':
#        twitfmt = "Bill \"\" now in third reading"
    elif instance.status=='WH':
        twitfmt = "Bill \"\" now in Whole House Committee"
    elif instance.status=='PL':
        twitfmt = "Bill \"\" now in Private/Local Bills Committee"
    elif instance.status=='LA':
        twitfmt = "Bill \"\" now in Law Amendments Committee"
#    elif instance.status=='2nd':
#        twitfmt = "Bill \"\" now in second reading"
#    elif instance.status=='1st':
#        twitfmt = "Bill \"\" is in first reading"
    else:
        print "Twitter interface dropping update tweet as it does not meet requirements"
        print "Bill was "+str(instance)+" and status was "+str(instance.status)
        return

    twitfmt = twitfmt.replace("\"\"","\""+BillTitleAbbreviate(instance.title,140-len(twitfmt))+"\"")
    print "TWEET SCHEDULING"
    print twitfmt
    print str(len(twitfmt))+"/140 characters in use"

    #
    # Send out the tweet here and delay execution for a few seconds.
    # There will probably be enough of a delay but we're just being safe
    #
    if twitter is not None:
        try:
            twitter.statuses.update(status=twitfmt)
        except:
            print "WARNING: unable to update status, got an error"

    time.sleep(20)

    return # end of function...

print "******* Twitter hook initialized *******"
