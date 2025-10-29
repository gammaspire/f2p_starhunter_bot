#####################################################
# Utility Functions for the /galaxy Discord Command #
#####################################################

import requests
from random import randint
import csv   #so I can read my sparkly galaxy table (keyword_lists/galaxy_table.csv)


def z_to_dist(z):
    H0 = 70 #km/s/Mpc
    c = 3e5 #km/s
    dist = c*z/H0 #Mpc
    dist *= 3.262e6 #light years!
    return dist

def dist_to_ducks(distance):
    conversion = 9.46e15 #number of meters per light year
    duck_height = 0.45 #meters
    m_to_ly = distance * conversion #number of meters spanning the input distance
    nducks = m_to_ly / duck_height #number of DUCKIES!
    return int(nducks)


def read_table():
    path = 'keyword_lists/galaxy_table.csv'
    with open(path, mode='r') as file:
        csv_reader = csv.reader(file)
        return list(csv_reader)


def get_legacy_url(ra, dec, imsize=256, pixscale=0.262):
    '''
    creates URL which returns the image of the sky at and with the specified parameters
    I will have to fiddle with the imsize parameter until I find one that is suitable for most/all galaxies
    I could use FITS header information, but that is too convoluted for a recreational pursuit
    '''
    url=f'http://legacysurvey.org/viewer/jpeg-cutout?ra={ra}&dec={dec}&layer=ls-dr9&size={imsize}&pixscale={pixscale}'
    
    #in principle, pasting this link into Discord will show the image rather than me needing to download it
    return url


#the 'default' scale, width, and height are quite possibly optimal but also quite possibly not. adjust as needed.
def get_sdss_url(ra, dec, scale=0.3, width=256, height=256):
    '''
    Return SDSS DR16 SkyServer cutout URL.
    '''
    url = f"https://skyserver.sdss.org/dr16/SkyServerWS/ImgCutout/getjpeg?ra={ra}&dec={dec}&scale={scale}&width={width}&height={height}"
    
    #in principle, pasting this link into Discord will show the image rather than me needing to download it
    return url


def get_random_placeholder():
    '''
    Return a cache-busted random image URL.
    "A cachebuster is a unique tag or value that is added to a URL to prevent a browser or proxy server from serving an 
     outdated, cached version of a file."
    '''
    cachebuster = randint(0, 999999)  #the randint is needed to force Discord to output a RANDOM image.
                                      #indeed...without it, copy+pasting the picsum link into Discord will 
                                      #output the same image. what a silly nilly.
    return f"https://picsum.photos/256/256.jpg?random={cachebuster}"
 
    
def get_galaxy_info(csv_catalog, index):
    '''
    Try Legacy Survey first, then SDSS, then Picsum.
    Returns message that Discord bot will send publicly to the user.
    '''
    
    #isolate the galaxy row from the csv catalog
    galaxy_row = csv_catalog[index]
    
    #grab the 'features'
    objname = galaxy_row[0]
    ra = float(galaxy_row[1])
    dec = float(galaxy_row[2])
    redshift = float(galaxy_row[3])
    constellation = galaxy_row[4]   #yay
    
    #convert redshift to distance...
    distance = z_to_dist(redshift)
    
    #convert distance to duckies
    nducks = dist_to_ducks(distance)
    
    #define the URLs for Legacy Survey and SDSS
    urls = [("Legacy Survey", get_legacy_url(ra, dec)), ("SDSS", get_sdss_url(ra, dec))]

    #first try to grab from the Legacy Survey; if the website is down, then grab instead from SDSS
    for source, url in urls:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200 and "image" in r.headers.get("Content-Type", "").lower():
                #print(f'The image URL is from the {source}.')
                return{"objname": objname,
                        "index": index,
                        "constellation": constellation,
                        "distance": distance,
                        "nducks": nducks,
                        "image_url": url,
                        "source": source,
                        "failed": False}
        
        except Exception as e:
            print(e)
            continue

    #if both fail (womp-womp), return the fallback placeholder.
    return {"objname": objname,
            "index": index,
            "constellation": constellation,
            "distance": distance,
            "nducks": nducks,
            "image_url": get_random_placeholder(),
            "source": "Lorem Picsum",
            "failed": True}