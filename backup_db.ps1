$timestamp = Get-Date -Format "MM-dd-yyyy-HH-mm"
mongoexport --uri="mongodb://localhost:27017" /d house /c house_hist --out=db_backup/house_db_$timestamp.json