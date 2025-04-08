import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

#function that will pull the current wave time from dust.wiki
def get_wave_time():
    #scope grants access to read/write spreadsheets and access Google Drive for sharing
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name('animated-scope-456121-q8-5b10debc616d.json', scope)
    gc = gspread.authorize(creds)

    #open Google Sheet (you can also use .worksheet("Tab Name"))
    #key is part of dust.wiki hyperlink...which is public
    spreadsheet=gc.open_by_key('17rGbgylW_IPQHaHUW1WsJAhuWI7y2WhplQR79g-obqg')

    #prints cell C3, giving the number of minutes until EoW
    #returns a nested list (e.g., [['14']]...so [['14']][0][0] yields '14'). I do not make the rules.
    return spreadsheet.worksheet('Dashboard').get('C3')[0][0]
