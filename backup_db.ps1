$timestamp = Get-Date -Format "MM-dd-yyyy-HH-mm"
mongoexport --uri="mongodb://localhost:27017" /d house /c house_hist --out=db_backup/house_db_house_hist_$timestamp.json
mongoexport --uri="mongodb://localhost:27017" /d house /c new_house --out=db_backup/house_db_new_house_$timestamp.json
mongoexport --uri="mongodb://localhost:27017" /d house /c price_drop --out=db_backup/house_db_price_drop_$timestamp.json
mongoexport --uri="mongodb://localhost:27017" /d house /c deal --out=db_backup/house_db_deal_$timestamp.json
mongoexport --uri="mongodb://localhost:27017" /d house /c deal_cpking --out=db_backup/house_db_deal_$timestamp.json