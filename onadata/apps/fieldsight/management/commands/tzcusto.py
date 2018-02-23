import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from onadata.apps.fieldsight.models import TimeZone

class Command(BaseCommand):
	def handle(self, *args, **options):
		def slicer(timezone):
			tz = timezone
		    	try:
		    		index = tz.index('/')
		    		index+=1
		    		ntz=tz[index:]
				print "Fixed ..."
		    		return ntz
				
		    	except:
		    		return tz
		lists=TimeZone.objects.all()	
		for li in lists:
			tz = li.time_zone
			ntz=slicer(tz)
			nntz=slicer(ntz)
			li.time_zone=nntz
			li.save()
			print nntz
